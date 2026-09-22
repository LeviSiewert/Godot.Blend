from __future__ import annotations
from weakref import ref, ReferenceType as _RefType
from string import ascii_letters
from typing import Any, Iterable
from .signals import Signal
import random

from .context import StructContext

class _UNSET():
    pass 

_NULLREF = ref(_UNSET()) 

class Reference[ADDR:Any, V:Item]():
    cached_value : _RefType[V] = _NULLREF
    cached_addr : ADDR = None
    collection : Collection = None

    def __setup__(self,):
        pass

    def __init__(self, /, key_id:str=None, address:ADDR=None, cached_value:V=None, collection=None):
        self.__setup__()
        self.key_id = key_id
        self.store_address(address)
        self.store_value(cached_value)
        self.set_collection(collection)

    def store_value(self, v:V):
        if v is None: 
            self.cached_value = _NULLREF
        else:
            self.cached_value = ref(v)
    def store_address(self, addr:ADDR):
        self.cached_addr = addr

    def set_collection(self, collection):
        old_collection = self.collection
        
        if not (old_collection is None):
            self._search()
            old_collection._remove_reference(self)
            
        self.collection = collection

        if not (collection is None):
            collection._append_reference(self)
            self._search()

    def _search(self,):
        ''' search from stored values to check if local values exist '''
        if self.cached_addr:
            if res:=self.collection.get(self.cached_addr, self.key_id, default=None):
                self.store_value(res)
                # if isinstance(res,tuple):
                #     raise Exception(res)
                # if not (self.cached_value() is None):
                #     assert res is self.cached_value()
                # else:
                    # self.store_value(res)
        elif not (self.cached_value() is None):
            found = self.collection.get_key(self.cached_value(), self.key_id, default=None)
            if not (found is None):
                self.cached_addr = found.addr

    def is_valid(self,):
        if self.collection:
            if (self.cached_value() is None):
                return False
            return (self.collection.get(self.cached_addr, self.key_id) == self.cached_value()) 
        return False
    
    def get(self,)->V:
        #TODO: Search/double check against col if valid ref!
        return self.cached_value()

    def __eq__(self, value):
        if isinstance(value, Reference):
            return any((
                value.cached_addr == self.cached_addr,
                ((value.cached_value() == self.cached_value()) and self.cached_value()),
                ))
        return super().__eq__(value)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.cached_addr} :: {self.cached_value})"
            

class CollectionKey[ADDR:Any, I:Item]():
    collection : Collection|None = None
    key_id : str|None = None
    
    source : I
    addr : ADDR
    addr_updated : Signal[ADDR]

    def __init__(self, source:I, key_id:str, addr:ADDR,):
        self.addr_updated = Signal(self)
        self.key_id = key_id
        self.source = source
        self.addr = addr
        
    
    def set(self, addr):
        if self.collection:
            return self.collection.set(key=addr, value=self.source, key_id=self.key_id)
        self.addr = addr
        self.addr_updated(addr)

    def get(self):
        return self.addr
    
    def ensure(self,):
        if (self.addr is None) and (self.collection is None):
            raise RuntimeError("Cannot ensure an address without a namespace")
        elif (self.addr is None):
            self.set(self.collection.addr_generate(self.key_id))

    def __eq__(self, value):
        if isinstance(value, CollectionKey):
            return all((
                self.addr == value.addr,
                self.key_id == value.key_id,
                ))
        if isinstance(value, str):
            return self.add == value
        return super().__eq__(value)

    def __repr__(self)->str:
        return f"{self.__class__.__name__}({self.key_id} :: {self.addr})"

class Item():
    def __colkeys__(self,)->tuple[CollectionKey]:
        pass

