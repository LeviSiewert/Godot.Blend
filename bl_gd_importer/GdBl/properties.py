from __future__ import annotations

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty, PointerProperty, FloatProperty, FloatVectorProperty, IntVectorProperty
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator

from typing import Any, Type

from string import ascii_letters
from random import sample

from ..GdPy.core.structure import (
    Promise as GdPromise
)
from ..GdPy.core.values import (
    Array as GdArray,
    Dictionary as GdDictionary,
    NodePath as GdNodePath,
    _FixedLenArray as GdFixedLenArray,
    _PackedListSimple as GdPackedListSimple,
    _PackedListComplex as GdPackedListComplex,
    StringName as GdStringName,
    Object as GdObject,
)

from collections import UserDict, UserList, UserString


class Promise():
    p_type : EnumProperty(items = [
        ("SUBRESOURCE","subresource",""),
        ("EXTRESOURCE","extresource",""),
        ("EXTRESOURCE_DIRECT","extresource_direct",""), #Refereing to promise in scope, W/out address, uid, ect
        ("RID","rid",""),
    ]) #type:ignore
    id : StringProperty() #type:ignore
    uid : StringProperty() #type:ignore
    filepath : StringProperty() #type:ignore

    ptr_col : PointerProperty(type=bpy.types.Collection) #type:ignore
    ptr_obj : PointerProperty(type=bpy.types.Object) #type:ignore
    ptr_tex : PointerProperty(type=bpy.types.Texture) #type:ignore
    ptr_img : PointerProperty(type=bpy.types.Image) #type:ignore
    ptr_mat : PointerProperty(type=bpy.types.Material) #type:ignore
    ptr_txt : PointerProperty(type=bpy.types.Text) #type:ignore
    ptr_scn : PointerProperty(type=bpy.types.Scene) #type:ignore
    ptr_snd : PointerProperty(type=bpy.types.Sound) #type:ignore
    ptr_lgt : PointerProperty(type=bpy.types.Light) #type:ignore
    ptr_cam : PointerProperty(type=bpy.types.Camera) #type:ignore
    ptr_mesh : PointerProperty(type=bpy.types.Mesh) #type:ignore
    ptr_anim : PointerProperty(type=bpy.types.Animation) #type:ignore
    ptr_clip : PointerProperty(type=bpy.types.Action) #type:ignore
    ptr_curv : PointerProperty(type=bpy.types.Curve) #type:ignore
    ptr_geon : PointerProperty(type=bpy.types.NodeTree) #type:ignore
    ptr_wrld : PointerProperty(type=bpy.types.World) #type:ignore
    
class UNSET:pass

class Property[IN:Any](PropertyGroup):
    wrapper : Type[PropertyWrapper]|None = None
    name : StringProperty(name="pointer") #type:ignore

    def store(self, properties:Properties, val:IN)->None:
        ''' Store value and any dependencies stored in Properties '''
        raise NotImplementedError()
    
    def dump(self, properties:Properties): 
        ''' Dump any related values from src properties obj '''

class PropertyWrapper[PROPERTY]():
    ''' Wrapped interface, returned by PropertyBin on get/set w/a '''
    _type : Type[PROPERTY]
    _property : PROPERTY
    _properties : Properties

    def __init__(self, properties:Properties, property:PROPERTY):
        self._property = property
        self._properties = properties

    @property
    def name(self):
        return self._property.name
    @name.setter
    def name(self, val):
        self._property.name = val

