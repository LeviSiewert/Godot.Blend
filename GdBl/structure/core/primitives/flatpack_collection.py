from __future__ import annotations
import bpy
import random
import string
from typing import Any, Iterable
from abc import ABC, abstractmethod
class _NULL():pass

## TODO: This implimentation could be better setup using signals for pointer updates, however that's alright for now

class FlatPackItemInterface(ABC):

    @abstractmethod
    def get_pointer_references()->tuple[str]:
        return tuple()

    def pointer_reference_update(self, fr_pointer:str, old_val:Any|None, to_pointer:str, add_val:Any)->dict[FlatPackItemInterface,str]:
        ''' reported pointer via reference tree in flat pack has been updated, update references (fr => to) '''
        raise NotImplementedError()   

    def pointer_reference_remove(self, pointer:str)->dict[FlatPackItemInterface,str]:
        ''' reported pointer via reference tree has been removed from the root collection, remove references to pointer & handle side effects '''
        raise NotImplementedError()   

    def get_flatpackitem_children(self)->tuple[FlatPackItemInterface]:
        return tuple()

    def pointer_reference_tree(self,)->dict[FlatPackItemInterface,tuple[str]]:
        ''' return all pointers used within the current instance & children that are not referenced '''
        child_refs = {k:k.pointer_reference_tree() for k in self.get_flatpackitem_children() }
        if l_refs := self.get_pointer_references():
            return {self:l_refs} | child_refs
        return self.get_flatpackitem_children_refs()
    

