from __future__ import annotations
import bpy
from .. import GdPy
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty

from ..addon_config import bl_info, id_name

class ModuleOption(PropertyGroup):
    name : StringProperty() #type:ignore
    uid : StringProperty() #type:ignore #Module.uid / Version / id

    ##TODO: Virtual Properties, write back to singleton
    value_str : StringProperty() #type:ignore
    value_int : IntProperty() #type:ignore
    value_bool : BoolProperty() #type:ignore
    value_enum : EnumProperty(items=[]) #type:ignore

    def draw_line(self, context, layout):
        #TODO: draw from singleton options using uid.
        ...

class MODULE_OPTION_UL_regular(bpy.types.UIList):
    def draw_item(self, context, layout, data:Preferences, item:ModuleOption, icon, active_data, active_propname):
        item.draw_line(context, layout)

class ModuleVersion(PropertyGroup):
    ## STATIC:
    ver  : StringProperty() #type:ignore
    uid  : StringProperty() #type:ignore #Module.uid / Version
    # path : StringProperty() #type:ignore 
    # desc : StringProperty() #type:ignore

    ## MUTABLE:
    options : CollectionProperty(type=ModuleOption) #type:ignore

    def draw_line(self, context:Context, layout:UILayout):
        ## TODO: draw from signleton && self.options
        layout.label(self.ver)
        layout.label(str(len(self.options)))

    def draw_full(self, context:Context, layout:UILayout):
        ## TODO: draw from signleton && self.options, incl revert to default
        ...


class MODULE_VERSION_UL_regular(bpy.types.UIList):
    ## TODO: Sort by version!
    def draw_item(self, context, layout, data:Preferences, item:Project, icon, active_data, active_propname):
        item.draw_line(context, layout)

class Module(PropertyGroup):
    ''' Settings entry Imported & Exported to modules.json. Used to drive transformers, discovered from .bl.py files in project '''
    # From .bl.py file(s):
    uid  : StringProperty() #type:ignore # prim id

    # local to modules.json:
    enabled : BoolProperty() #type:ignore

    version_slots : CollectionProperty(type=ModuleVersion) #type:ignore
    version_index : IntProperty() #type:ignore
    version_active : EnumProperty(items=[]) #type:ignore

    def draw_line(self, context:Context, layout:UILayout):
        layout.label(self.enabled, text="")
        layout.label(self.name, text="")
        layout.label(self.active_version, text="")

    def draw_full(self, context:Context, layout:UILayout):
        layout.label(self.enabled)
        layout.label(self.name)
        layout.label(self.active_version)
        ... # TODO: draw from python only Module data "singleton" using UID. Err if missing

    def _active_version_set(self, value):
        self["active_version"] = value
        ... #TODO: Declare

    def _enabled_set(self, value):
        self["enabled"] = value
        ... #TODO: Declare


class MODULE_UL_regular(bpy.types.UIList):
    def draw_item(self, context, layout, data:Preferences, item:Module, icon, active_data, active_propname):
        item.draw_line(context, layout)


