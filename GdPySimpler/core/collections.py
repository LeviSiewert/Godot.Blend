from __future__ import annotations
from weakref import ref, ReferenceType as _RefType
from string import ascii_letters
from typing import Any, Iterable
import random

from .context import StructContext

class _UNSET():
    pass 

_NULLREF = ref(_UNSET()) 

class Reference[ADDR:Any, V:Item]():
    cached_value : _RefType[V] = _NULLREF
    cached_addr : ADDR = None
    collection : Collection = None

    def __init__(self, /, key_id:str=None, address:ADDR=None, cached_value:V=None, collection=None):
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
        pass
    
class Key[ADDR:Any, I:Item]():
    collection : Collection|None = None
    key_id : str|None = None
    
    source : I
    addr : ADDR
    
    def __init__(self, source:I, addr:ADDR, key_id:str):
        self.key_id = key_id
        self.source = source
        self.addr = addr
        
    
    def set(self, addr):
        if self.collection:
            return self.collection.set(key=addr, value=self.source, key_id=self.key_id)
        self.addr = addr

    def get(self):
        return self.addr
    
    def ensure(self,):
        if (self.addr is None) and (self.collection is None):
            raise RuntimeError("Cannot ensure an address without a namespace")
        elif (self.addr is None):
            self.set(self.collection.addr_generate(self.key_id))

    def __repr__(self)->str:
        return f"CKey({self.key_id} :: {self.addr})"

class Item():
    def __colkeys__(self,)->tuple[Key]:
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

    def append(self, item:I):
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

        if hasattr(item,"context"):
            item.context.set_extends(self.context)

    def extend(self,items:Iterable[I]):
        for item in items:
            self.append(item)

    def find[D](self, item:I, /, default:D=_UNSET)->int|D:
        for i, (o, keys) in enumerate(self.data):
            if o is item:
                return i
        if default is _UNSET:
            raise KeyError(item)
        return default

    def remove(self,item:I):
        idx = self.find(self,item,None)
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
        key : Key = self.get_keys(obj, default={}).get(key_id, None)
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
    
    def ensure_unique(self, obj, key:Key):
        _obj,_key = self.unique_get( key.addr, key.key_id, default=(None,None))
        if (_obj is None) or (_obj is obj): 
            return
        self.key_unique_collision_handle(_obj, _key, obj, key)

    def map_addresses(self,)->dict[str,tuple[I,Key]]:
        res = {}
        for o,ks in self.data:
            for k,v in ks:
                if not k in res.keys():
                    res[k] = []
                res[k].append(tuple(o,v))
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


        

# class _UNSET():
#     pass

# class CollectionKey[KEY:str]():
#     ''' Instances of this class are found via _keys on Collection itself. 
#     Thus all objects that a collection houses must match the interface of _keys defined by the collection '''

#     key_id : str
#     source_obj : Any
#     local_data : KEY
#     collection : Collection = None

#     def __init__(self, source:Any, key_id:str, value:KEY):
#         self.source_obj = source
#         self.key_id = key_id
#         self.local_data = value

#     def set_collection(self, collection:Collection|None):
#         self.collection = collection

#     def get(self,):
#         if (self.collection is None):
#             return self.local_data
#         return self.collection.get(self)
    
#     def set(self, key:KEY):
#         if (self.collection is None):
#             self.local_data = key
#             return
#         return self.collection.set(self, key)

# class CollectionReferenceUnique[T]():
#     ''' Deferable reference to a collection utilizing either a cached value &| address 
#     is_valid is true be fetched when all: 
#         - Collection is set
#         - value_cached.get() or (address_cached in collection)
#     value_cached can an input to resolve to a collection address later, but cached_value must exist
#     '''

#     value_cached : ReferenceType[Any]|None = ref(_UNSET())
#     address_cached : Any|None = None
#     key_id : str = None

#     collection : Collection

#     def __setup__(self,):
#         pass

#     def __init__(self, /, key_id:str=None, address:Any=None, value:Any=None, collection:Collection=None):
#         self.key_id = key_id
#         self.set_address(address)
#         self.set_cached_value(value)
#         self.set_collection(collection)

#     def set_collection(self, collection:Collection):
#         if self.collection:
#             self.collection.remove_reference(self)

#         self.collection = collection

#         if collection:
#             collection.append_reference(self)

#     def is_valid(self,):
#         if self.collection:
#             val = self.collection.get(self.address_cached, None)
#             return self.value_cached() == val
#         return False

#     def set_address(self, address:Any):
#         self.address_cached = address

#     def set_cached_value(self, value:Any):
#         self.value_cached = ref(value)

#     def _on_collection_match_add(self, addr, value):
#         self.set_address(addr)
#         self.set_cached_value(value)
        
#     def _on_collection_match_rem(self, addr, old_value):
#         self.set_address(addr)
#         self.set_cached_value(old_value)

