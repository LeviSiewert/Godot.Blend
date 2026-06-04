from __future__ import annotations
from typing import Any

class GdPropertyDef():
    name : str
    default : Any

class GdClassDef():
    ''' '''
    name : str
    uuid : str
    path : str
    extends : str
    is_internal : bool

    _extends : GdClassDef
    _properties : dict[str,GdPropertyDef]

    @property
    def properties(self,)->dict[GdPropertyDef]:
        if self._extends:
            return self._properties | self._extends.properties
        else:
            return self._properties
        
class ClassDb():
    items : list[GdClassDef]