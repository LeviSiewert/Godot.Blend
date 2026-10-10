from __future__ import annotations

import bpy
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty, PointerProperty

from .preferences import active_preferences, active_project, active_gdproject
from ..GdPy.core.structure import (
    Project as GdProject, 
    File as GdFile
)


class OP_ProjectIo(Operator):
    bl_label="gdpy.project_io"
    bl_idname="gdpy.project_io"
    mode : EnumProperty(items = [
        ("ADD","add",""),
        ("REMOVE","remove",""),
        ("RELOAD","reload",""),
    ]) #type:ignore

    prj_colname : StringProperty(options={"HIDDEN"}) #type:ignore

    ## File sections options:
    filepath: bpy.props.StringProperty(subtype="FILE_PATH") #type:ignore
    filter_glob: StringProperty( default="*.godot", options={'HIDDEN'}, maxlen=255 ) #type:ignore

    def invoke(self, context, event):
        if self.mode == "ADD":
            context.window_manager.fileselect_add(self)
            return {"RUNNING_MODAL"}
        else:
            return self.execute(context)
            
    def execute(self, context):
        match self.mode:
            case "ADD":
                return self.execute_add(context)
            case "REMOVE":
                return self.execute_remove(context)
            case "RELOAD":
                return self.execute_reload(context)

    def execute_add(self, context):
        prefs = active_preferences()
        _keys = prefs.project_slots.keys()
        project = prefs.project_slots.add()

        project.root = self.filepath
        # project.load_settings()

        _name = "ProjectObject"
        name = _name
        i = 0
        while name in _keys:
            name = _name + "." + str(i).zfill(3)
            i = i+1

        project.name = name


        prefs.project_selected = len(prefs.project_slots)
        return {"FINISHED"}
    
    def execute_remove(self, context):
        prefs = active_preferences()
        index = prefs.project_selected
        if index == -1:
            return
        prefs.project_slots.remove(index)
        prefs.project_selected = -1
        return {"FINISHED"}

    def execute_reload(self, context):
        pass
    
class OP_SceneIo(Operator):
    bl_label = "gdpy.scene_io"
    bl_idname = "gdpy.scene_io"
    col : StringProperty() #type:ignore
    mode : EnumProperty(items = [
        ("LOAD","load",""),
        ("RELOAD","reload",""),
        ("WRITE","write",""),
    ]) #type:ignore

    def execute(self, context):
        gdproject: GdProject|None = active_gdproject()
        col : bpy.types.Collection = bpy.data.collections[self.col]        

        if gdproject is None:
            return {"Error"}

        if col.gd.path is None:
            return {"Error"}

        gdfile : GdFile = gdproject.files.get(col.gd.path,None)

        return {"FINISHED"}

class OP_NodeIo(Operator):
    bl_label = "gdpy.node_io"
    bl_idname = "gdpy.node_io"
    obj : StringProperty() #type:ignore
    mode : EnumProperty(items = [
        ("LOAD","load",""),
        ("RELOAD","reload",""),
        ("WRITE","write",""),
    ]) #type:ignore

    def execute(self, context):
        return {"FINISHED"}


classes = [
    OP_ProjectIo,
    OP_SceneIo,
    OP_NodeIo,
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