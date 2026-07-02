from __future__ import annotations
from typing import Any, Generator, Callable
from types import LambdaType, FunctionType
from string import ascii_letters
import random 
# class Signal():
#     pass

class _UNSET():
    pass

class CollectionKey[KEY:str]():
    key_id : str
    source_obj : Any
    local_data : KEY
    collection : Collection = None

    def __init__(self, source:Any, key_id:str, value:KEY):
        self.source_obj = source
        self.key_id = key_id
        self.local_data = value

    def set_collection(self, collection:Collection|None):
        self.collection = collection

    def get(self,):
        if (self.collection is None):
            return self.local_data
        return self.collection.get(self)
    
    def set(self, key:KEY):
        if (self.collection is None):
            self.local_data = key
            return
        return self.collection.set(self, key)
    
class Collection[OBJECT:Any, KEY:str|Any, VALUE:str|Any]():
    ''' KEY is required to be hashable 
    all keys must exist on the originating object at integration as CollectionKey objects
    
    for inheritance into a specific role, consider overriding:
    __init__
        > Remove input_keys, res_methods
    _extract_keycol
        > Or _keyid_attr_map
    _generate_key
    _match_key
    _resolve_key_collision
    
    unique_keys
    shared_keys
    unique_resolution_method
    keyid_attr_map
    '''
    
    data : list[tuple[VALUE, dict[str, CollectionKey]]]
    
    unique_keys : tuple[str] = tuple()
    shared_keys : tuple[str] = tuple()

    unique_resolution_method : dict[str,str|Callable] 
    keyid_attr_map : dict

    def __init__(self, unique_keys:tuple[str]=None, shared_keys:tuple[str]=None, unique_resolution_method:dict[str,str]=None, keyid_attr_map:dict[str,str]=None):
        if unique_keys is None:
            self.unique_keys = unique_keys
        if shared_keys is None:
            self.shared_keys = shared_keys

        if unique_resolution_method is None:
            self.unique_resolution_method = {}
        else:
            self.unique_resolution_method = unique_resolution_method
        
        if keyid_attr_map is None:
            inst = {}
            for k in (*unique_keys, *shared_keys):
                inst[k] = k
            self.keyid_attr_map = inst

        
    def generate_key(self, key_id:str, object:OBJECT)->KEY:
        if key_id in self.unique_keys:
            mapping = {self._iter_keyid(key_id)}
            keys = tuple(mapping.keys())
            res = self._generate_key(self, key_id, object)
            if res in keys:
                self._resolve_key_collision(key_id, res, mapping[res], object)
            return
        else:
            return self._generate_key(self, key_id, object)
            
    def _generate_key(self, key_id:str, object:OBJECT)->KEY:
        return key_id + "://" + "".join(random.sample(ascii_letters, 9))
    
    def _match_key(self, key:KEY)->str:
        ''' if incoming key cannot be resolved, should raise error as __setobj__ requires this to be consistent'''
        return key.split("://")[0]
        # raise NotImplementedError()
    
    def _resolve_key_collision(self, key_id:str, key, old_obj, new_obj):
        existing = tuple({self._iter_keyid(key_id)}.keys())

        method = self.unique_resolution_method.get(key_id, "INDEX")

        if callable(method):
            old_obj_key, new_obj_key = method(key_id, key, old_obj, new_obj, existing)
            assert(old_obj_key != new_obj_key)
            if old_obj_key != key:
                self.set_key(key_id, old_obj, old_obj_key)
            if new_obj_key != key:
                self.set_key(key_id, new_obj, new_obj_key)
            return

        if method == "INDEX":
            c = 0
            k = key
            while k in existing:
                c = c+1
                k = key+"."+str(c)
                if c > 100:
                    raise RecursionError(method, k)
            self.set_key(key_id, new_obj, k)

        elif method == "REGENERATE":
            c = 0
            k = key
            while k in existing:
                c = c+1
                k = self.generate_key(key_id, new_obj)
                if c > 100:
                    raise RecursionError(method, k)
            self.set_key(key_id, new_obj, k)

    def _iter_keyid(self, key_id:str)->Generator[KEY, OBJECT]:
        for t in self.data:
            if res:=t[1].get(key_id, None):
                yield (t[0].local_data, res)

    ## With a given object:

    def set_key(self, key_id:str, object:OBJECT, key)->None:
        collection_key = self.get_colkey(key_id, object)
        collection_key.local_data = key
    def get_key(self, key_id:str, object:OBJECT)->KEY:
        collection_key = self.get_colkey(key_id, object)
        return collection_key.local_data
    
    def get_colkey(self, key_id:str, object:OBJECT, )->CollectionKey:
        kd = self.get_keydict(object)
        return kd.get(key_id)
    def set_colkey(self, key_id:str, object:OBJECT, colkey:CollectionKey)->CollectionKey:
        kd = self.get_keydict(object)
        kd[key_id] = colkey

    def get_keydict(self, object:OBJECT):
        for i in self.data:
            if i[0] is object:
                return i[1]
        raise KeyError()
    def set_keydict(self, object:OBJECT, new:dict[str,CollectionKey]):
        for i in self.data:
            if i[0] is object:
                i[1].clear()
                i[1].update(new)
                return
        raise KeyError()

    def append(self, object:OBJECT, _suspend_key_ids:tuple[str]=tuple()):
        ''' Suspend keys is meant for internal use only'''
        key_map = {}

        for k,attr in self.unique_keys:
            if k in _suspend_key_ids:
                continue
            colkey = getattr(object,attr)
            assert(isinstance(colkey, CollectionKey))
            self._ensure_unique(k, colkey, object)
            key_map[k] = colkey

        for k,attr in self.shared_keys:
            if k in _suspend_key_ids:
                continue
            colkey = getattr(object,attr)
            assert(isinstance(colkey, CollectionKey))
            key_map[k] = colkey

        self.data.append((object, key_map))
    
    def _ensure_unique(self, key_id, colkey, new_obj):
        for k,o in self._iter_keyid(key_id):
            if k == colkey.local_data:
                self._resolve_key_collision(key_id, k, o, new_obj)

    def remove(self, object:OBJECT, missing_ok:bool = True):
        if not (res:=self.find(object, None) is None):
            self.data.remove(res)
            return
        if not missing_ok:
            raise KeyError(object)
        
    def find(self, object:OBJECT, default=_UNSET)->int:
        for i,o in enumerate(self.data):
            if o is object:
                return i
        if default is _UNSET:
            raise KeyError(object)
        return default

    def get[D](self, key:KEY, key_id:str=None, /, default:D=_UNSET)->OBJECT|D|tuple[OBJECT|D]:
        if key_id is None:
            key_id = self._match_key(key)
        if key_id in self.unique_keys:
            for k,v in self._iter_keyid(key_id):
                if k == key:
                    return v
            if default is _UNSET:
                raise KeyError(key)
            return default

        else:
            res = []
            for k,v in self._iter_keyid(key_id):
                if k == key:
                    res.append(v)
            return res
        
    def set(self, key:KEY, value:OBJECT, key_id:str=None, ensure_exists=True, resolve_unique_collision=True):
        if key_id is None:
            key_id = self._match_key(key)
        
        if (index:=self.find(value,None) is None) and ensure_exists:
            self.append(value, _suspend_key_ids=(key_id,))
        elif (index is None):
            raise ValueError("Must exist to be set or use ensure_exists!")

        if (key_id in self.unique_keys) and resolve_unique_collision:
            self._ensure_unique(key_id, self.get_colkey(key_id, value), value)
            return
        elif key_id in self.unique_keys:
            for k,o in self._iter_keyid(key_id):
                if k == key:
                    raise KeyError("must be unique!", k)
        self.get_colkey(key_id, value).local_data = key

    def __getitem__(self, key:KEY):
        return self.get(key)
        
    def __setitem__(self, key:KEY, value:OBJECT):
        return self.set(key, value)