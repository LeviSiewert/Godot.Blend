from __future__ import annotations
from .primitives import Collection, Signal, SignalContainer
from .file_db import File
from typing import Any

class GdSignalDef():
    pass

class GdPropertyDef():
    """ 
    Minimum defintion of a GD property
    Secondary transformers: 
        - Will be a part of a standard per-env file
    """

    name : str
    default : Any
    typeing : tuple


class GdClassDef(SignalContainer):
    """ 
    Minimum defintion of a GD script|class
    Populated from the results of a scraping script. Function held within GdProject class
    Secondary transformers: 
        - env filtered integrations from a different module, 
        - env will be filtered via extension of a file, ie "script.gd.bl.py" 
        - File will matched by any of (name, uuid, path)
    """

    def_updated : Signal
    upstream_def_updated : Signal

    name : str
    name_set : Signal[str, str]
    
    uuid : str
    uuid_set : Signal[str, str]
    
    path : str
    path_set : Signal[str, str]
    
    extends : str
    _extends : GdClassDef
    _extends_me : list[GdClassDef]
    extends_set : Signal[GdClassDef]

    # is_internal : bool

    is_abstract : str
    language : str

    _properties : dict[str,GdPropertyDef]
    _signals : dict[str,GdSignalDef]

    @property
    def parents(self)->tuple[GdClassDef]:
        if self._extends:
            return self._extends.parents | (self._extends,)
        else:
            return tuple()

    @property
    def children(self)->list[GdClassDef]:
        res = []
        for x in self._extends_me:
            res.append(x)
            res.extend(x.children)
        return res 

    @property
    def properties(self,)->dict[GdPropertyDef]:
        if self._extends:
            return self._properties | self._extends.properties
        else:
            return self._properties
    
    def __init__(self, properties:list[GdPropertyDef]):
        self._extends_me = []
        self._properties = {}
        for x in properties:
            self._properties[x.name] = x
        super().__init__()
        self.upstream_def_updated.connect(self.def_updated)

    def set_extends(self, val:GdClassDef, is_bulk:bool=False):
        if self._extends:
            self._extends._extends_me.remove(self)
            self._extends.upstream_def_updated.disconnect(self.upstream_def_updated.forward)
        self._extends = val

        if val:
            val._extends_me.append(self)
            val .upstream_def_updated.connect(self.upstream_def_updated.forward)
        
        if not is_bulk:
            self.definition_updated()

class ClassDb[T:GdClassDef](Collection):
    src_file : File #FileClassDefinition

    by_name: dict[str, T]
    by_uuid: dict[str, T]
    by_path: dict[str, T]

    def __init__(self):
        self.by_name = {}
        self.by_uuid = {}
        self.by_path = {}
        super().__init__()

    def _integrate(self, item:T):
        if item.name: self.by_name[item.name] = item
        if item.uuid: self.by_uuid[item.uuid] = item
        if item.path: self.by_path[item.path] = item
    
    def _disintegrate(self, item:T):
        if item in self.by_name.values(): del self.by_name[item.name]
        if item in self.by_uuid.values(): del self.by_uuid[item.uuid]
        if item in self.by_path.values(): del self.by_path[item.path]

    def __getitem__(self, key)->T:
        return self.by_uuid.get(key, self.by_path.get(key, self.by_name.get(key, None)))
    
    def set_inheritance_chain(self,):

        for x in self.items:
            if not x.extends: 
                continue
            x.set_extends(self[x.extends], True)

        for x in self.items:
            x.def_updated()

    def set_src_file(self, file:File):
        if self.file:
            self.file.data_loaded.disconnect(self.load_fr_src_file)
        self.file = file
        file.data_loaded.connect(self.load_fr_src_file)
        self.load_fr_src_file()
    
    def load_fr_src_file(self):
        for x in self.file.get_definitions():
            self.append(x)
        