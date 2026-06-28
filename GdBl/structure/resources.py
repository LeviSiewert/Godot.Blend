import bpy
from .property_collection import BlPropertyCollection 
from .sub_resources import SubResource, SubResourceCategory, SubResourceExt
from .core.types import _BlResource, _BlResourceSettings

class ResourceImport(_BlResource):
    ''' standalone data type '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    cat_resources : bpy.props.CollectionProperty(type = SubResourceCategory) #type:ignore

class ResourceProject(_BlResource):
    ''' standalone data type '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    cat_resources : bpy.props.CollectionProperty(type = SubResourceCategory) #type:ignore

class ResourceTres(_BlResource):
    ''' standalone data type '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    ext_resources : bpy.props.CollectionProperty(type = SubResourceExt) #type:ignore
    sub_resources : bpy.props.CollectionProperty(type = SubResource) #type:ignore

class ResourceTscn(_BlResource):
    ''' Representated via and Stored on Collection.gd '''
    ext_resources : bpy.props.CollectionProperty(type = SubResourceExt) #type:ignore
    sub_resources : bpy.props.CollectionProperty(type = SubResource) #type:ignore

_all = (
    ResourceImport,
    ResourceProject,
    ResourceTres,
    ResourceTscn,
)