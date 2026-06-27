from .core import GdType
from .core.property_collection import PropertyCollection

class GdObject(GdType):
    gdtype : str
    properties : PropertyCollection
    def __init__(self, gdtype, **kwargs):
        self.gdtype = gdtype
        self.properties = PropertyCollection(kwargs.items())

    def __eq__(self, value):
        if isinstance(value, GdObject):
            return all((
                value.gdtype == self.gdtype,
                value.properties == self.properties,
            ))
        return super().__eq__(value)
    
    def __repr__(self):
        return f"Object({self.gdtype}, {self.properties.items})"

_all = (
    GdObject,
)