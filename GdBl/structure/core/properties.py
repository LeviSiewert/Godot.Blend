import bpy
from typing import Any
import random
import string

POINTER_PREFIX : str = "*"

class _UNSET():pass

class BlPointerItem(bpy.types.PropertyGroup):
    value : bpy.props.StringProperty() #type:ignore

class BlPropertyItem(BlPointerItem):
    name : bpy.props.StringProperty() #type:ignore
    value : bpy.props.StringProperty() #type:ignore


class BlArray(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueArray", "GdValuePackedStringArray","GdValuePackedByteArray", "GdValuePackedVector2Array","GdValuePackedVector3Array","GdValuePackedVector4Array","GdValuePackedColorArray")
    val_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    items : bpy.props.CollectionProperty(type = BlPointerItem) #type:ignore

class BlDictionaryItem(bpy.types.PropertyGroup):
    key_ptr : bpy.props.PointerProperty(type = BlPointerItem) #type:ignore
    val_ptr : bpy.props.PointerProperty(type = BlPointerItem) #type:ignore

class BlDictionary(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueDictionary",)
    key_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    val_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    items : bpy.props.CollectionProperty(type = BlDictionaryItem) #type:ignore

class BlFloatVector(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValuePackedFloat32Array","GdValuePackedFloat64Array","GdValueVector2","GdValueVector3","GdValueVector4","GdValueRect2","GdValuePlane","GdValueColor","GdValueAABB","GdValueQuaternion","GdValueTransform2D","GdValueBasis","GdValueTransform3D",)
    gdtype : bpy.props.StringProperty() #type:ignore

    def set_value(self,):
        pass
    def get_value(self,):
        pass

class BlIntVector(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueVector2i","GdValueVector3i","GdValueVector4i","GdValueRect2i","GdValuePackedInt32Array","GdValuePackedInt64Array"),
    gdtype : bpy.props.StringProperty() #type:ignore

    def set_value(self,):
        pass
    def get_value(self,):
        pass

class BlPrimitive(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueStringName","int","float","bool","None","String")
    gdtype : bpy.props.StringProperty() #type:ignore
    val_str : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_flt : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore

    def set_value(self, value:Any):
        match self.gdtype:
            case "String":
                self.val_str = value
            case "GdValueStringName":
                self.val_str = value
            case "int":
                self.val_int = value
            case "float":
                self.val_flt = value
            case "bool":
                self.val_bool = value
            case "None":
                pass
            case _:
                raise KeyError(self.gdtype, value)

    def get_value(self,):
        match self.gdtype:
            case "String":
                return self.val_str
            case "GdValueStringName":
                return self.val_str
            case "int":
                return self.val_int
            case "float":
                return self.val_flt
            case "bool":
                return self.val_bool
            case "None":
                return None
        

def _invert_dict_tuple(di:dict[str,tuple[str]])->dict[str,str]:
    res = {}
    for v,kl in di.items():
        for k in kl:
            res[k] = v
    return res

class BlPropertyCollection(bpy.types.PropertyGroup):
    ''' Class that encompasses bins and properties, where any element can hold and query pointers held by the root '''

    properties : bpy.props.CollectionProperty(type = BlPropertyItem) #type:ignore

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
        if key.startswith(POINTER_PREFIX):
            return self.fetch_pointer_data(key, default)
        if res:=self.properties.get(key, None):
            if return_ptr:
                return res
            return self.fetch_pointer_data(res.value)
        if default is _UNSET:
            raise KeyError(key)
        return default
    
    def fetch_pointer_data(self, ptr:str, default=_UNSET):
        for c in self._yield_bins():
            if obj := c.get(ptr,None):
                return obj
        if default is _UNSET:
            raise KeyError(ptr)
        return default

    def fetch_pointer_tree(self, ptr:str, chain:list[str]=None)->list:
        ''' Fetch a list of references by structure traversal '''
        if chain is None:
            chain = []
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
    
    def remove_property(self, key:str):
        ptr = self.properties[key]
        affected = self.fetch_pointer_tree(ptr.value)
        for c in self._yield_bins():
            c : bpy.types.CollectionProperty
            c_keys = tuple(c.keys())
            for ptr in affected:
                if ptr in c_keys:   
                    c.remove(c_keys.index(ptr))
                    affected.remove(ptr)
        _keys = tuple(self.properties.keys())
        self.properties.remove(_keys.index(key))
    
    def new(self, gdtype:str, key:str, *args, **kwargs)->tuple[Any,BlPropertyItem]:
        col = getattr(self,self.BIN_MAP[gdtype])
        p_str = self._generate_pointer()

        obj = col.add()
        obj.name = p_str 
        obj.gdtype = gdtype
        obj.set_value(*args, **kwargs)

        ptr = self.properties.add()
        ptr.name = key
        ptr.value = p_str
        
        return obj, ptr
    
    def _generate_pointer(self,)->str:
        _all = []
        for c in self._yield_bins():
            _all.extend(c.keys())
        r = POINTER_PREFIX+"".join(random.sample(string.ascii_letters, 9))
        while r in _all:
            r = POINTER_PREFIX+"".join(random.sample(string.ascii_letters, 9))
        return r 

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        self.remove_property(key)

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