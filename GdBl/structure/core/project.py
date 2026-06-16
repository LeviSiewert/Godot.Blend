import bpy
from bpy.types import PropertyGroup, AddonPreferences
from bpy.props import StringProperty, CollectionProperty

from contextvars import ContextVar

class BlProjectItem(PropertyGroup):
    name : StringProperty(name="Name") #type:ignore
    filepath : StringProperty(name="project_dir", subtype="DIR_PATH")# help="Project directory, should have project.godot directly inside") #type:ignore
    #Discovered Scripts here as well?

class BlProjects(PropertyGroup):
    items = CollectionProperty(type = BlProjectItem)

class Preferences(AddonPreferences):
    bl_idname = __package__

    projects : CollectionProperty(type = BlProjects) #type:ignore
    active_project : ContextVar = ContextVar("GdProject")

_all = (
    BlProjectItem,
    BlProjects,
    Preferences,
)