from __future__ import annotations

from typing import Type, Any
from .context import Context

class GdDefValue:
    base : Type = None
    contents_a : Type|Any = Any
    contents_b : Type|Any = Any

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