import bpy
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty
from .property_collection import BlPropertyCollection

from .core.types import _BlSubResource, _BlSubResourceCollection


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

_all = (
    BlSubResource,
    BlCatResource,
    BlExtResource,
    BlEditResource,
    BlNodeResource,
    BlSubResourceCollection,
    BlCatResourceCollection,
    BlExtResourceCollection,
    BlEditResourceCollection,
    BlNodeResourceCollection,
) 