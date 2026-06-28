import bpy
from .property_collection import BlPropertyCollection 
from .sub_resources import BlSubResource, BlSubResourceCategory, BlSubResourceExt
from .core.types import _BlResource, _BlResourceSettings

class BlResourceImport(_BlResource):
    ''' standalone data type '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    cat_resources : bpy.props.CollectionProperty(type = BlSubResourceCategory) #type:ignore

class BlResourceProject(_BlResource):
    ''' standalone data type '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    cat_resources : bpy.props.CollectionProperty(type = BlSubResourceCategory) #type:ignore

class BlResourceTres(_BlResource):
    ''' standalone data type '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    ext_resources : bpy.props.CollectionProperty(type = BlSubResourceExt) #type:ignore
    sub_resources : bpy.props.CollectionProperty(type = BlSubResource) #type:ignore

class BlResourceTscn(_BlResource):
    ''' Representated via and Stored on Collection.gd '''
    ext_resources : bpy.props.CollectionProperty(type = BlSubResourceExt) #type:ignore
    sub_resources : bpy.props.CollectionProperty(type = BlSubResource) #type:ignore

_all = (
    BlResourceTres,
    BlResourceImport,
    BlResourceProject,
    BlResourceTscn,
)