class Collection[I:Item, ADDR:str|Any, V:Item]():
    data : list[I, dict[str,ADDR]]
    refs : list[Reference]

    context : StructContext

    unique_keys : tuple[str] = tuple()
    shared_keys : tuple[str] = tuple() #TODO: NOT IMPLIMENTED

    _unique_key_maintain_left : bool = True

    def __setup__(self,):
        self.data = []
        self.refs = []
        self.context = StructContext()

    def __init__(self, context=None):
        self.__setup__()
        self.context.set_extends(context)

    def append_reference(self, ref:Reference):
        ref.set_collection(self)
    def _append_reference(self, ref:Reference):
        self.refs.append(ref)
    
    def remove_reference(self, ref:Reference):
        ref.set_collection(None)
    def _remove_reference(self, ref:Reference):
        self.refs.remove(ref)

    def iter_invalid_references(self,):
        for r in self.refs:
            if not r.is_valid():
                yield r 

    def update_refs(self, key:Key, v:V):
        for r in self.refs:
            if key.key_id != r.key_id:
                continue
            if (r.cached_addr==key.addr) or (r.cached_value()==v):
                r.store_value(v)
                r.store_address(key.addr)

    def append(self, item:I, /, _defer_context_extension=False):
        keys = {} 
        if not (self.find(item, None) is None):
            raise ValueError("Already in collection!")
        
        for k in item.__colkeys__():
            keys[k.key_id] = k
            if k.key_id in self.unique_keys:
                self.ensure_unique(item,k)
                self.update_refs(k, item)
                ## TODO: Double call possible here!!
        self.data.append((item, keys))

        if not _defer_context_extension:
            if hasattr(item,"context"):
                item.context.set_extends(self.context)

    def extend(self,items:Iterable[I]):
        for item in items:
            self.append(item, _defer_context_extension=True)

        ## Defered context extension to prevent (NOT SOLVE!) timing problems
        ## If you are having troubles w/ timing, consider using a Reference
        ## Otherwise it's a TODO for a simpler Reference-like Promise via a Signal (in general)
        ## This A Promise would require ability to see caller, track and cleanup
        for item in items:
            if hasattr(item,"context"):
                item.context.set_extends(self.context)
        

    def find[D](self, item:I, /, default:D=_UNSET)->int|D:
        for i, (o, keys) in enumerate(self.data):
            if o is item:
                return i
        if default is _UNSET:
            raise KeyError(item)
        return default

    def remove(self,item:I):
        idx = self.find(item,None)
        if idx is None:
            raise KeyError(item)
        obj,keys = self.data.pop(idx)
        for k_id,k in keys.items():
            self.update_refs(k, item)
        if hasattr(item,"context"):
            item.context.set_extends(None)

    def iter_get(self, addr:ADDR, key_id:str=None, ret_key:bool=False):
        if key_id is None:
            key_id = self.key_matcher(addr)
        for i,ks in self.data:
            if k:=ks.get(key_id,None):
                if k.addr == addr:
                    if ret_key:
                        yield i, k
                    else:
                        yield i

    def unique_get[D](self, addr, key_id:str=None, /, ret_key:bool=False, default:D=_UNSET)->V|tuple[V,Key]|D:
        t = tuple(self.iter_get(addr=addr, key_id=key_id, ret_key=ret_key))
        if len(t) == 1:
            return t[0]
        elif len(t) > 1:
            raise LookupError("Unique get query returned multiple answers")
        if default is _UNSET:
            raise KeyError(key_id, addr, " in ", self.data)
        return default

    def get[D](self, addr:ADDR, key_id:str=None, /, default:D=_UNSET)->V|tuple[V]|D:
        if key_id is None:
            key_id = self.key_matcher(addr)
            
        if key_id in self.unique_keys:
            return self.unique_get(addr, key_id)
        elif key_id in self.shared_keys:
            return tuple(self.iter_get(addr, key_id))
        else:
            raise KeyError(key_id, addr) 
    
    def get_keys[D](self, obj:V, /, default:D=_UNSET)->dict[str,ADDR]|D:
        for o,r in self.data:
            if obj is o:
                return r
        if default is _UNSET:
            raise KeyError(obj)
        return default
    
    def get_key[D](self, obj:V, key_id:str,/, default:D=_UNSET)->Key|D :
        key : CollectionKey = self.get_keys(obj, default={}).get(key_id, None)
        if (key is None): 
            if (default is _UNSET):
               raise KeyError("Object was not initialized with key_id: ", key_id)
            return default
        return key

    def set(self, addr:ADDR, value:V, key_id:str=None):
        if key_id is None:
            key_id = self.key_matcher(addr)

        if key_id in self.unique_keys:
            _obj,_Key = self.unique_get(addr, key_id, (None,None), ret_key=True)
            if _obj is value: 
                return
            if (_Key != None):
                self.key_unique_collision_handle(_obj, _Key, value, addr)
                return

            key = self.get_key(value,key_id)
            key.addr = addr
            self.update_refs(key, value)

        else: 
            self.get_key(value,key_id).addr = addr
            # self.update_refs(key, value)

    def addr_generate(self, key_id):
        return f"{key_id}://{random.sample(ascii_letters, 9)}"

    def key_matcher(self, addr:Any):
        if not isinstance(addr,str):
            raise KeyError(addr)
        return addr.split("://")[0]
    
    def ensure_unique(self, obj, key:Key, obj_is_right=True):
        #TODO: Figure out best way to accomidate!
        pass

        # all_shared = list(filter(lambda x: not(x[0] is obj) , self.iter_get(key.addr, key.key_id, ret_key=True)))
        # all_shared.append((obj,key))

        # for _obj, _key in all_shared:
        #     self.key_unique_collision_handle(_obj, _key, obj, key)
        #     obj, key = _obj, _key
        # _obj,_key = self.unique_get(key.addr, key.key_id, default=(None,None), ret_key=True)
        # if (_obj is None) or (_obj is obj): 
        #     return

    def map_addresses(self,)->dict[str,tuple[I,Key]]:
        res = {}
        for o,ks in self.data:
            for k,v in ks.items():
                if not k in res.keys():
                    res[k] = []
                res[k].append(tuple((o,v)))
        return self

    def key_unique_collision_handle(self, left_obj:V, left_key:Key, right_obj:V, right_key:Key,):
        addrs = self.map_addresses()[left_key.key_id]
        addr = left_key.addr 
        i = 0
        while addr in addrs:
            addr = self.addr_generate() 
            i = i+1
            if i > 999:
                raise RuntimeError("KeyGenerator is not producing unique keys!")
        
        if self._unique_key_maintain_left:
            right_key.addr = addr
            self.update_refs(right_key,right_obj)

        else:
            left_key.addr = addr
            self.update_refs(left_key,left_obj)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, val):
        return self.set(key, val)
    
    def __iter__(self):
        for o,d in self.data:
            yield o

    def __len__(self):
        return len(self.data)
    
    def clear(self,):
        for o,d in self.data:
            self.remove(o)

    def __eq__(self, value):
        if not isinstance(value, Collection):
            return super().__eq__(value)
        return sorted((*self.values(),)) == sorted((*value.values(),)) 
    
    def values(self):
        for o,d in self.data:
            yield o