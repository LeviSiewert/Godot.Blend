import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import PointerProperty, StringProperty, BoolProperty
from .sub_resources import BlSubResourceCollection, BlExtResourceCollection, BlNodeResourceCollection, BlEditResourceCollection, BlCatResourceCollection

from .core.types import _BlResource

class BlTscn(_BlResource):
    ## Ontop of collection
    # node_resources : PointerProperty(type=BlNodeResourceCollection) #type:ignore
    root_node : StringProperty() #type:ignore
    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore
    edit_resources : PointerProperty(type=BlEditResourceCollection) #type:ignore

class BlTres(_BlResource):
    sub_resources : PointerProperty(type=BlSubResourceCollection) #type:ignore
    ext_resources : PointerProperty(type=BlExtResourceCollection) #type:ignore

class BlSettings(_BlResource):
    cat_resources : PointerProperty(type=BlCatResourceCollection) #type:ignore

class BlProjectSettings(_BlResource):
    cat_resources : PointerProperty(type=BlCatResourceCollection) #type:ignore

_all = (
    BlTscn,
    BlTres,
    BlSettings,
    BlProjectSettings,
    # BlTscnOnCollection,
)