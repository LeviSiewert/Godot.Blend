import bpy
from ... import register, unregister, bl_info
# from ..structure.blcore import BlProjects


from pathlib import Path

# def is_registered()->bool:
#     if not (bl_info["name"] in bpy.context.preferences.addons.keys()):
#         return False
#     return bpy.context.preferences.addons[bl_info["name"]]

def _get_root_path()->str:
    cf = Path(__file__).resolve()
    for p in cf.parents:
        if (p/"blender_manifest.toml").exists():
            return str(p)
    raise FileNotFoundError()

# def ensure_registered()->bool:
#     if not (bl_info["name"] in bpy.context.preferences.addons.keys()):
#         bpy.ops.wm.addon_install(overwrite=True, filepath=_get_root_path()+"__init__.py")
#     bpy.ops.wm.addon_enable(module=bl_info["name"])

# def ensure_unregistered()->bool:
#     if not (bl_info["name"] in bpy.context.preferences.addons.keys()):
#         return
#     bpy.ops.wm.addon_disable(module=bl_info["name"])

class TestRegistration():
    @classmethod
    def setup_class(cls):
        register()

    @classmethod
    def teardown_class(cls):
        unregister()
    
    def test_primary(self):
        assert(hasattr(bpy.types, BlProjects.__name__))
        
    