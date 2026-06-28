import bpy
from bpy.types import PropertyGroup, AddonPreferences
from bpy.props import StringProperty, CollectionProperty

from contextvars import ContextVar

from .core.types import _BlProject

class BlProjectItem(_BlProject):
    pass

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