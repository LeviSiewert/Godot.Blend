from __future__ import annotations
from .context import StructContext
from typing import Any

from collections import UserDict

class GdValue():
    ''' Base class for all writeable atomic values, prim for isinstance checking '''

class PropertyCollection(UserDict):
    context : StructContext
    overlay : PropertyCollection|None = None
    pinned : list[str]

    def __init__(self, iterable=tuple(), /, context:StructContext=None,):
        self.context = StructContext(extends=context)
        super().__init__(iterable)

    def __missing_key__(self, key)->Any:
        if not self.overlay is None:
            return self.overlay[key]
        raise KeyError
    def __setitem__(self, key, value):
        res = super().__setitem__(key, value)
        if not isinstance(key, str):
            raise TypeError("Property Collection Key must be str!")
        if (not isinstance(value, GdValue)) and isinstance(value, (dict, list)):
            raise TypeError("This object cannot intake base dicts or lists due to context object support. Use values.Dictionary or values.Array instead")
        if hasattr(value, "context"):
            value.context.set_extends(self.context)
        return res
        
    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("{}")})"