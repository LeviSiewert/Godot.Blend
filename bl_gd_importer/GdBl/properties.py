from __future__ import annotations

import bpy
from enum import Enum
from typing import Any, Type, Iterable

from random import sample
from string import ascii_letters

class UNSET:...

class ReturnType(Enum):
    POINTER = 0
    PROPERTY = 1
    WRAPPED = 2
    EXPORT = 3

class Property_Base(bpy.types.PropertyGroup):
    def store(self, properties:Properties_Base, val:Any):
        raise NotImplementedError()
    def dump(self, properties:Properties_Base):
        raise NotImplementedError()
    def export(self, properties:Properties_Base):
        raise NotImplementedError()
    
class Property_Wrapped:
    _properties : Properties_Base
    _property : Property_Base
    def __init__(self, properties:Property_Base, prop:Property_Base):
        self._properties = properties
        self._properties = prop

    def store(self, val:Any):
        return self._property.store(self._properties, val)
    def dump(self):
        return self._property.dump(self._properties)
    def export(self, *args, **kwargs):
        return self._property.export(self._properties, *args, **kwargs)

class Property_Bin(bpy.types.PropertyGroup):
    data : bpy.props.CollectionProperty #: bpy.props.CollectionProperty(type=...)
    types : tuple[Type] = tuple()
    wrapper : Type|None = None

    @staticmethod
    def _return_type(properties:Properties_Base, bin:Property_Bin, entry:Property_Base, return_type:ReturnType)->Property_Bin|Property_Base|str|Any:
        wrapper :Property_Wrapped|None = bin.wrapper
        match return_type:
            case ReturnType.EXPORT:
                return entry.export(properties)
            case ReturnType.WRAPPED:
                if (wrapper is None):
                    return entry
                return wrapper(properties=properties, property=entry)
            case ReturnType.POINTER:
                return entry.name
            case ReturnType.PROPERTY:
                return entry
        raise NotImplementedError()

    def bin_items(self, properties:Properties_Base, return_type:ReturnType=ReturnType.WRAPPED):
        for v in self.data:
            yield v.name, self._return_type(properties, self, entry=v, return_type=return_type)

    def bin_values(self, properties:Properties_Base, return_type:ReturnType=ReturnType.WRAPPED):
        for entry in self.data:
            yield self._return_type(properties, self, entry, return_type=return_type)
        
    def bin_keys(self):
        yield from self.data.keys()

    def bin_match(self, properties:Properties_Base, val:Any)->bool:
        return isinstance(val, self.types)

    def bin_store(self, properties:Properties_Base, val:Any, return_type:ReturnType=ReturnType.WRAPPED)->Property_Base:
        entry = self.data.add()
        entry.name = properties.bin_generate_pointer(self)
        entry.store(val)
        return self._return_type(properties, self, entry, return_type=return_type)
        
    def bin_get(self, properties:Properties_Base, ptr:str, default:Any=UNSET, return_type:ReturnType=ReturnType.WRAPPED)->Property_Base|None:
        if ptr == "":
            return None
        entry = self.data.get(ptr, None)
        if (entry is None):
            if not (default is UNSET):
                return default
            raise KeyError(ptr)
        return self._return_type(properties, self, entry, return_type=return_type)                

    def bin_remove(self, properties:Properties_Base, ptr:str, not_exist_ok:bool=False)->None:
        if ptr == "":
            return
        entry = self.bin_get(properties, ptr, default=None, return_type=ReturnType.PROPERTY)
        if (entry is None):
            if not_exist_ok:
                return
            raise KeyError(ptr)
        entry.dump(properties)

    def __contains__(self, key:str):
        return (key in self.data.keys())


class Properties_Base(bpy.types.PropertyGroup):
    _bins : tuple[str]

    def bins(self):
        for k in self._bins:
            yield getattr(self,k)

    def bin_items(self, return_type:ReturnType=ReturnType.WRAPPED):
        for b in self.bins():
            yield from b.bin_items(return_type=return_type)

    def bin_values(self, return_type:ReturnType=ReturnType.WRAPPED):
        for b in self.bins():
            yield from b.bin_values(return_type=return_type)
        
    def bin_keys(self):
        for b in self.bins():
            yield from b.bin_keys()

    def bin_generate_pointer(self, bin:Property_Bin|None=None):
        r = "".join(sample(ascii_letters, 9))
        if r in (keys:=tuple(self.keys())):
            while r in keys:
                r = "".join(sample(ascii_letters, 9))
        return r 

    def bin_match(self, val:Any)->Property_Bin:
        for b in self.bins():
            b : Property_Bin
            if b.bin_match(self, val):
                return b
        raise TypeError(val)
    
    def bin_store(self, val:Any, return_type:ReturnType=ReturnType.WRAPPED)->Property_Base:
        return self.bin_match(val).bin_store(self, val, return_type=return_type)
        
    def bin_get(self, ptr:str, default:Any=UNSET, return_type:ReturnType=ReturnType.WRAPPED)->Property_Base|None:
        if ptr == "":
            return None
        for b in self.bins():
            r = b.bin_get(ptr, default=None, return_type=return_type)
            if not (r is None):
                return r
        if default is UNSET:
            raise KeyError(ptr)
        return default

    def bin_remove(self, ptr:str, not_exist_ok:bool=False)->None:
        if ptr == "":
            return
        for b in self.bins():
            b : Property_Bin
            if ptr in b:
                b.bin_remove(self, ptr)
                return
        if not not_exist_ok:
            raise KeyError(ptr)

    def bin_clear(self):
        for b in self.bins():
            for i in range(len(b.data)):
                b.data.remove(i)

    def clear(self):
        self.bin_clear()


