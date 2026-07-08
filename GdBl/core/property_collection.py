from __future__ import annotations
import bpy

from .primitives.pointer_collection import (
    PointerCollection as _PointerCollection, 
    BlPointerDictionary as _BlPointerDictionary, 
    BlPointerArray as _BlPointerArray
)

class GdPropertyCollection(_PointerCollection):    
    _bins = ("bin_array","bin_dict","bin_vector","bin_primitive", "bin_reference")

    bin_dict : bpy.props.CollectionProperty(type=GdDictionary) #type:ignore
    bin_array : bpy.props.CollectionProperty(type=GdArray) #type:ignore

    bin_primitive : bpy.props.CollectionProperty(type = GdPrimitive) #type:ignore
    bin_vector : bpy.props.CollectionProperty(type = GdVector) #type:ignore
    bin_reference : bpy.props.CollectionProperty(type= GdReference) #type:ignore

class GdDictionary(_BlPointerDictionary):
    typing : bpy.props.StringProperty() #type:ignore

class GdArray(_BlPointerArray):
    typing : bpy.props.StringProperty() #type:ignore

class GdPrimitive(bpy.types.PropertyGroup):
    type : bpy.props.StringProperty() #type:ignore
    
class GdVector(bpy.types.PropertyGroup):
    type : bpy.props.StringProperty() #type:ignore
    
class GdReference(bpy.types.PropertyGroup):
    typing : bpy.props.StringProperty() #type:ignore
    type : bpy.props.StringProperty() #type:ignore


from .primitives.pointer_collection import (
    BlPointerDictionaryItem as _BlPointerDictionaryItem, 
    BlPointerArrayItem as _BlPointerArrayItem,
    BlPropertyItem as _BlPropertyItem,
)

_all = (
    _BlPropertyItem,
    _BlPointerDictionaryItem,
    _BlPointerArrayItem,
    GdPrimitive,
    GdVector,
    GdReference,
    GdDictionary,
    GdArray,
    GdPropertyCollection,
)

def register():
    for c in _all:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_all):
        bpy.utils.unregister_class(c)

    