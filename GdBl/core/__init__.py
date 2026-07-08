import bpy

from . import property_collection
from . import structure

def register():
    property_collection.register()
    structure.register()

    bpy.types.Object.gd = bpy.props.PointerProperty(type=structure.GdNode)
    bpy.types.Collection.gd = bpy.props.PointerProperty(type=structure.GdScene)

def unregister():
    structure.unregister()
    property_collection.unregister()

    del bpy.types.Object.gd
    del bpy.types.Collection.gd