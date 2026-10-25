import bpy

from collections import UserDict, UserList, UserString

class Promise(bpy.types.PropertyGroup):
    p_type : bpy.props.EnumProperty(items = [
        ("SUBRESOURCE","subresource",""),
        ("EXTRESOURCE","extresource",""),
        ("EXTRESOURCE_DIRECT","extresource_direct",""), #Refereing to promise in scope, W/out address, uid, ect
        ("RID","rid",""),
    ]) #type:ignore
    id : bpy.props.StringProperty() #type:ignore
    uid : bpy.props.StringProperty() #type:ignore
    filepath : bpy.props.StringProperty() #type:ignore

    ptr_col : bpy.props.PointerProperty(type=bpy.types.Collection) #type:ignore
    ptr_obj : bpy.props.PointerProperty(type=bpy.types.Object) #type:ignore
    ptr_tex : bpy.props.PointerProperty(type=bpy.types.Texture) #type:ignore
    ptr_img : bpy.props.PointerProperty(type=bpy.types.Image) #type:ignore
    ptr_mat : bpy.props.PointerProperty(type=bpy.types.Material) #type:ignore
    ptr_txt : bpy.props.PointerProperty(type=bpy.types.Text) #type:ignore
    ptr_scn : bpy.props.PointerProperty(type=bpy.types.Scene) #type:ignore
    ptr_snd : bpy.props.PointerProperty(type=bpy.types.Sound) #type:ignore
    ptr_lgt : bpy.props.PointerProperty(type=bpy.types.Light) #type:ignore
    ptr_cam : bpy.props.PointerProperty(type=bpy.types.Camera) #type:ignore
    ptr_mesh : bpy.props.PointerProperty(type=bpy.types.Mesh) #type:ignore
    ptr_clip : bpy.props.PointerProperty(type=bpy.types.Action) #type:ignore
    ptr_curv : bpy.props.PointerProperty(type=bpy.types.Curve) #type:ignore
    ptr_geon : bpy.props.PointerProperty(type=bpy.types.NodeTree) #type:ignore
    ptr_wrld : bpy.props.PointerProperty(type=bpy.types.World) #type:ignore
    # ptr_anim : bpy.props.PointerProperty(type=bpy.types.AnimData) #type:ignore

classes = [
    Promise,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        for l,n in getattr(c, "attach", tuple()):
            setattr(l, n, bpy.props.PointerProperty(type=c))
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        for l,n in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)