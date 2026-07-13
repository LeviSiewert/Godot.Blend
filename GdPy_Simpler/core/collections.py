from __future__ import annotations

from weakref import ref, ReferenceType as WeakRef
from string import ascii_letters
from typing import Any, Iterable

from .context import StructContext
from .signals import Signal

import random

class _UNSET:...

class CollectionKey[T:Any]():
    src : T
    col : Collection[T]|None = None
    key : str|None = None

    def set_key(self, key):
        if self.col:
            return self.col.set(self.src, key)
        self.key = key

class CollectionRef[T:Any]():
    ''' Weak reference based on collection & key.
    cached is stored on collection=None
    cached is checked on collection = ? to re-ascociate keys w/ correct option
    '''
    col : Collection[T]|None = None
    key : str|None = None
    _cached : WeakRef = ref(_UNSET())

    # is_free_ref : 
    #   col[key] == None. 
    #   _cached has no match 
    
    # is_sub_ref : 
    #   matching key->val in collection. 
    #   _cached is val

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

        self.set_cached(self.get(self, default=self._cached())) 
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

    def detach_collection(self):
        if self.col is None:
            return
        self.col.refs.remove(self)
        
    def get[D](self, default:D=None)->T|D:
        if self.key is None:
            return default
        if self.col is None:
            return default
        
        res = self.col.get(self.key, None)
         
        if res is None:
            return default

        return res
    

class Collection[T:Any]():
    ## TODO: switch functionality to dict && appended loose items list (better performance)

    context : StructContext
    data : list[T]
    refs : list[CollectionRef]
    
    key_attr : str = "key"

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
        self.data = {}
        
    def __init__(self, key_attr:str, context:StructContext):
        self.__setup__()
        self.key_attr = key_attr
        self.context.set_extends(context)
    
    def append(self, item:T, update_free_refs:bool=True):
        data = dict(self.items())

        if item in data.values():
            raise ValueError("Already exists in collection!")
        
        key = getattr(item, self.key_attr, None)
        if (key is None) or not isinstance(key, CollectionKey):
            raise KeyError(item, self.key_attr)

        if (key.key is None):
            key.key = self.generate_key()

        if key.key in data.keys():
            self.handle_key_collision(key.key, data[key.key], item)
        
        item.context.set_extends(self.context)
        self.data.append(item)
            
    def remove(self, item:T, update_sub_refs:bool=True):
        self.data.remove(item)
        item.context.set_extends(None)

    def generate_key(self,)->str:
        raise NotImplementedError()

    def handle_key_collision(self, key:str, l_item:T, r_item:T, update_sub_refs:bool=True, update_free_refs:bool=True):
        raise NotImplementedError()
    
    def get[D](self, key:str, default:D=_UNSET)->T|D:
        for k,i in self.data():
            if key == k:
                return i
        if default is _UNSET:
            raise KeyError(key)
        return default
    
    def set(self, item:T, key:str, update_sub_refs:bool=True,  update_free_refs:bool=True):
        data = dict(self.data.items())
        
        if item in data.values():
            l_item = data.get(key, None)

            if not (l_item is None):
                self.handle_key_collision(key, l_item, item)
            else:
                getattr(item, self.key_attr).key = key

            return
    
    # def set(self, key:str, item:T):
    #     data = dict(self.data.items())
    #     l_item = data.get(key, None)
    #     if l_item is item:
    #         return
    #     if not (l_item is None):
    #         self.handle_key_collision(key, l_item, item)
    #         return
        

# class CollectionKey():
#     collection : Collection
    
#     src : Any
#     key : str|_UNSET
#     key_updated : Signal[str]

#     def __setup__(self,):
#         self.key_updated = Signal()

#     def __init__(self, src, key:str=_UNSET):
#         pass

#     def set(self, key):
#         if self.collection:
#             return self.collection.set(key=key, value=self.source)
#         self.key = key
#         self.key_updated(key)

#     def get(self):
#         return self.key
    
#     def __eq__(self, value:Any):
#         if isinstance(value,str):
#             return value == self.key
        
#         if isinstance(value, CollectionKey):
#             return all((
#                 self.key == value.key
#             ))

#         return super().__eq__(value)
    
#     def __repr__(self):
#         return f"{self.__class__.__name__}({self.key})"

# class CollectionRef[T:Any]():
#     ''' Weak Caching Reference, context is used to find the collection. '''

#     collection : Collection
#     context : StructContext
    
#     cached_key : str = None
#     cached_object : _RefType[Any] = None

#     def __setup__(self,):
#         self.context = StructContext()
#         self.context.callback('...', lambda x: self.set_collection(x))
#         ## Override calback with scope & collection reference

#     def __init__(self, key:str|None=None, obj:T|None=None, context:StructContext|None=None):
#         self.__setup__()
#         self.store_key(key)
#         self.store_obj(obj)
#         self.context.set_extends(context)


#     def get[D](self, default:D=_UNSET)->T|D:
#         ...

#     def search(self):
#         ...


#     def set_collection(self, col:Collection[T]|None):
#         ...


#     def store_key(self, key:str|None):
#         ...

#     def store_obj(self, obj:T|None):
#         ...


#     def is_valid(self,)->bool:
#         ...


# class Collection[T:Any]():
#     ''' A collection of objects that are self-keyed, and through context can be soft-referenced by a CollectionRef 
#     Self keying done through a CollectionRef.
#     argued key_attr is what is used to request the CollectionKey from the object
#     '''

#     context : StructContext
#     data : list[T]
#     refs : list[CollectionRef]

#     def __setup__(self,):
#         self.context = StructContext()

#     def __init__(self, key_attr:str, context:StructContext):
#         self.__setup__()
#         self.context.set_extends(context)
#         self.key_attr = key_attr


#     def append(self, val:T):
#         ...

#     def remove(self, val:T):
#         ...

#     def duplicate(self, val:T)->T:
#         ...

#     def resolve_key_collision(self, k, l:T, r:T):
#         ...

#     def append_reference(self, ref:CollectionRef):
#         ref.set_collection(self)
#     def _append_reference(self, ref:CollectionRef):
#         ...


#     def remove_reference(self, ref:CollectionRef):
#         ref.set_collection(None)
#     def _remove_reference(self, ref:CollectionRef):
#         ...