## INT ##

class Property_Int(Property_Base):
    value : bpy.props.IntProperty() #type:ignore
    def store(self, val):
        self.value = int(val)
    def dump(self, properties=None):
        pass
    def export(self, properties=None):
        return self.value

class Property_Bin_Int(Property_Bin):
    data : bpy.props.CollectionProperty(type=Property_Int) #type:ignore
    types = (int,)
    wrapper = None

## FLOAT ##

class Property_Float(Property_Base):
    value : bpy.props.FloatProperty() #type:ignore
    def store(self, val):
        self.value = int(val)
    def dump(self):
        pass
    def export(self):
        return self.val

class Property_Bin_Float(Property_Bin):
    data : bpy.types.CollectionProperty(type=Property_Float) #type:ignore
    types = (float,)
    wrapper = None


## VECTOR ##

from ..GdPy.core.values import (
    Vector2i as GdVector2i,
    Vector3i as GdVector3i,
    Vector4i as GdVector4i,
    Rect2i as GdRect2i,
    Vector2 as GdVector2,
    Vector3 as GdVector3,
    Vector4 as GdVector4,
    Rect2 as GdRect2,
    Plane as GdPlane,
    Color as GdColor,
    AABB as GdAABB,
    Quaternion as GdQuaternion,
    Transform2D as GdTransform2D,
    Transform3D as GdTransform3D,
    Basis as GdBasis,
)

class Property_Vector(Property_Base):
    subtype : bpy.props.StringProperty() #type:ignore
    ## Not as effecient as an enum, but a bullwark against class name changes.
    subtypes = {
        GdVector2i.__class__.__name__.lower() : GdVector2i,
        GdVector3i.__class__.__name__.lower() : GdVector3i,
        GdVector4i.__class__.__name__.lower() : GdVector4i,
        GdRect2i.__class__.__name__.lower() : GdRect2i,
        GdVector2.__class__.__name__.lower() : GdVector2,
        GdVector3.__class__.__name__.lower() : GdVector3,
        GdVector4.__class__.__name__.lower() : GdVector4,
        GdRect2.__class__.__name__.lower() : GdRect2,
        GdPlane.__class__.__name__.lower() : GdPlane,
        GdColor.__class__.__name__.lower() : GdColor,
        GdAABB.__class__.__name__.lower() : GdAABB,
        GdQuaternion.__class__.__name__.lower() : GdQuaternion,
        GdTransform2D.__class__.__name__.lower() : GdTransform2D,
        GdTransform3D.__class__.__name__.lower() : GdTransform3D,
        GdBasis.__class__.__name__.lower() : GdBasis,
    }

    vector2i : IntVectorProperty(size=2) #type:ignore
    vector3i : IntVectorProperty(size=3) #type:ignore
    vector4i : IntVectorProperty(size=4) #type:ignore
    rect2i : IntVectorProperty(size=4) #type:ignore
    vector2 : FloatVectorProperty(size=2) #type:ignore
    vector3 : FloatVectorProperty(size=3) #type:ignore
    vector4 : FloatVectorProperty(size=4) #type:ignore
    rect2 : FloatVectorProperty(size=4) #type:ignore
    plane : FloatVectorProperty(size=4) #type:ignore
    color : FloatVectorProperty(size=4, subtype="COLOR") #type:ignore
    aabb : FloatVectorProperty(size=6) #type:ignore
    quaternion : FloatVectorProperty(size=4, subtype="QUATERNION") #type:ignore
    transform2d : FloatVectorProperty(size=6) #type:ignore
    transform3d : FloatVectorProperty(size=12) #type:ignore
    basis : FloatVectorProperty(size=9) #type:ignore

    def store(self, val):
        self.value = str(val)
        if (st := val.__class__.__name__.lower()) in self.subtypes.keys():
            self.subtype = st
        else:
            self.property_unset("subtype")
    def dump(self):
        pass
    def export(self):
        return self.subtypes.get(self.subtype, str)(getattr(self, self.subtype))

    def __iter__(self,):
        yield from getattr(self, self.subtype)

