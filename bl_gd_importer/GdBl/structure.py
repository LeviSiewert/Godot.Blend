from __future__ import annotations

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty, PointerProperty, FloatProperty, FloatVectorProperty, IntVectorProperty
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator

from typing import Any, Type

from .promise import Promise
from .properties import Properties

class Signal(PropertyGroup):
    to : PointerProperty(type=bpy.types.Object) #type:ignore
    # fr # Stored on node when imported.
    to_str : StringProperty() #type:ignore
    fr_str : StringProperty() #type:ignore
    # flags, ect

class FlagEdit(PropertyGroup):
    name : StringProperty() #type:ignore


class Resource(PropertyGroup):
    ''' Global resource definition, stored on all types '''
    attach = [
        ["gd", bpy.types.Object],
        ["gd", bpy.types.Texture],
        ["gd", bpy.types.Image],
        ["gd", bpy.types.Material],
        ["gd", bpy.types.Text],
        ["gd", bpy.types.Scene],
        ["gd", bpy.types.Sound],
        ["gd", bpy.types.Light],
        ["gd", bpy.types.Camera],
        ["gd", bpy.types.Mesh],
        ["gd", bpy.types.Action],
        ["gd", bpy.types.Curve],
        ["gd", bpy.types.NodeTree],
        ["gd", bpy.types.World],
        # ["gd", bpy.types.AnimData],
    ]

    gd_type : EnumProperty(items=[
        ("SUBRESOURCE","subresource or node",""),
        ("RESOURCE","scene or resource file",""),
    ]) #type:ignore

    name : StringProperty() #type:ignore

    typing : StringProperty() #type:ignore
    script : PointerProperty(type=Promise) #type:ignore

    properties : PointerProperty(type=Properties) #type:ignore

    instance : PointerProperty(type=Promise) #type:ignore
    instance_editable : BoolProperty() #type:ignore
    
    signals : CollectionProperty(type=Signal) #type:ignore


    uid : StringProperty() #type:ignore
    path : StringProperty() #type:ignore
    
    unclaimed_subres : CollectionProperty(type=Resource) #type:ignore 
    unclaimed_extres : CollectionProperty(type=Promise) #type:ignore 
    unclaimed_signals : CollectionProperty(type=Signal) #type:ignore 
    unclaimed_edit : CollectionProperty(type=FlagEdit) #type:ignore 

class ResourceCollection(Resource):
    ''' Implementation of a scene exposed as a collection (standard method) 
    - Root object
        - required to be exported
        - is a NODE type
        - does not hold `unclaimed_...`
    '''

    gd_type : EnumProperty(items=[
        ("UNSET","",""),
        ("RESOURCE","scene or resource file",""),
        ("SUBRESOURCE","subresource or node",""),
    ]) #type:ignore
    
    attach = [ 
        ["gd", bpy.types.Collection],
    ]

    root : PointerProperty(type=bpy.types.Object) #type:ignore


classes = [
    Signal,
    FlagEdit,
    Resource,
    ResourceCollection,
]


def register():
    for c in classes:
        try:
            bpy.utils.register_class(c)
            for n,l in getattr(c, "attach", tuple()):
                setattr(l, n, PointerProperty(type=c))
        except Exception as e:
            raise Exception(e, c)
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        for n,l in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)