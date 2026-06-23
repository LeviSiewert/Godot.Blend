from __future__ import annotations
import bpy
import random
import string

from typing import Any,Generator

POINTER_PREFIX = "*"

class _UNSET():
    pass

class EMPTYPOINTER():
    pass

class _Wrapper:
    root : PointerCollection
    data : Any
    def __init__(self, root:PointerCollection, data:Any):
        self.root = root
        self.data = data


class BlArrayItem(bpy.types.PropertyGroup):
    _duplicate_on_copy = True
    ptr : bpy.props.StringProperty() #type:ignore
    def _wrap(self, root:PointerCollection)->BlArrayItemWrapper:
        return BlArrayItemWrapper(root, self)
    def _list_sub_pointers()->tuple[str]:
        raise NotImplementedError()
class BlArrayItemWrapper(_Wrapper):
    @property
    def value(self,)->Any:
        return self.root.get_value(self.data.ptr, default=EMPTYPOINTER)
    @value.setter
    def value(self, value):
        if self.root._is_pointer(value):
            self.data.ptr = value
            return
        if self.data.ptr != "":
            self.root.set_value(self.root._generate_pointer(), value)
            return
        self.root.set_value(self.data.ptr, value)


class BlArray(bpy.types.PropertyGroup):
    _duplicate_on_copy = True
    items : bpy.props.CollectionProperty(type = BlArrayItem) #type:ignore
    def _wrap(self, root:PointerCollection)->BlArrayWrapper:
        return BlArrayWrapper(root, self)
    def _list_sub_pointers()->tuple[str]:
        raise NotImplementedError()
class BlArrayWrapper(_Wrapper):
    def __iter__(self,):
        for e in self.data.items.values():
            yield self.root.get_value(e.ptr, default=EMPTYPOINTER)
    def values(self, yield_entry=False, wrap=True):
        for e in self.data.items.values():
            if yield_entry and wrap:
                yield self.root._wrap(e), self.root.get_value(e.ptr, default=EMPTYPOINTER, wrap=wrap)
            elif yield_entry:
                yield e, self.root.get_value(e.ptr, default=EMPTYPOINTER, wrap=wrap)
            else:
                yield self.root.get_value(e.ptr, default=EMPTYPOINTER, wrap=wrap)

    def set_value(val, /, subtype:str=None):
        raise NotImplementedError()

class BlDictionaryItem(bpy.types.PropertyGroup):
    _duplicate_on_copy = True
    val_ptr : bpy.props.StringProperty() #type:ignore
    key_ptr : bpy.props.StringProperty() #type:ignore
    def _wrap(self, root:PointerCollection)->BlDictionaryItemWrapper:
        return BlDictionaryItemWrapper(root, self)
    def _list_sub_pointers()->tuple[str]:
        raise NotImplementedError()
    
class BlDictionaryItemWrapper(_Wrapper):
    @property
    def key(self,)->Any:
        return self.root.get_value(self.data.key_ptr, default=EMPTYPOINTER)
    @key.setter
    def key(self, value):
        self.root.set_value(self.data.key_ptr, value)
        if self.root._is_pointer(value):
            self.data.key_ptr = value
            return
        if self.data.key_ptr != "":
            self.root.set_value(self.root._generate_pointer(), value)
            return
        self.root.set_value(self.data.key_ptr, value)

    @property
    def value(self,)->Any:
        return self.root.get_value(self.data.val_ptr, default=EMPTYPOINTER)
    @value.setter
    def value(self, value):
        if self.root._is_pointer(value):
            self.data.val_ptr = value
            return
        if self.data.val_ptr != "":
            self.root.set_value(self.root._generate_pointer(), value)
            return
        self.root.set_value(self.data.val_ptr, value)

class BlDictionary(bpy.types.PropertyGroup):
    _duplicate_on_copy = True
    items : bpy.props.CollectionProperty(type = BlDictionaryItem) #type:ignore
    def _wrap(self, root:PointerCollection)->BlDictionaryWrapper:
        return BlDictionaryWrapper(root, self)
    def _list_sub_pointers()->tuple[str]:
        raise NotImplementedError()
class BlDictionaryWrapper(_Wrapper):
    def items(self, yield_entry=False, wrap=True):
        for e in self.data.items.values():
            k = self.root.get_value(e.key_ptr, default=EMPTYPOINTER, wrap=True)
            v = self.root.get_value(e.val_ptr, default=EMPTYPOINTER, wrap=True)
            if yield_entry and wrap:
                yield self.root._wrap(e),k,v
            elif yield_entry:
                yield e,k,v
            else:
                yield k,v
    def set_value(val, /, subtype:str=None):
        raise NotImplementedError()

