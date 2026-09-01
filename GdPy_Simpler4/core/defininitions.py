from __future__ import annotations

from typing import Type, Any
from .context import Context

class GdDefValueTyping:
    contents_a : str|GdDefType|Type|Any|None = Any
    contents_b : str|GdDefType|Type|Any|None = Any

    def __init__(self, contents_a=None, contents_b=None):
        self.contents_a = contents_a
        self.contents_b = contents_b

class GdDefValue:
    base : Type = None

class GdDefProperty:
    context : Context
    name : str
    value : GdDefValue|Any = Any
    ...

class GdDefSignal:
    context : Context
    ...

class GdDefType:
    extends : GdDefType|None = None
    context : Context
