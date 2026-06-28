import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import PointerProperty, StringProperty, BoolProperty
from .sub_resources import BlSubResourceCollection, BlExtResourceCollection, BlNodeResourceCollection, BlEditResourceCollection, BlCatResourceCollection

class _BlResource(PropertyGroup):
    ''' Resource representation '''

class BlTscn(_BlResource):
    ''' Floating/Thin Tscn representation '''
    root_node : StringProperty() #type:ignore
    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore
    node_resources : PointerProperty(type=BlNodeResourceCollection) #type:ignore
    edit_resources : PointerProperty(type=BlEditResourceCollection) #type:ignore

class BlTscnOnCollection(_BlResource):
    ''' Variant for nodes that are stored inside of a Collection'''
    is_used : BoolProperty() #type:ignore
    root_node : PointerProperty(type=Object) #type:ignore

    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore
    edit_resources : PointerProperty(type=BlEditResourceCollection) #type:ignore

class BlTres(_BlResource):
    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore

class BlSettings(_BlResource):
    cat_resources : PointerProperty(type=BlCatResourceCollection) #type:ignore

_all = (
    BlTscn,
    BlTres,
    BlSettings,
    BlTscnOnCollection,
)