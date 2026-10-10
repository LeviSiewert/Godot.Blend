from __future__ import annotations

import bpy

from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty
from contextvars import ContextVar

from ..addon_config import bl_info, id_name
from ..GdPy.core.structure import Project as GdProject
from ..GdPy.core.wrapped_fsspec import LocalFileSystem


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
    title : StringProperty(name="name", get=_get_title, set=_set_title) #type:ignore
    root : StringProperty(name="path", subtype="FILE_PATH") #type:ignore
    desc : StringProperty(name="desc") #type:ignore

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

    def _get_title(self):
        title = self.get("title",None)
        return title if title else self.name
    def _set_title(self, val):
        self["title"] = val

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
        
        a_prj = active_project()
        if not (a_prj is None) and (a_prj.name == self.name):
            layout.label(text = "@")
        else:
            layout.label(text = " ")
        
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
        # options = row.operator("blgd.ops_modules", text="reload")
        # options.path = self.root.strip(".godot") + "/" + self.modules_path.strip("res://")
        # options = row.operator("blgd.ops_modules", text="save")
        
        layout.template_list("MODULE_UL_regular", "", self, "module_slots", self, "module_selected")

        if (len(self.module_slots)-1) >= self.module_selected:
            self.module_slots[self.module_selected].draw_full(context, layout)
    
    @staticmethod
    def draw_header_container(context:Context, layout:UILayout):
        if prj:=active_preferences().active_project:
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
    def is_active(self):
        prj = active_preferences().project_python.get() 
        if prj is None:
            return False
        fs : LocalFileSystem
        fs.path         

    def _on_activate(self):
        ''' Construct project '''
        prefs = active_preferences()
        if prefs is None:
            return
        ctx_py_project = prefs.project_python
        # if ctx_py_project.get():
            # ctx_py_project.get().close()
        # Load types
        ctx_py_project.set(
            GdProject(
                fs = LocalFileSystem(self.root),
                # type_file = self.classes_path.split("res:/")[-1] if self.classes_path else None,
            )
        )


class PROJECT_UL_regular(bpy.types.UIList):
    def draw_item(self, context, layout, data:Preferences, item:Project, icon, active_data, active_propname):
        item.draw_line(context, layout)


class OP_blgd_add_project(Operator):
    bl_label = "Add Project"
    bl_idname = "blgd.ops_project_list_add"
    def execute(self, context):
        prefs = active_preferences()
        prefs.project_slots.add()
        prefs.project_selected = len(prefs.project_slots)
        return {"FINISHED"}

class OP_blgd_rem_project(Operator):
    bl_label = "Rem Project"
    bl_idname = "blgd.ops_project_list_rem"



class Preferences(AddonPreferences): 
    bl_idname = id_name
    
    project_slots : CollectionProperty(type=Project) #type:ignore
    project_selected : IntProperty() #type:ignore
    project_active : EnumProperty(items=get_projects_enum, update=_on_project_enum_update, default=-1) #type:ignore
    project_python : ContextVar[GdProject|None] = ContextVar("GdPy.Preferences.project_python", default=None) 
    ## Populated and maintained by Project when activated.

    def get_projects_enum(self, context:Context)->list[tuple]:
        return [
            (-1,"<None>",""),
            *((i, p.title, p.desc) for i,p in enumerate(self.project_slots) if (p.name != "")),
        ]
    
    def _on_project_enum_update(self, context):
        if self.project_selected == -1 or (self.project_selected < (len(self.project_slots)-1)):
            return
        self.project_slots[self.project_active]._on_activate()

    @property
    def selected_project(self)->Project|None:
        if self.project_selected == -1 or (self.project_selected < (len(self.project_slots)-1)):
            return None
        return self.project_slots[self.project_selected]
    
    @property
    def active_project(self)->Project|None:
        if self.project_selected == -1 or (self.project_selected < (len(self.project_slots)-1)):
            return None
        for p in self.project_slots:
            if self.project_active == p.root:
                return p
        return None
        # return self.project_slots[self.project_active]
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self,"project_active")
        layout.label(text=self.project_active)

        row = layout.row()
        row.template_list("PROJECT_UL_regular", "", self, "project_slots", self, "project_selected")
        col = row.column()
        col.operator("gdpy.project_io")
        col.operator("gdpy.project_io")

        if prj:=self.selected_project:
            prj.draw_full(context, layout)


    @staticmethod
    def _on_save(context):
        self = active_preferences()
        self.find_active()
    @staticmethod
    def _on_load(context):
        self = active_preferences()
        self.find_active()
        self.reload
    @staticmethod
    def _on_close(context):
        self = active_preferences()
        for p in self.project_slots:
            p.module_slots.clear()

def active_preferences()->Preferences:
    return bpy.context.preferences.addons[id_name].preferences

def active_project()->Project|None:
    return active_preferences().active_project
    
def active_gdproject()->GdProject|None:
    return active_preferences().project_python.get()
    

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