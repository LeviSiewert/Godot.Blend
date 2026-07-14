from __future__ import annotations

from weakref import ref, ReferenceType as WeakRef
from string import ascii_letters, digits
from typing import Any, Iterable

from .context import StructContext
from .signals import Signal

import random

class _UNSET:...

class CollectionKey[T:Any]():
    src : T
    col : Collection[T]|None = None
    key : str|None = None

    def set_key(self, key, update_sub_refs:bool=True, update_free_refs:bool=True):
        if self.col:
            self.col.set(self.src, key, update_sub_refs=update_sub_refs, update_free_refs=update_free_refs)
            return 
        self.key = key

    def __init__(self, src, /, key:str|None=None, col:Collection[T]|None=None):
        self.src = src
        self.col = col
        self.set_key(key)

class CollectionRef[T:Any]():
    ''' Weak reference based on collection & key.
    cached is stored on collection=None
    cached is checked on collection = ? to re-ascociate keys w/ correct option
    '''
    col : Collection[T]|None = None
    key : str|None = None
    _cached : WeakRef = ref(_UNSET())

    def __init__(self, key:str|None=None, col:Collection[T]|None=None, cache:T=None):
        self.set_key(key)
        self.set_cached(cache)
        self.set_col(col, rekey=True)

    def set_key(self, key, search=True):
        self.key = key
        if (not (self.col is None)) and search:
            self.set_cached(self.get())
    
    def set_cached(self, cache:T|None):
        if cache is None:
            self._cached = ref(_UNSET())
            return
        self._cached = ref(cache)

    def set_col(self, col, rekey=True):
        ''' if (rekey) or (self.key is None): if an _cached() exists and is in the collection, set local key to it
        If it doesnt exist and above criteria, clear key and attach to signals to search until (self.key is set) or (coll[key]) declared. 
        Otherwise, search new collection and set cached
        '''

        self.set_cached(self.get(default=self._cached())) 
        self.detach_collection() 

        self.col = col
        if col is None:
            return

        if ((rekey) or (self.key is None)) and not (self._cached()) is None:
            self.key = None
            key = self.col.find(self._cached(), None)
            if not (key is None): 
                self.set_key(key, search=False)

        assert (not (self.key is None) or not (self._cached() is None))
        ## Some logical disconnect here.
        self.attach_collection()

    def attach_collection(self):
        if self.col is None:
            return
        self.col.refs.append(self)
        self.col.kv_updated.connect(self._on_collection_kv_updated)

    def detach_collection(self):
        if self.col is None:
            return
        self.col.refs.remove(self)
        self.col.kv_updated.disconnect(self._on_collection_kv_updated)
        
    def get[D](self, default:D=None)->T|D:
        if self.key is None:
            return default
        if self.col is None:
            return default
        
        res = self.col.get(self.key, None)
         
        if res is None:
            return default

        return res
    
    def _on_collection_kv_updated(self, k:str, v:T|None, affect_free:bool, affect_sub:bool):
        ''' Goal is to update self to match k,v if criteria, state and affect by state is correct
        IE: be able to 
        - switch keys of objects in a collection w/out dragging references to new keys
        - attach an object with specific key w/out activating key on refs.
        '''
        if k is None: 
            return

        cache = self._cached()
        
        affects_me = (self.key == k) or ((cache is v) and not (cache is None))
        if not affects_me:
            return

        is_free = ((cache is None) and (self.key)) or ((cache) and (self.key is None))
        is_sub = not is_free

        if is_free and affect_free:
            self.key = k
            self._cached = ref(v)

        if is_sub and affect_sub:
            self.key = k
            self._cached = ref(v)

