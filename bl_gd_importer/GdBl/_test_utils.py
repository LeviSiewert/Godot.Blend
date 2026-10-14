import bpy

from ..addon_config import id_name, addon_path, flag_testing, flag_debug

def is_addon_registered()->bool:
    return (id_name in bpy.context.user_preferences.addons)

def addon_ensure(registered:bool):
    if is_addon_registered() == registered:
        return
    elif registered:
        addon_register()
    else:
        addon_unregister()

def addon_register():
    bpy.ops.preferences.addon_install(filepath=addon_path)
    bpy.ops.preferences.addon_enable(module=id_name)
    assert is_addon_registered()

def addon_unregister():
    bpy.ops.preferences.addon_disable(module=id_name)
    bpy.ops.preferences.addon_remove(module=id_name)
    assert not is_addon_registered()