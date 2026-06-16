from .core import TransformerModule

from bpy.props import StringProperty
from ....GdPy.structure.values import GdValueStringName

class TrfmString(TransformerModule):
    @classmethod
    def get_gdbl_keys(cls):
        return (StringProperty,GdValueStringName,str)
    
    def to_blender(self, key, c, gd_item, _children):
        return str(gd_item)

    def fr_blender(self, key, c, bl_item, _children):
        return str(bl_item)

_all = (
    TrfmString,
    )