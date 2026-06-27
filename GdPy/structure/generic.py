from .core import GdType
from .core.property_collection import PropertyCollection

class GdObject(GdType):
    gdtype : str
    properties : PropertyCollection
    def __init__(self, gdtype, **kwargs):
        self.gdtype = gdtype
        self.properties = PropertyCollection(kwargs.items())

_all = (
    GdObject,
)