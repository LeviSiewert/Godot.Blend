from __future__ import annotations
from .context import StructContext
from typing import Any

class PropertyCollection(dict):
    context : StructContext
    overlay : PropertyCollection|None = None
    pinned : list[str]

    def __new__(cls, *args, **kwargs):
        self = super().__new__(*args, **kwargs)
        self.context = StructContext()

    def __missing_key__(self, key)->Any:
        if not self.overlay is None:
            return self.overlay[key]
        raise KeyError
    def __setitem__(self, key, value):
        res = super().__setitem__(key, value)
        if hasattr(value, "context"):
            value.context.set_extends(self.context)
        return res