class Collection[T:Any]():
    ## TODO: switch functionality to dict && appended loose items list (better performance)

    context : StructContext
    data : list[T]
    refs : list[CollectionRef]
    
    key_attr : str = "key"

    kv_updated : Signal[str,T, bool, bool]

    def keys(self, yield_keyobj=False):
        if not yield_keyobj:
            for item in self.data:
                yield getattr(item, self.key_attr).key
        else:
            for item in self.data:
                yield getattr(item, self.key_attr)

    def items(self, yield_keyobj=False):
        if not yield_keyobj:
            for item in self.data:
                yield getattr(item, self.key_attr).key, item 
        else:
            for item in self.data:
                yield getattr(item, self.key_attr), item 

    def values(self):
        yield from self.data.__iter__() 

    def __setup__(self):
        self.context = StructContext()
        self.kv_updated = Signal(self,)
        self.data = []
        self.refs = []
        
    def __init__(self, key_attr:str, context:StructContext):
        self.__setup__()
        self.key_attr = key_attr
        self.context.set_extends(context)
    
    def find[D](self, item:T, default:D=None)->str|D:
        if item in self.data:
            return getattr(item, self.key_attr).key
        return None

    def append(self, item:T, update_free_refs:bool=True):
        data = dict(self.items())

        if item in data.values():
            raise ValueError("Already exists in collection!")
        
        key = getattr(item, self.key_attr, None)
        if (key is None) or not isinstance(key, CollectionKey):
            raise KeyError(item, self.key_attr)

        if (key.key is None):
            key.key = self.generate_key()

        key.col = self
        item.context.set_extends(self.context)
        self.data.append(item)
        
        if key.key in data.keys():
            self.handle_key_collision(key.key, data[key.key], item, update_free_refs)
            return
        self.kv_updated(key.key, item, update_free_refs, False)
    

    def extend(self, items:Iterable[T], update_free_refs:bool=True):
        for item in items:
            self.append(item, update_free_refs)

    def remove(self, item:T, update_sub_refs:bool=True):
        k = self.find(item, None)
        if k is None: 
            return
        self.data.remove(item)
        item.context.set_extends(None)
        key = getattr(item, self.key_attr) 
        key.col = None
        self.kv_updated(k, None, False, update_sub_refs)
    
    def get[D](self, key:str, default:D=_UNSET)->T|D:
        for k,i in self.items():
            if key == k:
                return i
        if default is _UNSET:
            raise KeyError(key)
        return default
    
    def set(self, item:T, key:str, update_sub_refs:bool=True,  update_free_refs:bool=True):
        data = dict(self.items())
        
        if item in data.values():
            l_item = data.get(key, None)

            if not (l_item is None):
                self.handle_key_collision(key, l_item, item, update_sub_refs, update_free_refs)
                return     
            
            getattr(item, self.key_attr).key = key
            self.kv_updated(key, item, update_free_refs, update_sub_refs)
            return

        self.data.append(item)
        # item.context.set_extends(self.context)
        # _key = getattr(item, self.key_attr) 
        # _key.col = self
        # _key.key = key
        # self.kv_updated(key, item, update_free_refs, update_sub_refs)

    def generate_key(self)->str:
        keys = tuple(self.keys())
        n_key = self._generate_key()
        while n_key in self.keys:
            n_key = self._generate_key()
        return n_key
    def _generate_key(self,)->str:
        return "".join(random.sample(9, ascii_letters))
    
    def index_key(self, key:str):
        keys = tuple(self.keys())
        n_key = key.rstrip(digits)
        i = 1
        while n_key in keys:
            n_key = f"{key}{i}"
            i = i+1
        return n_key

    _keep_left = True
    _random_key = True

    def handle_key_collision(self, key:str, l_item:T, r_item:T, update_sub_refs:bool=True, update_free_refs:bool=True):
        
        if self._random_key:
            n_key = self.generate_key()
        else: 
            n_key = self.index_key(key)
        
        if self._keep_left:
            getattr(r_item,self.key_attr).key = n_key
            self.kv_updated(n_key, r_item, update_free_refs, update_sub_refs)

        else: 
            getattr(l_item,self.key_attr).key = n_key
            self.kv_updated(n_key, l_item, update_free_refs, update_sub_refs)

    def __getitem__(self, key)->T:
        return self.get(key)
    
    def __len__(self):
        return len(self.data)