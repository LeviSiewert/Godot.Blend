from __future__ import annotations 
import bpy
from typing import Any
import random
import string

POINTER_PREFIX : str = "*"

class _UNSET():pass

class BlPointerItem(bpy.types.PropertyGroup):
    prt : bpy.props.StringProperty() #type:ignore

class BlPropertyItem(BlPointerItem):
    name : bpy.props.StringProperty() #type:ignore
    ptr : bpy.props.StringProperty() #type:ignore

class BlPropertyItemWrapper():
    ''' wrapper object to obscure pointers'''

    def __init__(self, root:BlPropertyCollection, data:BlPropertyItem,):
        self.root = root
        self.data = data

    @property
    def value(self):
        return self.root.get(self.ptr, None)


class BlArray(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueArray", "GdValuePackedStringArray","GdValuePackedByteArray", "GdValuePackedVector2Array","GdValuePackedVector3Array","GdValuePackedVector4Array","GdValuePackedColorArray")
    val_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    items : bpy.props.CollectionProperty(type = BlPointerItem) #type:ignore

class BlArrayWrapper():
    ''' Utility class that obscures pointers '''
    data : BlArray
    root : BlPropertyCollection
    def __init__(self, root_col:BlPropertyCollection, data:BlArray):
        self.root = root_col
        self.data = data

    def __iter__(self,):
        return self.data.items.values()

    def __eq__(self,item):
        return self.data == item

    def new(self, gdtype:str=None, *args, **kwargs)->tuple[Any,BlPointerItem]:
        if gdtype is None:
            gdtype = self.data.val_gdtype
        if (self.data.val_gdtype != "Variant"):
            if self.data.val_gdtype != gdtype:
                raise TypeError()
        ptr,obj = self.root.new_bin_value(gdtype, *args, **kwargs)
        entry = self.data.items.new()
        entry.ptr = ptr
        return entry,obj

    def remove(self, index:int):
        entry = self.data.items[index]
        self.root.remove_pointer_tree(entry.ptr)
        self.data.items.remove(index)

    def find(self, item:Any, default=_UNSET)->int:
        if isinstance(item, str):
            if item.startswith(POINTER_PREFIX):
                return self.find_by_pointer()
        
        for i,k,ptr,v in enumerate(self.items_w_pointer()):
            if v == item:
                return i

        if default is _UNSET:
            raise KeyError()

        return default
    
    def items_w_pointer(self,):
        for k,e in self.data.items():
            yield (k, e.ptr, self.root.fetch_pointer_data(e.ptr, default = None))

    def items(self,):
        for k,e in self.data.items():
            yield (k, self.root.fetch_pointer_data(e.ptr, default = None))

    def find_by_pointer(self, ptr:str, default=_UNSET):
        for i,e in self.data.items.items():
            if e.ptr == ptr:
                return i
        if default is _UNSET:
            raise KeyError()
        return default

    def find_and_remove(self, item:Any):
        index = self.find(item)
        self.remove(index)
        

class BlDictionaryItem(bpy.types.PropertyGroup):
    key_ptr : bpy.props.PointerProperty(type = BlPointerItem) #type:ignore
    val_ptr : bpy.props.PointerProperty(type = BlPointerItem) #type:ignore

class BlDictionaryItemWrapper():
    ''' Utility class that obscures pointers '''
    data : BlDictionary
    root : BlPropertyCollection

    def __init__(self, root_col:BlPropertyCollection, data:BlDictionary):
        self.root = root_col
        self.data = data

    @property
    def key(self,)->Any:
        pass

    @property
    def value(self,)->Any:
        pass

class BlDictionary(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueDictionary",)
    key_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    val_gdtype : bpy.props.StringProperty(default="Variant") #type:ignore
    items : bpy.props.CollectionProperty(type = BlDictionaryItem) #type:ignore

class BlDictionaryWrapper():
    ''' Utility class that obscures pointers '''
    data : BlDictionary
    root : BlPropertyCollection

    def __init__(self, root_col:BlPropertyCollection, data:BlDictionary):
        self.root = root_col
        self.data = data

    def items(self,):
        for e in self.data:
            yield (
                self.root.fetch_pointer_data(e.key_ptr, default = None),
                self.root.fetch_pointer_data(e.val_ptr, default = None),
                )
    def items_w_pointer(self,):
        for e in self.data:
            yield (
                e,
                self.root.fetch_pointer_data(e.key_ptr, default = None),
                self.root.fetch_pointer_data(e.val_ptr, default = None),
                )
    
    def new(self, key_ptr:str=None, val_ptr:str=None, _wrap_complex=True)->BlDictionaryItem|BlDictionaryItemWrapper:
        entry = self.data.items.new() 
        if _wrap_complex:
            return BlDictionaryItemWrapper(self.root, entry)
        return entry
    

class BlFloatVector(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValuePackedFloat32Array","GdValuePackedFloat64Array","GdValueVector2","GdValueVector3","GdValueVector4","GdValueRect2","GdValuePlane","GdValueColor","GdValueAABB","GdValueQuaternion","GdValueTransform2D","GdValueBasis","GdValueTransform3D",)
    gdtype : bpy.props.StringProperty() #type:ignore

    def set_value(self, value, /, _root_col:BlPropertyCollection=None):
        pass
    def get_value(self, /, _root_col:BlPropertyCollection=None):
        pass

class BlIntVector(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueVector2i","GdValueVector3i","GdValueVector4i","GdValueRect2i","GdValuePackedInt32Array","GdValuePackedInt64Array"),
    gdtype : bpy.props.StringProperty() #type:ignore

    def set_value(self, value, /, _root_col:BlPropertyCollection=None):
        pass
    def get_value(self, /, _root_col:BlPropertyCollection=None):
        pass

class BlPrimitive(bpy.types.PropertyGroup):
    _handles : tuple[str] = ("GdValueStringName","int","float","bool","None","str")
    gdtype : bpy.props.StringProperty() #type:ignore
    val_str : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_flt : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore

    def set_value(self, value:Any,/, _root_col:BlPropertyCollection=None):
        match self.gdtype:
            case "str":
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

    def get_value(self, /, _root_col:BlPropertyCollection=None):
        match self.gdtype:
            case "str":
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

    def _wrap_complex(self, data:Any):
        if isinstance(data, BlDictionary):
            return BlDictionaryWrapper(self,data)
        if isinstance(data, BlArray):
            return BlArrayWrapper(self,data)
        if isinstance(data, BlPropertyItem):
            return BlPropertyItemWrapper(self,data)
        return data

    def get(self, key:str, default=_UNSET,/, return_ptr=False, _wrap_complex:bool=False):
        if key.startswith(POINTER_PREFIX):
            return self.fetch_pointer_data(key, default, _wrap_complex=_wrap_complex)
        if res:=self.properties.get(key, None):
            if return_ptr:
                return res
            return self.fetch_pointer_data(res.value, _wrap_complex=_wrap_complex)
        if default is _UNSET:
            raise KeyError(key)
        return default
    
    def fetch_pointer_data(self, ptr:str, default=_UNSET, /, _wrap_complex:bool=False):
        for c in self._yield_bins():
            if obj := c.get(ptr,None):
                if _wrap_complex:
                    return self._wrap_complex(obj)
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
        if r := self.fetch_pointer_data(ptr, None, _wrap_complex=False):
            if isinstance(r, BlArray):
                for ptr in r.items.values():
                    res.extend(self.fetch_pointer_tree(item.key_ptr.value, chain))
            elif isinstance(r,BlDictionary):
                for item in r.items.values():
                    res.extend(self.fetch_pointer_tree(item.key_ptr.value, chain))
                    res.extend(self.fetch_pointer_tree(item.val_ptr.value, chain))
        return res
    
    def remove(self, key:str):
        ptr = self.properties[key]
        self.remove_pointer_tree(ptr.value)
        _keys = tuple(self.properties.keys())
        self.properties.remove(_keys.index(key))
        
    def remove_pointer_tree(self,ptr_str):
        affected = self.fetch_pointer_tree(ptr_str)
        for c in self._yield_bins():
            c : bpy.types.CollectionProperty
            c_keys = tuple(c.keys())
            for ptr in affected:
                if ptr in c_keys:   
                    c.remove(c_keys.index(ptr))
                    affected.remove(ptr)
    
    def new(self, gdtype:str, key:str, *args, **kwargs)->tuple[Any,BlPropertyItem]:
        p_str, obj = self.new_bin_value(gdtype,*args,**kwargs)
        ptr = self.properties.add()
        ptr.name = key
        ptr.value = p_str
        
        return obj, ptr

    def new_bin_value(self, gdtype:str, *args, **kwargs)->tuple[str,Any]:
        col = getattr(self,self.BIN_MAP[gdtype])
        p_str = self._generate_pointer()

        obj = col.add()
        obj.name = p_str 
        obj.gdtype = gdtype
        obj.set_value(*args, **kwargs, _root_col=self)
    
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
        self.remove(key)

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