class Property_Bin_Vector(Property_Bin):
    data : bpy.props.CollectionProperty(type=Property_Vector) #type:ignore
    types = (GdVector2i, GdVector3i, GdVector4i, GdRect2i, GdVector2, GdVector3, GdVector4, GdRect2, GdPlane, GdColor, GdAABB, GdQuaternion, GdTransform2D, GdTransform3D, GdBasis)
    wrapper = None

## STRINGS ## 

from ..GdPy.core.values import (
    NodePath as GdNodePath, 
    StringName as GdStringName,
)
from collections import UserString

class Property_String(Property_Base):
    value : bpy.props.StringProperty() #type:ignore
    subtype : bpy.props.StringProperty() #type:ignore
    ## Not as effecient as an enum, but a bullwark against class name changes.
    subtypes = {
        GdNodePath.__class__.__name__.lower():GdNodePath, 
        GdStringName.__class__.__name__.lower():GdStringName,
    }
    def store(self, properties, val):
        self.value = str(val)
        if (st := val.__class__.__name__.lower()) in self.subtypes.keys():
            self.subtype = st
        else:
            self.property_unset("subtype")
    def dump(self, properties):
        pass
    def export(self, properties):
        return self.subtypes.get(self.subtype, str)(self.val)

class Property_Bin_String(Property_Bin):
    data : bpy.types.CollectionProperty(type=Property_String) #type:ignore
    types = (str, GdNodePath, GdStringName, UserString)
    wrapper = Property_Wrapped


## PROMISE

# from ..GdPy.core.structure import ( 
#     Promise as GdPromise
# )
# from .structure import (
#     Promise as BlPromise
# )

# class PropertyPromise(Property_Base):
#     typing : StringProperty() #type:ignore
#     data : PointerProperty(type=BlPromise) #type:ignore
    
# class Property_Bin_Promise(Property_Bin):
#     in_types = (GdPromise, BlPromise)
#     data : CollectionProperty(type=PropertyPromise) #type:ignore


## ARRAY ## 

class ArrayItem(bpy.types.PropertyGroup):
    ptr : bpy.props.StringProperty() #type:ignore

class Property_Array(Property_Base):
    subtype : bpy.props.StringProperty() #type:ignore
    subtypes = {

    }
    data : bpy.props.CollectionProperty(type=ArrayItem) #type:ignore

    def store(self, properties, val:Iterable):
       self.dump(properties)
       for v in val:
           entry = self.data.add()
           entry.name = properties.bin_store(val = v, return_type=ReturnType.POINTER)

    def dump(self, properties):
        for ptr in self.values(return_type=ReturnType.POINTER):
            properties.bin_remove(ptr)

    def export(self, properties)->tuple:
        return tuple(self.values(properties=properties, return_type=ReturnType.EXPORT))

    def values(self, properties:Properties_Base, return_type:ReturnType=ReturnType.WRAPPED):
        match return_type:
            case ReturnType.POINTER:
                for e in self.data:
                    yield e.ptr
            case ReturnType.EXPORT:
                for e in self.data:
                    yield properties.bin_get(e.ptr, return_type=ReturnType.PROPERTY).export(properties)
            case ReturnType.PROPERTY:
                for e in self.data:
                    yield properties.bin_get(e.ptr, return_type=ReturnType.PROPERTY)
            case ReturnType.WRAPPED:
                    yield properties.bin_get(e.ptr, return_type=ReturnType.WRAPPED)
        
    def __len__(self):
        return len(self.data)
    
    def __contains__(self, item):
        return item in self.data.keys()

class Property_Bin_Array(Property_Bin):
    types = (list,)
    data = bpy.props.CollectionProperty(type=Property_Array)


class Properties(Properties_Base):
    _bins = ("bin_int",)
    # _bins = ( "bin_float", "bin_int", "bin_vector", "bin_string", "bin_promise", "bin_array", )

    bin_int : bpy.props.PointerProperty(type=Property_Bin_Int) #type:ignore
    # bin_float : bpy.props.PointerProperty(type=Property_Bin_Float) #type:ignore
    # bin_vector : bpy.props.PointerProperty(type=Property_Bin_Vector) #type:ignore
    # bin_string : bpy.props.PointerProperty(type=Property_Bin_String) #type:ignore
    # # bin_promise : bpy.props.PointerProperty(type=Property_Bin_Promise) #type:ignore
    # bin_array : bpy.props.PointerProperty(type=Property_Bin_Array) #type:ignore


classes = [
    Property_Int,
    Property_Bin_Int,
    # Property_Float,
    # Property_Bin_Float,
    # Property_Vector,
    # Property_Bin_Vector,
    # Property_String,
    # Property_Bin_String,
    # # Property_Promise,
    # # Property_Bin_Promise,
    # ArrayItem,
    # Property_Array,
    # Property_Bin_Array,
    Properties,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
        for l,n in getattr(c, "attach", tuple()):
            setattr(l, n, bpy.props.PointerProperty(type=c))
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        for l,n in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)