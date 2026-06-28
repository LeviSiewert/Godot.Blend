import bpy
from .property_collection import BlPropertyCollection 
from .core.types import _BlSubResource


## GENERATED ON IMPORT/EXPORT, NO BL EQUIV:
# class BlSubResourceEdit(_BlSubResource):
# class BlResourceContainer(_BlSubResource):

class BlSubResourceExt(_BlSubResource): 
    ''' Standalone data type 
    external resource mapping, implicitly updated in tscn.
    '''
    gdtype : bpy.props.StringProperty() #type:ignore
    path : bpy.props.StringProperty() #type:ignore
    uid : bpy.props.StringProperty() #type:ignore
    unique_id : bpy.props.StringProperty() #type:ignore

class BlSubResourceCategory(_BlSubResource):
    ''' Standalone data type 
    Generic category in a settings resource
    '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    name : bpy.props.StringProperty() #type:ignore

class BlSubResource(_BlSubResource):
    ''' Standalone data type
    Script-Typeable object, generic.
    '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    gd_type : bpy.props.StringProperty() #type:ignore
    unqiue_id : bpy.props.StringProperty() #type:ignore

class BlSubResourceNode(_BlSubResource):
    ''' Placed on bpy.types.Object.Gd
    Missing properties & similar are asc/on the parent node.
    Functions are called with context.
    '''
    properties : bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore
    gd_type : bpy.props.StringProperty() #type:ignore
    script : bpy.props.StringProperty() #type:ignore
    name : bpy.props.StringProperty() #type:ignore
    unique_id : bpy.props.IntProperty() #type:ignore
    # instance : str #GENERATED, root of instance #match then generate BlSubresourceExt on export.

_all = (
    BlSubResourceExt, 
    BlSubResourceCategory,
    BlSubResource,
    BlSubResourceNode,
)