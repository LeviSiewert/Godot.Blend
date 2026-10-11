from __future__ import annotations

import bpy
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty, PointerProperty

class Property(PropertyGroup):
    name : StringProperty() #type:ignore

class Properties(PropertyGroup):
    data : CollectionProperty(type = Property) #type:ignore
    
class SubRes(PropertyGroup):
    name : StringProperty() #type:ignore
    properies : PointerProperty(type = Properties) #type:ignore
    type : StringProperty() #type:ignore
    script : StringProperty() #type:ignore ## Path | UID | GlobalName

class ExtResRef(PropertyGroup):
    name : StringProperty() #type:ignore
    type : StringProperty() #type:ignore 
    properies : PointerProperty(type = Properties) #type:ignore

class Resource(PropertyGroup):
    uid : StringProperty() #type:ignore
    path : StringProperty() #type:ignore

    type : StringProperty() #type:ignore
    script : StringProperty() #type:ignore ## Path | UID | GlobalName
    properies : PointerProperty(type = Properties) #type:ignore

    unclaimed_subres : CollectionProperty(type=SubRes) #type:ignore 
    unclaimed_extres : CollectionProperty(type=ExtResRef) #type:ignore 

class Signal(PropertyGroup):
    fr : PointerProperty(type=bpy.types.Object) #type:ignore
    to : PointerProperty(type=bpy.types.Object) #type:ignore
    
    #when unclaimed:
    fr_path : StringProperty()  #type:ignore
    to_path : StringProperty()  #type:ignore

class NodeGd(SubRes):
    attach = [[bpy.types.Object,  "gd"]]
    name : StringProperty() #type:ignore
    signals : CollectionProperty(type=Signal) #type:ignore
    
    def draw(self, obj, context:Context, layout:UILayout):
        s = layout.operator("gdpy.node_io")
        s.obj = obj.name
        s.mode = "LOAD"



class FlagEdit(PropertyGroup):
    name : StringProperty() #type:ignore



class SceneGd(Resource):
    attach = [[bpy.types.Collection,  "gd"]]

    unclaimed_nodes : CollectionProperty(type=NodeGd) #type:ignore 
    unclaimed_edits : CollectionProperty(type=FlagEdit) #type:ignore 
    unclaimed_signals : CollectionProperty(type=Signal) #type:ignore 

    def draw(self, collection, context:Context, layout:UILayout):
        s = layout.operator("gdpy.scene_io")
        s.col = collection.name
        s.mode = "LOAD"



classes = [
    Property,
    Properties,
    SubRes,
    ExtResRef,
    Resource,
    Signal,
    NodeGd,
    FlagEdit,
    SceneGd,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
        for l,n in getattr(c, "attach", tuple()):
            setattr(l, n, PointerProperty(type=c))

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        for l,n in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)