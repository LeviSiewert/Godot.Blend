from . import property_collection 
from . import sub_resources
from . import resources
# from . import file
# from . import project

import bpy

_all = (
    *property_collection._all,
    *sub_resources._all,
    *resources._all,
    # *file._all,
    # *project._all,
)

def register():
    for c in _all:
        bpy.utils.register_class(c)
    # bpy.types.Collection.gd = bpy.props.PointerProperty(type=resources.BlTscnOnCollection)
    # bpy.types.Text.gd = bpy.props.PointerProperty(type=file.BlFileCollection)
    # bpy.types.Object.gd = bpy.props.PointerProperty(type=sub_resources.BlNodeResource)

def unregister():
    for c in reversed(_all):
        bpy.utils.unregister_class(c)
    # del bpy.types.Text.gd
    # del bpy.types.Collection.gd
    # del bpy.types.Object.gd