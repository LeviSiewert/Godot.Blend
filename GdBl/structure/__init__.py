
# from . import core 

# import bpy
# from bpy.props import PointerProperty

# from .. import property_collection, sub_resource

# from . import pointer_collection
# from . import resource, meta, file, project

# _all = (
#     *pointer_collection._all,
#     *property_collection._all, 
#     *sub_resource._all, 
#     *resource._all, 
#     *meta._all, 
#     *file._all, 
#     *project._all
# )

# def register():
#     for c in _all:
#         bpy.utils.register_class(c)
#     bpy.types.Text.gd = PointerProperty(type=file.BlFileCollection)
#     bpy.types.Collection.gd = PointerProperty(type=resource.BlTscnOnCollection)
#     bpy.types.Scene.gd = PointerProperty(type=meta.BlScene)
#     bpy.types.Object.gd = PointerProperty(type=sub_resource.BlNodeResource)

# def unregister():
#     for c in reversed(_all):
#         bpy.utils.unregister_class(c)
#     del bpy.types.Text.gd
#     del bpy.types.Scene.gd
#     # del bpy.types.Collection.gd
#     del bpy.types.Object.gd