class Project(PropertyGroup):
    name : StringProperty(name="name") #type:ignore
    root : StringProperty(name="path", subtype="FILE_PATH") #type:ignore

    classes_path : StringProperty(name="Classes Path", subtype="FILE_PATH", default="res://.blender/classes.json") #type:ignore
    modules_path : StringProperty(name="Modules Path", subtype="FILE_PATH", default="res://.blender/modules.json") #type:ignore
    caching_path : StringProperty(name="Caching Path", subtype="DIR_PATH", default="res://.blender/.caching/") #type:ignore

    module_slots : CollectionProperty(type=Module) #type:ignore
    module_selected : IntProperty() #type:ignore

    def godot_make_abs(self, path:str)->str:
        if not path.startswith("res://"):
            return path
        if self.root == "":
            return path
        return self.root.strip(".godot") + "/" + path[6:]

    def godot_make_rel(self, path:str)->str:
        if path.startswith("res:://"):
            return path
        if self.root == "":
            return path
        root = self.root.strip(".godot")
        if not path.startswith(root):
            return "res://"+path[len(root):]
        return path

    @property
    def classes_fullpath(self):
        return self.godot_make_abs(self.classes_path)
    @property
    def modules_fullpath(self):
        return self.godot_make_abs(self.modules_fullpath)
    @property
    def caching_fullpath(self):
        return self.godot_make_abs(self.caching_fullpath)

    def draw_line(self, context:Context, layout:UILayout):
        ''' Preferences list of Projects'''
        # layout.label(text = self.name)
        layout.label(text=self.name)
        layout.prop(self,"root")

    def draw_full(self, context:Context, layout:UILayout):
        ''' Preferences w/ this selected '''
        layout.prop(self,"name")
        layout.prop(self,"root")
        
        layout.prop(self,"classes_path")
        layout.prop(self,"modules_path")
        layout.prop(self,"caching_path")

        layout.label(text="WARNING: This is a synced rep of the modules.json file. All changes are pushed to disc! ")
        row = layout.row()
        options = row.operator("blgd.ops_modules", text="reload")
        # options.path = self.root.strip(".godot") + "/" + self.modules_path.strip("res://")
        options = row.operator("blgd.ops_modules", text="save")
        
        layout.template_list("MODULE_UL_regular", "", self, "module_slots", self, "module_selected")

        if (len(self.module_slots)-1) >= self.module_selected:
            self.module_slots[self.module_selected].draw_full(context, layout)
    
    @staticmethod
    def draw_header_container(context:Context, layout:UILayout):
        if prj:=preferences(context).active_project:
            prj.draw_header(context,layout)

    def draw_header(self, context:Context, layout:UILayout):
        ''' Header property next to scene '''

    @property
    def is_viable(self)->bool:
        fp = bpy.data.filepath
        if not fp: 
            return False 
        if not self.root:
            return False
        return fp.startswith(self.root.strip("/.godot"))

    @property
    def project(self)->GdPy.core.Project:
        pass

    def _on_activate(self):
        pass

    def _on_deactivate(self):
        pass

        
class PROJECT_UL_regular(bpy.types.UIList):
    def draw_item(self, context, layout, data:Preferences, item:Project, icon, active_data, active_propname):
        item.draw_line(context, layout)


class OP_blgd_add_project(Operator):
    bl_label = "Add Project"
    bl_idname = "blgd.ops_project_list_add"
    def execute(self, context):
        prefs = preferences(context)
        prefs.project_slots.add()
        prefs.project_selected = len(prefs.project_slots)+1
        return {"FINISHED"}

class OP_blgd_rem_project(Operator):
    bl_label = "Rem Project"
    bl_idname = "blgd.ops_project_list_rem"
    def execute(self, context):
        prefs = preferences(context)
        index = prefs.project_selected
        if index == -1:
            return
        prefs.project_slots.remove(index)
        prefs.project_selected = -1
        return {"FINISHED"}

class Preferences(AddonPreferences): 
    bl_idname = id_name
    
    project_slots : CollectionProperty(type=Project) #type:ignore
    project_selected : IntProperty() #type:ignore
    project_active : IntProperty() #type:ignore
    
    @property
    def active_project(self)->Project|None:
        if (self.project_active < 0) or (self.project_active > (len(self.project_slots)-1)) :
            return None
        return self.project_slots[self.project_active]
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.template_list("PROJECT_UL_regular", "", self, "project_slots", self, "project_selected")
        col = row.column()
        col.operator("blgd.ops_project_list_add")
        col.operator("blgd.ops_project_list_rem")

        if prj:=self.active_project:
            prj.draw_full(context, layout)

    @staticmethod
    def _on_save(context):
        self = preferences(context)
        self.find_active()
    @staticmethod
    def _on_load(context):
        self = preferences(context)
        self.find_active()
        self.reload
    @staticmethod
    def _on_close(context):
        self = preferences(context)
        for p in self.project_slots:
            p.module_slots.clear()
        
def preferences(context:Context)->Preferences:
    return context.preferences.addons[id_name].preferences
    

classes = [
    ModuleOption,
    MODULE_OPTION_UL_regular,
    ModuleVersion,
    MODULE_VERSION_UL_regular,
    Module,
    MODULE_UL_regular,
    Project,
    PROJECT_UL_regular,
    OP_blgd_add_project,
    OP_blgd_rem_project,
    Preferences,
]
    
def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)