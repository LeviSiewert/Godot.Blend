import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty

class BlProperty(PropertyGroup):
    type : StringProperty() #type:ignore
    name : StringProperty() #type:ignore
    value : StringProperty() #type:ignore

class BlPropertyCollection(PropertyGroup):
    items : CollectionProperty(type = BlProperty) #type:ignore

_all = (
    BlProperty,
    BlPropertyCollection,
)