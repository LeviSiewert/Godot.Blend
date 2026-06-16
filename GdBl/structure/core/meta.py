
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty

class BlScene(PropertyGroup):
    is_reference_bin : BoolProperty(default=False) #type:ignore

_all = (
    BlScene,
)