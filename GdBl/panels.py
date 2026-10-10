import bpy
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty, PointerProperty


class PT_ScenePanel(bpy.types.Panel):
    bl_label = "Godot Info"
    bl_idname = "GDSCENE_PT_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "collection"

    def draw(self, context):
        layout = self.layout
        collection = context.collection
        collection.gd.draw(collection, context, layout)

class PT_ObjectPanel(bpy.types.Panel):
    bl_label = "Godot Info"
    bl_idname = "GDNODE_PT_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        obj.gd.draw(obj, context, layout)


classes = [
    PT_ScenePanel,
    PT_ObjectPanel,
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