class PropertyBin[IN:Any, OUT:Property|PropertyWrapper[Property]](PropertyGroup):
    ''' data container that acts as an interface for accessing and wrapping data stored in local .data'''
    in_types : tuple[Type] 
    wrapper : None|Type[PropertyWrapper] = None
    data : CollectionProperty[Property] #type:ignore

    def matches_type(self, data:Any|IN)->bool:
        return isinstance(data, self.in_types)

    def get(self, /, properties:Properties, ptr:str, default:Any=UNSET, wrap:bool=True)->OUT:
        entry = self.data.get(ptr, UNSET)
        if entry is UNSET:
            if default is UNSET:
                raise KeyError(self, ptr)
            return default
        if wrap and self.wrapper:
            return self.wrapper(properties, entry)
        return entry

    def add(self, /, properties:Properties, value:IN, wrap:bool=True)->OUT:
        return self.set(properties, properties.generate_pointer(), value, wrap)
    
    def set(self, /, properties:Properties, ptr:str, value:IN, wrap:bool=True)->OUT:
        entry = self.data.new()
        entry.name = ptr
        entry.store(value)
        if wrap and self.wrapper:
            return self.wrapper(properties, entry)
        return entry

    def delete(self, /, properties:Properties, ptr:str, not_exist_ok:bool=False):
        entry = self.data.get(ptr, UNSET)
        if entry is UNSET:
            if not not_exist_ok:
                raise KeyError(self, ptr)
            return
        entry.dump(properties)
        self.data.remove(ptr)

    def __contains__(self, ptr:str)->bool:
        return (ptr in self.data.keys()) 

class PropertiesEntry(CollectionProperty):
    name : StringProperty() #type:ignore
    ptr : StringProperty() #type:ignore

class Properties[OUT:Property|PropertyWrapper[Property]](PropertyGroup):
    ''' Dict-like using "bins" to store values ''' 
    _bins : tuple[str] = tuple()

    data : CollectionProperty(type=PropertiesEntry) #type:ignore
    
    def generate_pointer(self)->str:
        keys = tuple(self.keys())
        ptr = "".join(sample(ascii_letters,5))
        while ptr in keys:
            ptr = "".join(sample(ascii_letters,5))
        return ptr

    ## DICT INTERFACE:

    def get(self, /, key:str, default:Any=UNSET, wrap:bool=True)->OUT:
        entry = self.data.get(key, None)
        if entry is None:
            if default is UNSET:
                raise KeyError(key)
            return default
        return self.bin_get(entry.ptr, default, wrap)

    def set(self, /, key:str, value:Any, wrap:bool=True)->OUT:
        val = self.bin_add(value, wrap)
        entry = self.data.get(key, None)
        if entry is None:
            entry = self.data.new()
            entry.name = key 
        else:
            self.bin_delete(entry.ptr, not_exist_ok = True)
        entry.ptr = val.name
        return val

    def delete(self, /, key:str, not_exist_ok:bool=False):
        entry = self.data.get(key, None)
        if entry is None:
            if not not_exist_ok:
                raise KeyError(key)
            return 
        self.bin_delete(entry.ptr, not_exist_ok=True)

    def __contains__(self, key):
        return (key in self.data.keys()) or (key in self.data.values())

    def keys(self):
        yield from self.data.keys()
    
    def values(self, wrap:bool):
        for _,v in self.items(wrap):
            yield v
    
    def items(self, wrap:bool):
        for e in self.data.values():
            yield e.name, self.bin_get(e.ptr, None, wrap)

    def clear(self):
        for b in self.bins:
            b.data.clear()
        self.data.clear()

    ## PTR/DATA HANDLING:

    def bins(self):
        for k in self._bins:
            yield getattr(self, k)

    def bin_get(self, /, key:str, default:Any=UNSET, wrap:bool=True)->OUT:
        for b in self.bins():
            res = b.get(self, key, wrap=wrap, default=UNSET)
            if not (res is UNSET):
                return res
        if default is UNSET:
            raise KeyError(key)
        return default
            
    def bin_add(self, value:Any, wrap:bool):
        _bin = None
        for b in self.bins():
            if b.matches(value):
                _bin = b
                break
        if _bin is None:
            raise TypeError(self, value)

        value = _bin.add(self, value, wrap)
        return value

    def bin_delete(self, /, ptr:str):
        for b in self.bins():
            b.remove(self, ptr, not_exist_ok=True)



## IMPLEMENTATION ##

## BASIC:
class PropertyString(Property):
    subtype : StringProperty() #type:ignore
    value : StringProperty() #type:ignore
    def store(self, properties, val):
        self.value = val
class PropertyBinString(PropertyBin):
    in_types = [str, UserString]
    data : CollectionProperty(type=PropertyString) #type:ignore