#     def _on_collection_match_update_addr(self, old_addr, new_addr):
#         self.address_cached = new_addr

#     def _on_collection_match_update_value(self, old_value, new_value):
#         self.value_cached = ref(new_value)


#     def get(self, ret_cached=True, default=_UNSET)->T:
#         if (self.collection is None) and ((not ret_cached) or (self.value_cached() is None)):
#             if (default is _UNSET):
#                 raise KeyError(self.address_cached)
#             return default
#         elif (self.collection is None):
#             return self.value_cached()
        
#         if self.value_cached() in self.collection:
#             return self.value_cached()
        
#         return self.collection.get(self.address_cached, key_id=self.key_id, default=default)


# class Collection[OBJECT:Any, KEY:str|Any, VALUE:str|Any]():
#     ''' KEY is required to be hashable 
#     all keys must exist on the originating item at integration as CollectionKey items
    
#     for inheritance into a specific role, consider overriding:
#     __init__
#         > Remove input_keys, res_methods
#     _extract_keycol
#         > Or _keyid_attr_map
#     _generate_key
#     _match_key
#     _resolve_key_collision
    
#     unique_keys
#     shared_keys
#     unique_resolution_method
#     keyid_attr_map
#     '''
    
#     context : StructContext
    
#     data : list[tuple[VALUE, dict[str, CollectionKey]]]
#     references : list[CollectionReferenceUnique]
    
#     unique_keys : tuple[str] = tuple()
#     shared_keys : tuple[str] = tuple()

#     unique_resolution_method : dict[str,str|Callable] 
#     keyid_attr_map : dict

#     value_appended : Signal
#     value_removed : Signal[Any]
#     value_key_set : Signal[str,Any,Any]

#     def __setup__(self):
#         self.value_appended = Signal(self)
#         self.data = []

#     def __init__(self, *args, context:StructContext, unique_keys:tuple[str]=None, shared_keys:tuple[str]=None, unique_resolution_method:dict[str,str]=None, keyid_attr_map:dict[str,str]=None):
#         self.__setup__()

#         if not  (unique_keys is None):
#             self.unique_keys = unique_keys
#         if not  (shared_keys is None):
#             self.shared_keys = shared_keys

#         if unique_resolution_method is None:
#             self.unique_resolution_method = {}
#         else:
#             self.unique_resolution_method = unique_resolution_method
        
#         if keyid_attr_map is None:
#             self.keyid_attr_map = {}
#         else:
#             self.keyid_attr_map = keyid_attr_map 
        
#         self.context = StructContext(extends=context)
#         self.extend(args)
        
#     def generate_key(self, key_id:str, item:OBJECT)->KEY:
#         if key_id in self.unique_keys:
#             mapping = {self._iter_keyid(key_id)}
#             keys = tuple(mapping.keys())
#             res = self._generate_key(self, key_id, item)
#             if res in keys:
#                 self._resolve_key_collision(key_id, res, mapping[res], item)
#             return
#         else:
#             return self._generate_key(self, key_id, item)
            
#     def _generate_key(self, key_id:str, item:OBJECT)->KEY:
#         return key_id + "://" + "".join(random.sample(ascii_letters, 9))
    
#     def _match_key(self, key:KEY)->str:
#         ''' if incoming key cannot be resolved, should raise error as __setobj__ requires this to be consistent'''
#         return key.split("://")[0]
#         # raise NotImplementedError()
    
#     def _resolve_key_collision(self, key_id:str, key, old_obj, new_obj):
#         existing = tuple({self._iter_keyid(key_id)}.keys())

#         method = self.unique_resolution_method.get(key_id, "INDEX")

#         if callable(method):
#             old_obj_key, new_obj_key = method(key_id, key, old_obj, new_obj, existing)
#             assert(old_obj_key != new_obj_key)
#             if old_obj_key != key:
#                 self.set_key(key_id, old_obj, old_obj_key)
#             if new_obj_key != key:
#                 self.set_key(key_id, new_obj, new_obj_key)
#             return

#         if method == "INDEX":
#             c = 0
#             k = key
#             while k in existing:
#                 c = c+1
#                 k = key+"."+str(c)
#                 if c > 100:
#                     raise RecursionError(method, k)
#             self.set_key(key_id, new_obj, k)

#         elif method == "REGENERATE":
#             c = 0
#             k = key
#             while k in existing:
#                 c = c+1
#                 k = self.generate_key(key_id, new_obj)
#                 if c > 100:
#                     raise RecursionError(method, k)
#             self.set_key(key_id, new_obj, k)

#     def _iter_keyid(self, key_id:str)->Generator[KEY, OBJECT]:
#         for t in self.data:
#             if res:=t[1].get(key_id, None):
#                 yield (t[0].local_data, res)

#     ## With a given item:

