from __future__ import annotations

import bpy

from .property_collection import GdPropertyCollection


class GdProject(bpy.types.PropertyGroup):
    ''' Located in settings, automatically activated via filepath matching '''
    name : bpy.props.StringProperty() #type:ignore
    filepath : bpy.props.StringProperty() #type:ignore


class GdSceneExportSettings(bpy.types.PropertyGroup):
    export_mode : bpy.props.EnumProperty(items=(
        ("TSCN", "Tscn", "", 1),
    )) #type:ignore


class GdScene(bpy.types.PropertyGroup):
    export_settings : bpy.props.PointerProperty(type=GdSceneExportSettings) #type:ignore
    
    file : str
    uid : str

    root_node : bpy.props.PointerProperty(type=bpy.types.Object) #type:ignore
    sub_resources : bpy.props.CollectionProperty(type=SubResource) #type:ignore
    ext_resources : bpy.props.CollectionProperty(type=ExtResource) #type:ignore
    #edit_flags ## Generated at export time.


class GdResource(bpy.types.PropertyGroup):
    file : str
    uid : str
    
    sub_resources : bpy.props.CollectionProperty(type=SubResource) #type:ignore
    ext_resources : bpy.props.CollectionProperty(type=ExtResource) #type:ignore
    #edit_flags ## Generated at export time.


class GdNode(bpy.types.PropertyGroup):
    name : bpy.props.IntProperty() #type:ignore
    type : bpy.props.StringProperty() #type:ignore
    
    properties : bpy.props.PointerProperty(type=GdPropertyCollection) #type:ignore

class SubResource(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty() #type:ignore
    type : bpy.props.StringProperty() #type:ignore
    
    properties : bpy.props.PointerProperty(type=GdPropertyCollection) #type:ignore

class ExtResource(bpy.types.PropertyGroup):
    type : bpy.props.StringProperty() #type:ignore
    path : bpy.props.StringProperty() #type:ignore
    uid : bpy.props.StringProperty() #type:ignore
    id : bpy.props.StringProperty() #type:ignore

_all = (
    ExtResource,
    SubResource,
    GdResource,
    GdNode,
    GdSceneExportSettings,
    GdScene,
    GdProject,
)

def register():
    for c in _all:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_all):
        bpy.utils.unregister_class(c)

    