class FlatPackPointer(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty() #type:ignore

    pointer_id : bpy.props.StringProperty() #type:ignore

    def get_pointer_data(self, col:FlatPackCollection):
        return col.get_pointer_value(self.pointer_id)

    def get_pointer_references(self,):
        return (self.pointer_id,)

    def pointer_reference_update(self, fr_pointer:str, old_val:Any|None, to_pointer:str, add_val:Any)->dict[FlatPackItemInterface,str]:
        if self.pointer_id == fr_pointer:
            self.pointer_id = to_pointer

    def pointer_reference_remove(self, pointer:str)->dict[FlatPackItemInterface,str]:
        if self.pointer_id == pointer:
            self.pointer_id = ""
        return

class FlatPackCollection(bpy.types.PropertyGroup):
    ''' Utility class for multiple sub-collections of different types in a uniform namespace & pointers
    Use case is for limited implimentation of arrays|dicts with variable type children
    data & pointed data CAN be in the same collections, due to required pointed value prefix (default="*")
    .add() and .add_pointer() requires key that is asc with _map_pointer_collections, and _map_data_collections
    '''
    # items : bpy.props.CollectionProperty(type = FlatPackPointer) #type:ignore
    _pointer_prefix : str = "*"

    def _map_pointer_collections(self,)->dict[str,bpy.types.Collection|bpy.types.PropertyGroup]:
        raise NotImplementedError("Implement in child class")
    def _map_data_collections(self,)->dict[str,bpy.types.Collection|bpy.types.PropertyGroup]:
        raise NotImplementedError("Implement in child class")

    def _get_pointer_collections(self,)->Iterable[bpy.types.Collection|bpy.types.PropertyGroup]:
        return self._map_pointer_collections().values()
    def _get_data_collections(self,)->Iterable[bpy.types.Collection|bpy.types.PropertyGroup]:
        return self._map_data_collections().values()

    def _map_all_pointers(self,)->dict[str:Any]:
        res = {}
        for c in self._get_pointer_collections():
            for k,v in c.items():
                if k.startswith(self._pointer_prefix):
                    res[k] = v
        return res
    def _get_all_pointers(self,)->tuple[str]:
        return self._map_all_pointers().keys()

    def _map_all_data(self,)->dict[str:Any]:
        res = {}
        for c in self._get_data_collections():
            for k,v in c.items():
                res[k] = v
        return res
    def _get_all_data(self,)->tuple[str]:
        return self._map_all_data().keys()

    def generate_pointer_id(self, typeid:str|None=None,)->str:
        r = self._pointer_prefix+"".join(random.sample(string.ascii_letters,9))
        all_ptr = self._get_all_pointers()
        while r in all_ptr:
            r = self._pointer_prefix+"".join(random.sample(string.ascii_letters,9))
        return r

    def add_pointer_value(self, typeid:str, *args, **kwargs)->tuple[str,object]:
        key = self.generate_pointer_id(typeid)
        col = self._map_pointer_collections()[typeid]
        obj = col.add(*args,**kwargs)
        obj.name = key
        return (key,obj)
    
    def get_pointer_value(self, pointer:str):
        return self._map_all_pointers()[pointer]

    def add_data(self, typeid:str, key:str, *args, **kwargs)->object:
        _all_keys = (*self._map_all_data().keys(), *self._map_all_pointers().keys())
        if key in _all_keys:
            raise KeyError("key already exists:", key)
        col = self._map_data_collections()[typeid]
        obj = col.add(*args, **kwargs)
        obj.name = key
        return obj
    
    def get_data(self,key):
        return self._map_all_data()[key]
    
    def is_pointer(self,key)->bool:
        return key.startswith(self._pointer_prefix)

    def get(self, key:str, default=_NULL):
        if self.is_pointer(key):
            return self.get_pointer_value(key)
        return self.get_data(key, default=default)

    def remove(self, key):
        for c in (*self._get_pointer_collections, *self._get_data_collections):
            res = c.get(key,None)
            if res is None: 
                continue
            if self.is_pointer(res):
                self.remove_pointer_refs(key)    
            del c[key]
            return 
        raise KeyError(key)
    
    def swap_pointer_refs(self, fr:str, to:str):
        ''' both must be existing pointed objects'''
        assert(self.is_pointer(fr)) 
        assert(self.is_pointer(to))

        old_val = self.get_pointer_value(fr,default=None)
        add_val = self.get_pointer_value(to)

        for item in self.get_references().get(fr,tuple()):
            item:FlatPackItemInterface
            item.pointer_reference_update(fr,old_val, to,add_val)
            
    def remove_pointer_refs(self, key):
        assert(self.is_pointer(key))
        old_val = self.get_pointer_value(key,default=None)
        for item in self.get_references().get(key,tuple()):
            item:FlatPackItemInterface
            item.pointer_reference_remove(key, old_val)

    def get_references(self,)->dict[str:list[FlatPackItemInterface]]:
        ''' Return all pointer references via requesting reference tree stuff '''
        res = []
        for c in (*self._get_data_collections(), self._get_pointer_collections()):
            if not hasattr(c,"pointer_reference_tree"): 
                continue
            for v,ks in c.pointer_reference_tree():
                for k in ks:
                    if not k in res.keys():
                        res[k] = []
                    res[k].append(v)
        return res

    def __getitem__(self, key):
        if self.is_pointer(key):
            return self.get_pointer_value(key)
        return self.get_data(key)

    def __delitem__(self, key):
        self.remove(key)
    


    
# class FlatPackCollection(bpy.types.PropertyGroup):
#     ''' Utility class for multiple sub-collections in a uniform/unique namespace & pointers '''

#     items : bpy.props.CollectionProperty(type = FlatPackItem) #type:ignore
#     _pointer_prefix : str = "*"

#     def get_subflatpacks(self,)->tuple[FlatPackCollection]:
#         return tuple()
        
#     def get_pointer_colls(self,)->tuple[bpy.types.CollectionProperty]:
#         return (self.items,)
#     def get_data_colls(self,)->tuple[bpy.types.CollectionProperty]:
#         return (self.items,)

#     def yield_pointers(self, local_only=False)->Iterable[tuple[FlatPackCollection, str, bpy.types.PropertyGroup]]:
#         for col in self.get_pointer_colls():
#             for k,v in col.items():
#                 if k.startswith(self._pointer_prefix):
#                     yield (self,k,v)
#         if local_only: 
#             return
#         for flatpack in self.get_subflatpacks:
#             yield from flatpack.yield_all_pointers()

#     def yield_datas(self, local_only=False)->Iterable[tuple[FlatPackCollection, str, bpy.types.PropertyGroup]]:
#         for col in self.get_data_colls():
#             for k,v in col.items():
#                 yield (self,k,v)
#         if local_only: 
#             return
#         for flatpack in self.get_subflatpacks:
#             yield from flatpack.yield_all_pointers()
    
#     def pointers_dict(self, local_only=True)->dict[str, bpy.types.PropertyGroup]:
#         res = {}
#         for c,k,v in self.yield_pointers(local_only):
#             assert(not (k in res.keys()))
#             res[k] = v
#         return res
    
#     def get_pointer(self, pointer:str, /, default=_NULL, local_only=False)->bpy.types.PropertyGroup|Any:
#         for c,k,v in self.yield_pointers(local_only):
#             if (k == pointer):
#                 return v
#         if default is _NULL:
#             raise KeyError(pointer)
#         return default

#     def is_valid_pointer(self, pointer:str, local_only=False):
#         if pointer.startswith(self._pointer_prefix):
#             return True
#         if local_only:
#             return False
#         for fp in self.get_subflatpacks():
#             if not pointer.startswith(fp._pointer_prefix):
#                 continue
#             if res := fp.is_valid_pointer(pointer):
#                 return True
#         return False
    
#     def does_pointer_exist(self, pointer:str, local_only=False):
#         for c,k,v in self.yield_pointers(local_only):
#             if (k==pointer):
#                 return True
#         return False
    
#     def get(self, key, default=_NULL, local_only=False):
#         for c in self.get_data_colls:
#             if res := c.get(key, None):
#                 return res

#         if local_only:
#             if default is _NULL:
#                 raise KeyError(key)
#             return default

#         for sfp in self.get_subflatpacks:
#             if res:=sfp.get(key, None, local_only):
#                 return res

#         if default is _NULL:
#             raise KeyError(key)
#         return default

#     def __getitem__(self, key_or_pointer):
#         ''' Search recursivly, match pointer, then fallback to data ''' 
#         if self.is_valid_pointer(key_or_pointer):
#             return self.get_pointer(key_or_pointer, local_only=False)
#         return self.get(key_or_pointer)
    
#     def __delitem__(self, key):
#         for c,k,v in self.yield_datas(local_only=True):
#             if (k == key):
#                 c.remove(key)
#                 return

#     def add(self, colid:str, key:str, **kwargs):
#         ## key must be unique in "global" space
#         ## Colid must be maped from {ID:Col}
#         ## **kwargs is forwarding the data to a specific loc.
#         pass





# class FlatPackContext():
#     ''' Utility class for recursive flatpack collection queires '''
#     collection_chain : 


# class FlatPackItem(bpy.types.PropertyGroup):
#     name : bpy.props.StringProperty() #type:ignore
    
#     ## Other values allowable.

#     is_pointer : bpy.props.BoolProperty(default=False) #type:ignore
#     pointer_addr : bpy.props.StringProperty() #type:ignore

#     def get_pointer_item(self, root_coll:FlatPackCollection):
#         if self.is_pointer:
#             return root_coll.get(self.pointer_addr)
#         return None
    
#     def get_dependencies(self, root_coll:FlatPackCollection)->dict[FlatPackItem, bpy.types.PropertyGroup]:
#         pass


# class FlatPackCollection(bpy.types.PropertyGroup):
#     items : bpy.props.CollectionProperty(type = FlatPackItem) #type:ignore

#     def generate_pointer_id(self)->str:
#         r = "".join(random.sample(string.ascii_letters) for i in range(9))
#         while r in self.items.keys():
#             r = "".join(random.sample(string.ascii_letters) for i in range(9))
#         return r
    
#     def get_dependencies(self, coll:FlatPackCollection, item: bpy.types.PropertyGroup):
#         pass