class BlPropertyItem(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty() #type:ignore
    ptr : bpy.props.StringProperty() #type:ignore

class PointerCollection(bpy.types.PropertyGroup):
    ''' Base class, seperated for later portability '''
    #TODO : Tree splitting via _duplicate_on_copy
    #TODO : User counts on items
    #TODO : Consider default TransformerV2 in set_value to/from regular python values.
    #TODO : Typing system, Eventually
    
    _bins : tuple[str] = ("bin_array", "bin_dict")
    
    properties : bpy.props.CollectionProperty(type = BlPropertyItem) #type:ignore
    bin_array : bpy.props.CollectionProperty(type = BlArray) #type:ignore
    bin_dict : bpy.props.CollectionProperty(type = BlDictionary) #type:ignore
    
    def _bin_key_matcher(self, key:str )->bpy.types.CollectionProperty:
        if res := getattr(self, key, None):
            return res
        raise KeyError("Could not determine bin for key", key)
    
    def _bin_val_to_key_matcher(self, val:Any)->str:
        raise KeyError("Could not determine bin for value", val)

    def _iter_bins(self,)->Generator[bpy.types.CollectionProperty]:
        for k in self._bins:
            yield getattr(self,k)

    def _get_all_pointers(self,)->tuple[str]:
        res = []
        for b in self._iter_bins:
            res.extend(b.keys())
        return tuple(res)

    def _generate_pointer(self,)->str:
        _all = self._get_all_pointers() 
        r = POINTER_PREFIX+"".join(random.sample(string.ascii_letters, 9))
        while r in _all:
            r = POINTER_PREFIX+"".join(random.sample(string.ascii_letters, 9))
        return r 

    def get_value(self, ptr:str, /, default=_UNSET, wrap=True):
        for b in self._iter_bins:
            if res := b.get(ptr,None):
                if wrap:
                    return self._wrap(res)
                return res
        if default is _UNSET:
            raise KeyError(ptr)
        return default
    
    def store_value(self, val:Any, /, ptr:str=None, subtype:str=None, wrap=True, exist_ok=False)->tuple[Any,str]:
        col : bpy.types.CollectionProperty
        
        if not exist_ok:
            if res:=self.get_value(ptr):
                raise KeyError(ptr, res)

        if subtype is None:
            subtype = self._bin_val_to_key_matcher(val)
        col = self._bin_key_matcher(subtype)
        
        item = col.add()

        if ptr is None:
            item.name = self._generate_pointer()
        else:
            assert(not (ptr in self._get_all_pointers()))
            item.name = ptr

        item.set_value(val, subtype=subtype)
        if wrap:
            return self._wrap(item), ptr
        return item,ptr
    
    def set_value(self, ptr:str, val:Any, /, subtype:str=None, make_ok=True, wrap=True):
        if (not make_ok): 
            if (self.get_value(ptr, None) is None):
                raise KeyError(ptr)
        self.delete_value(ptr)
        return self.store_value(val, ptr=ptr, subtype=subtype, wrap=wrap, exist_ok=True)
        
    def delete_value(self, ptr:str):
        _all_ptrs = self._get_sub_pointers(ptr)
        for c in self._iter_bins():
            cks = c.keys()
            for p in _all_ptrs:
                if not p in cks:
                    continue
                c.remove(cks.find(p))

    def _get_sub_pointers(self, ptr:str, _explored:list=None)->list[str]:
        if _explored is None:
            _explored = []

        if ptr in _explored:
            return tuple()
        _explored.append(ptr)

        item = self.get(ptr)

        if hasattr(item,"_list_sub_pointers"):
            res = []
            new = item._list_sub_pointers()
            for sptr in new:
                new = (self._get_sub_pointers(sptr, _explored))
                res.extend(new)
            return res
        return tuple()


    def new_property(self, key:str, val:Any, /, subtype:str=None, wrap=True)->tuple[Any,BlPropertyItem]:
        assert(not (key in self.properties.keys()))
        
        val, ptr = self.store_value(val, subtype=subtype)
        
        prop = self.properties.new()
        prop.name = key
        prop.ptr = ptr

        if wrap:
            return self._wrap(val), self._wrap(prop)
        return val, prop

    def get_property(self, key:str, /, default=_UNSET, wrap=True):
        res = self.properties.get(key)
        if res is _UNSET:
            raise KeyError(key)
        if wrap:
            return self._wrap(res)
        return res

    def set_property(self, key:str, val:Any, /, subtype:str=None, make_ok=True, wrap=True)->tuple[Any,BlPropertyItem]:
        if key in self.properties[key]:
            prop = self.properties[key]
            self.delete_value(prop.ptr)
        elif not make_ok:
            raise KeyError(key)
        else:
            prop = self.properties.new()
            prop.name = key
        ptr,obj = self.store_value(key,val,subtype=subtype)
        prop.ptr = ptr
        if wrap:
            return self._wrap(obj), self._wrap(prop)
        return obj, prop

    def delete_property(self, key):
        prop = self.properties[key]
        self.delete_value(prop.ptr)
        pcs = self.properties.keys()
        self.properties.remove(pcs.find(key))


    def _wrap(self, item):
        if hasattr(item,"_wrap"):
            return item._wrap(self)
        return item
    
    def _is_pointer(self,key:str|Any)->bool:
        if isinstance(key,str):
            return key.startswith(POINTER_PREFIX)
        return False


    def get(self, key, /, default=_UNSET, wrap=True, return_prop=False):
        if not self._is_pointer(key):
            prop = self.get_property(key, default=None, wrap=wrap)

            if (prop is None) and default is _UNSET:
                raise KeyError(key)
            elif (prop is None):
                return default
            if return_prop:
                return prop
            
            return self.get_value(prop.ptr, default=default, wrap=wrap)
        else:
            return self.get_value(key, default=default, wrap=wrap)

    def set(self, key, value, /, subtype=None, make_ok=True, wrap=True)->tuple[str,Any]:
        if not self._is_pointer(key): 
            return self.set_property(key, value, subtype=subtype, make_ok=make_ok, wrap=wrap )
        else:
            return self.set_value(key, value, subtype=subtype, make_ok=make_ok, wrap=wrap)

    def remove(self, key):
        if not self._is_pointer(key): 
            return self.delete_property(key)
        else:
            return self.delete_value(key)

_all = (
    BlArrayItem,
    BlArray,
    BlDictionaryItem,
    BlDictionary,
    BlPropertyItem,
)