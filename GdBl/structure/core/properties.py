import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatProperty

class BlProperty(PropertyGroup):
    name : StringProperty() #type:ignore

    type : StringProperty() #type:ignore

    val_boolean : BoolProperty() #type:ignore
    val_float : FloatProperty() #type:ignore
    val_int : IntProperty() #type:ignore
    val_str : StringProperty() #type:ignore

class BlPropertyDict(PropertyGroup):
    items : CollectionProperty(type = BlProperty) #type:ignore

class BlPropertyArray(PropertyGroup):
    items : CollectionProperty(type = BlProperty) #type:ignore

class BlPropertyCollection(PropertyGroup):
    items : CollectionProperty(type = BlProperty) #type:ignore
    dict_items : CollectionProperty(type = BlPropertyDict) #type:ignore
    array_items : CollectionProperty(type = BlPropertyArray) #type:ignore

_all = (
    BlProperty,
    BlPropertyDict,
    BlPropertyArray,
    BlPropertyCollection,
)