import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, PointerProperty, BoolProperty

## Project Structure:
# from ....GdPy import GdProject

from contextvars import ContextVar
class BlProjectItem(PropertyGroup):
    name : StringProperty(name="Name") #type:ignore
    filepath : StringProperty(name="project_dir", subtype="DIR_PATH")# help="Project directory, should have project.godot directly inside") #type:ignore
    #Discovered Scripts here as well?

class BlProjects(PropertyGroup):
    items = CollectionProperty(type = BlProjectItem)
    active_project : ContextVar = ContextVar("GdProject")


class BlScene(PropertyGroup):
    is_reference_bin : BoolProperty(default=False) #type:ignore


class BlProperty(PropertyGroup):
    type : StringProperty() #type:ignore
    name : StringProperty() #type:ignore
    value : StringProperty() #type:ignore

class _BlSubResource(PropertyGroup):
    properties : CollectionProperty(type = BlProperty) #type:ignore
class _BlSubResourceCollection(PropertyGroup):
    pass

class BlSubResource(_BlSubResource):
    pass
class BlSubResourceCollection(_BlSubResourceCollection):
    items = CollectionProperty(type = BlSubResource) #type:ignore

class BlCatResource(_BlSubResource):
    pass
class BlCatResourceCollection(_BlSubResourceCollection):
    items = CollectionProperty(type = BlCatResource) #type:ignore

class BlExtResource(_BlSubResource):
    pass
class BlExtResourceCollection(_BlSubResourceCollection):
    items = CollectionProperty(type = BlExtResource) #type:ignore

class BlEditResource(_BlSubResource):
    pass
class BlEditResourceCollection(_BlSubResourceCollection):
    items = CollectionProperty(type = BlEditResource) #type:ignore

class BlNodeResource(_BlSubResource):
    pass
class BlNodeResourceCollection(_BlSubResourceCollection):
    items = CollectionProperty(type = BlNodeResource) #type:ignore


class _BlFile(PropertyGroup):
    ''' File representation '''
    filepath : StringProperty() #type:ignore

class BlTscn(_BlFile):
    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore
    node_resources : PointerProperty(type=BlNodeResourceCollection) #type:ignore
    edit_resources : PointerProperty(type=BlEditResourceCollection) #type:ignore

class BlTres(_BlFile):
    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore

class BlSettings(_BlFile):
    cat_resources : PointerProperty(type=BlCatResourceCollection) #type:ignore


_all = (
        BlProjectItem,
        BlProjects,
        BlScene,
        BlProperty,
        BlSubResource,
        BlExtResource,
        BlEditResource,
        BlNodeResource,
        BlCatResource,
        BlSubResourceCollection,
        BlExtResourceCollection,
        BlEditResourceCollection,
        BlNodeResourceCollection,
        BlCatResourceCollection,
        BlTscn,
        BlTres,
        BlSettings,
    )

# _reg = bpy.utils.register_classes_factory(_all)

def register():
    for c in _all:
        bpy.utils.register_class(c)
    bpy.types.Object.Gd = PointerProperty(type=BlNodeResource)

def unregister():
    for c in reversed(_all):
        bpy.utils.unregister_class(c)