#     def set_key(self, key_id:str, item:OBJECT, key)->None:
#         collection_key = self.get_colkey(key_id, item)
#         collection_key.local_data = key
#     def get_key(self, key_id:str, item:OBJECT)->KEY:
#         collection_key = self.get_colkey(key_id, item)
#         return collection_key.local_data
    
#     def get_colkey(self, key_id:str, item:OBJECT, )->CollectionKey:
#         kd = self.get_keydict(item)
#         return kd.get(key_id)
#     def set_colkey(self, key_id:str, item:OBJECT, colkey:CollectionKey)->CollectionKey:
#         kd = self.get_keydict(item)
#         kd[key_id] = colkey

#     def get_keydict(self, item:OBJECT):
#         for i in self.data:
#             if i[0] is item:
#                 return i[1]
#         raise KeyError()
#     def set_keydict(self, item:OBJECT, new:dict[str,CollectionKey]):
#         for i in self.data:
#             if i[0] is item:
#                 i[1].clear()
#                 i[1].update(new)
#                 return
#         raise KeyError()

#     def append(self, item:OBJECT, _suspend_key_ids:tuple[str]=tuple(), _defer_context=False):
#         ''' Suspend keys is meant for internal use only'''
#         key_map = {}

#         for k in self.unique_keys:
#             attr = self.keyid_attr_map.get(k,k)
#             if k in _suspend_key_ids:
#                 continue
#             colkey = getattr(item,attr)
#             assert(isinstance(colkey, CollectionKey))
#             self._ensure_unique(k, colkey, item)
#             key_map[k] = colkey

#         for k in self.shared_keys:
#             attr = self.keyid_attr_map.get(k,k)
#             if k in _suspend_key_ids:
#                 continue
#             colkey = getattr(item,attr)
#             assert(isinstance(colkey, CollectionKey))
#             key_map[k] = colkey

#         self.data.append((item, key_map))
#         if not _defer_context:
#             item.context.set_extends(self.context)
    
#     def extend(self, items):
#         for item in items:
#             self.append(item, _defer_context=True)
#         for item in items:
#             item.context.set_extends(self.context)
        
#     def _ensure_unique(self, key_id, colkey, new_obj):
#         for k,o in self._iter_keyid(key_id):
#             if k == colkey.local_data:
#                 self._resolve_key_collision(key_id, k, o, new_obj)

#     def remove(self, item:OBJECT, missing_ok:bool = True):
#         if not (res:=self.find(item, None) is None):
#             self.data.remove(res)
#             return
#         if not missing_ok:
#             raise KeyError(item)
        
#     def find(self, item:OBJECT, default=_UNSET)->int:
#         for i,o in enumerate(self.data):
#             if o is item:
#                 return i
#         if default is _UNSET:
#             raise KeyError(item)
#         return default

#     def get[D](self, key:KEY, key_id:str=None, /, default:D=_UNSET)->OBJECT|D|tuple[OBJECT|D]:
#         if key_id is None:
#             key_id = self._match_key(key)
#         if key_id in self.unique_keys:
#             for k,v in self._iter_keyid(key_id):
#                 if k == key:
#                     return v
#             if default is _UNSET:
#                 raise KeyError(key)
#             return default

#         else:
#             res = []
#             for k,v in self._iter_keyid(key_id):
#                 if k == key:
#                     res.append(v)
#             return res
        
#     def set(self, key:KEY, value:OBJECT, key_id:str=None, ensure_exists=True, resolve_unique_collision=True):
#         if key_id is None:
#             key_id = self._match_key(key)
        
#         if (index:=self.find(value,None) is None) and ensure_exists:
#             self.append(value, _suspend_key_ids=(key_id,))
#         elif (index is None):
#             raise ValueError("Must exist to be set or use ensure_exists!")

#         if (key_id in self.unique_keys) and resolve_unique_collision:
#             self._ensure_unique(key_id, self.get_colkey(key_id, value), value)
#             return
#         elif key_id in self.unique_keys:
#             for k,o in self._iter_keyid(key_id):
#                 if k == key:
#                     raise KeyError("must be unique!", k)
#         self.get_colkey(key_id, value).local_data = key

#     def __getitem__(self, key:KEY):
#         return self.get(key)
        
#     def __setitem__(self, key:KEY, value:OBJECT):
#         return self.set(key, value)

#     def __iter__(self,):
#         for (o,d) in self.data:
#             yield o

#     def __eq__(self, item):
#         if isinstance(item, Collection):
#             return hash(item) == hash(self)
#         return False
    
#     def __hash__(self):
#         hash_sum : int = 0
#         for o in self:
#             hash_sum = hash_sum + hash(o)
#         return hash_sum
    
#     def append_reference(self, ref:CollectionReferenceUnique):
#         self.references.append(ref)

#     def remove_reference(self, ref:CollectionReferenceUnique):
#         self.references.remove(ref)