class PropertyInt(Property):
    subtype : StringProperty() #type:ignore
    value : IntProperty() #type:ignore
    def store(self, properties, val):
        self.value = val
class PropertyBinInt(PropertyBin):
    in_types = [int]
    data : CollectionProperty(type=PropertyInt) #type:ignore


class PropertyFloat(Property):
    subtype : StringProperty() #type:ignore
    value : FloatProperty() #type:ignore
    def store(self, properties, val):
        self.value = val
class PropertyBinFloat(PropertyBin):
    in_types = [float]
    data : CollectionProperty(type=PropertyFloat) #type:ignore


class PropertyVector(Property):
    ...
class PropertyVectorWrapper(PropertyWrapper):
    ...
class PropertyBinVector(PropertyBin):
    in_types = [GdFixedLenArray]
    data : CollectionProperty(type=PropertyVector) #type:ignore
    PropertyVectorWrapper


class PropertyPromise(Property):
    typing : StringProperty() #type:ignore
    data : PointerProperty(type=Promise) #type:ignore
class PropertyPromiseWrapper(PropertyWrapper):
    ...
class PropertyBinPromise(PropertyBin):
    in_types = [GdPromise,Promise]
    data : CollectionProperty(type=PropertyPromise) #type:ignore
    wrapper = PropertyPromiseWrapper


## DICT GROUP

class PropertyDictItem(Property):
    name : StringProperty() #type:ignore
    ptr : StringProperty() #type:ignore
class PropertyDictItemWrapper(PropertyWrapper):
    ...

class PropertyDict(Property, PropertyBin):
    typing : StringProperty() #type:ignore
    data : CollectionProperty(type=PropertyDictItem) #type:ignore
    wrapper = PropertyDictItemWrapper
class PropertyDictWrapper(PropertyWrapper):
    ...
class PropertyBinDict(PropertyBin):
    in_types = [dict, GdDictionary, UserDict, GdObject]
    data : CollectionProperty(type=PropertyDict) #type:ignore
    wrapper = PropertyDictWrapper


## ARRAY GROUP

class PropertyArrayItem(Property):
    ptr : StringProperty() #type:ignore
class PropertyArrayItemWrapper(PropertyWrapper):
    ...

class PropertyArray(Property, PropertyBin):
    typing : StringProperty() #type:ignore
    data : CollectionProperty(type=PropertyArrayItem) #type:ignore
    wrapper = PropertyDictItemWrapper
class PropertyArrayWrapper(PropertyWrapper):
    ...
class PropertyBinArray(PropertyBin):
    in_types = [GdArray, list, UserList, GdPackedListSimple, GdPackedListComplex]
    data : CollectionProperty(type=PropertyArray) #type:ignore
    wrapper = PropertyArrayWrapper


class Properties(Properties):
    bins = [ "bin_string", "bin_float", "bin_int", "bin_promises", "bin_dict", "bin_vector", "bin_array" ]
    ## bins array also doubles as priority of match. 
    bin_string : PointerProperty(type=PropertyBinString) #type:ignore
    bin_float : PointerProperty(type=PropertyBinInt) #type:ignore
    bin_int : PointerProperty(type=PropertyBinFloat) #type:ignore
    bin_promises : PointerProperty(type=PropertyBinPromise) #type:ignore
    bin_dict : PointerProperty(type=PropertyBinDict) #type:ignore
    bin_array : PointerProperty(type=PropertyBinArray) #type:ignore
    bin_vector : PointerProperty(type=PropertyBinVector) #type:ignore

classes = [
    PropertyString,
    PropertyInt,
    PropertyFloat,
    PropertyVector,
    PropertyPromise,
    PropertyDictItem,
    PropertyDict,
    PropertyArrayItem,
    PropertyArray,
    PropertyBinString,
    PropertyBinInt,
    PropertyBinFloat,
    PropertyBinPromise,
    PropertyBinDict,
    PropertyBinArray,
    PropertyBinVector,
    Properties,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        for l,n in getattr(c, "attach", tuple()):
            setattr(l, n, PointerProperty(type=c))

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        for l,n in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)