import bpy
from typing import Any

POINTER_PREFIX : str = "*"

class _UNSET():pass

class BlPointerItem(bpy.types.PropertyGroup):
    value : bpy.props.StringProperty() #type:ignore

class BlPropertyItem(BlPointerItem):
    name : bpy.props.StringProperty() #type:ignore
    value : bpy.props.StringProperty() #type:ignore


class BlArray(bpy.types.PropertyGroup):
    _handles : tuple[str] = tuple()
    val_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    items : bpy.props.CollectionProperty(type = BlPointerItem) #type:ignore

class BlDictionaryItem():
    key_ptr : bpy.props.PointerProperty(type = BlPointerItem) #type:ignore
    val_ptr : bpy.props.PointerProperty(type = BlPointerItem) #type:ignore

class BlDictionary(bpy.types.PropertyGroup):
    _handles : tuple[str] = tuple()
    key_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    val_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    items : bpy.props.CollectionProperty(type = BlDictionaryItem) #type:ignore

class BlFloatVector():
    _handles : tuple[str] = tuple()
    gdtype : bpy.props.StringProperty() #type:ignore

    def set_value():
        pass
    def get_value():
        pass

class BlIntVector():
    _handles : tuple[str] = tuple()
    gdtype : bpy.props.StringProperty() #type:ignore

    def set_value():
        pass
    def get_value():
        pass

class BlPrimitive():
    _handles : tuple[str] = tuple()
    gdtype : bpy.props.StringProperty() #type:ignore
    val_str : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_flt : bpy.props.FloatProperty() #type:ignore

    def set_value():
        pass
    def get_value():
        pass

def _invert_dict_tuple(di:dict[str,tuple[str]])->dict[str,str]:
    res = {}
    for v,kl in di:
        for k in kl:
            res[k] = v
    return res

class BlPropertyCollection():
    properties : bpy.prop.CollectionProperty(type = BlPropertyItem) #type:ignore

    bin_primitives : bpy.props.CollectionProperty(type = BlPrimitive) #type:ignore
    bin_int_vectors : bpy.props.CollectionProperty(type = BlIntVector) #type:ignore
    bin_flt_vectors : bpy.props.CollectionProperty(type = BlFloatVector) #type:ignore
    bin_arrays : bpy.props.CollectionProperty(type = BlArray) #type:ignore
    bin_dictionaries : bpy.props.CollectionProperty(type = BlDictionary) #type:ignore

    BIN_MAP = _invert_dict_tuple ({
        # "properties" : ("Pointer",),
        "bin_primitives" : BlPrimitive._handles,
        "bin_int_vectors" : BlIntVector._handles,
        "bin_flt_vectors" : BlFloatVector._handles,
        "bin_arrays" : BlArray._handles,
        "bin_dictionaries" : BlDictionary._handles,
    })

    def _yield_bins(self,):
        cols = ("bin_primitives","bin_int_vectors","bin_flt_vectors","bin_arrays","bin_dictionaries")
        for k in cols:
            yield getattr(self,k)

    def get(self, key:str, default=_UNSET, return_ptr=False):
        if res:=self.properties.get(key, None):
            return res
        if default is _UNSET:
            raise KeyError(key)
        if return_ptr:
            return res
        return self.fetch_pointer_data(res.value)
    
    def fetch_pointer_data(self, ptr:str, default=_UNSET):
        for c in self._yield_bins():
            if obj := c.get(ptr,None):
                return obj
        if default is _UNSET:
            raise KeyError(ptr)
        return default

    def fetch_pointer_tree(self, ptr:str, chain:list[str])->list:
        ''' Fetch a list of references by structure traversal '''
        if ptr in chain:
            return tuple()
        res = []
        res.append(ptr)
        if r := self.fetch_pointer_data(ptr, None):
            if isinstance(r, BlArray):
                for ptr in r.items.values():
                    res.extend(self.fetch_pointer_tree(item.key_ptr.value, chain))
            elif isinstance(r,BlDictionary):
                for item in r.items.values():
                    res.extend(self.fetch_pointer_tree(item.key_ptr.value, chain))
                    res.extend(self.fetch_pointer_tree(item.val_ptr.value, chain))
        return res
    
    def remove(self, key:str):
        prop = self.properties[key]
        affected = self.fetch_pointer_tree(prop.value)
        for c in self._yield_bins():
            c_keys = c.keys()
            for ptr in affected:
                if ptr in c_keys:
                    c.remove(ptr)
                    affected.remove(ptr)
    
    def new(self, gdtype:str, key:str, value:str, *args, **kwargs)->tuple[Any,BlPropertyItem]:
        col = getattr(self,self.BIN_MAP[gdtype])
        p_str = self._generate_pointer()

        obj = col.new()
        obj.name = p_str 
        obj.gdtype = gdtype
        obj.set_value(*args, **kwargs)

        ptr = self.properties.new()
        ptr.name = key
        ptr.value = p_str
        
        return obj, ptr

_all = (
    BlPointerItem,
    BlPropertyItem,
    BlArray,
    BlDictionaryItem,
    BlDictionary,
    BlFloatVector,
    BlIntVector,
    BlPrimitive,
    BlPropertyCollection,
)