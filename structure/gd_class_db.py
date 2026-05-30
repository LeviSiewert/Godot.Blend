from __future__ import annotations
from typing import Any 
from ..primitives import Collection

class PropertyDef():
    default_value : Any
    type : str
    hint_str : str
    hint_type : int
    usage : int

class ResourceDef():
    ## Constructed | Inheritable | Hookable
    _extends : ResourceDef
    extends : str
    name : str
    uuid : str
    path : str
    properties : dict[str, PropertyDef]

class ClassDb(Collection):
    pass