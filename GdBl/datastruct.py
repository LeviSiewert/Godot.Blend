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

    unclaimed_subres : CollectionProperty(type=Subres) #type:ignore 
    unclaimed_extres : CollectionProperty(type=ExtResRef) #type:ignore 

class NodeGd(SubRes):
    attach = [[bpy.types.Object,  "Gd"]]
    name : StringProperty() #type:ignore
    signals : CollectionProperty(type=Signal) #type:ignore

class Signal(PropertyGroup):
    fr : PointerProperty(bpy.types.Object) #type:ignore
    to : PointerProperty(bpy.types.Object) #type:ignore
    
    #when unclaimed:
    fr_path : StringProperty()  #type:ignore
    to_path : StringProperty()  #type:ignore

class FlagEdit(PropertyGroup):
    name : StringProperty() #type:ignore
    
class SceneGd(Resource):
    attach = [[bpy.types.Collection,  "Gd"]]

    unclaimed_nodes : PointerProperty(type=NodeGd) #type:ignore 
    unclaimed_edits : PointerProperty(type=FlagEdit) #type:ignore 
    unclaimed_signals : PointerProperty(type=Signal) #type:ignore 


classes = [
    Property,
    Properties,
    SubRes,
    ExtResRef,
    Resource,
    NodeGd,
    Signal,
    FlagEdit,
    SceneGd,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
        for l,n in getattr(c, "attach", tuple()):
            setattr(l, n, PointerProperty(c))

def unregister():
    for c in register(classes):
        bpy.utils.unregister_class(c)
        for l,n in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)