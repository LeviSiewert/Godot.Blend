import bpy
from pathlib import Path
from typing import Any

from ... import register, unregister

# def is_registered()->bool:
#     if not (bl_info["name"] in bpy.context.preferences.addons.keys()):
#         return False
#     return bpy.context.preferences.addons[bl_info["name"]]

# def _get_root_path()->str:
#     cf = Path(__file__).resolve()
#     for p in cf.parents:
#         if (p/"blender_manifest.toml").exists():
#             return str(p)
#     raise FileNotFoundError()

# def ensure_registered()->bool:
#     if not (bl_info["name"] in bpy.context.preferences.addons.keys()):
#         bpy.ops.wm.addon_install(overwrite=True, filepath=_get_root_path()+"__init__.py")
#     bpy.ops.wm.addon_enable(module=bl_info["name"])

# def ensure_unregistered()->bool:
#     if not (bl_info["name"] in bpy.context.preferences.addons.keys()):
#         return
#     bpy.ops.wm.addon_disable(module=bl_info["name"])


class BlenderPytest():
    @classmethod
    def setup_class(cls):
        register()

    @classmethod
    def teardown_class(cls):
        unregister()

class BlenderPytestAttr(BlenderPytest):
    ''' Provide a property of the given type on a scene for testing purposes
    self.get_attr & self.get_attr_loc are accessors
    '''
    attr_value : Any = bpy.props.StringProperty()
    attr_name : str = "test_attr"

    @classmethod
    def get_attr(cls):
        return getattr(bpy.data.scenes[0],cls.attr_name)

    @classmethod
    def get_attr_loc(cls)->tuple[Any,str]:
        return (bpy.data.scenes[0],cls.attr_name)

    @classmethod
    def setup_class(cls):
        super().setup_class()
        setattr(bpy.types.Scene,cls.attr_name, cls.attr_value)

    @classmethod
    def teardown_class(cls):
        delattr(bpy.types.Scene, cls.attr_name)
        super().teardown_class()