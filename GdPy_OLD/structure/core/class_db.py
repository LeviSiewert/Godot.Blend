from __future__ import annotations
from .primitives import Collection, Signal, SignalContainer
from .file_db import File
from typing import Any, Self
from abc import ABC, abstractmethod

class GdPropertyDef():
    """ 
    Minimum defintion of a GD property
    Secondary transformers: 
        - Will be a part of a standard per-env file
    """
    default_value : Any
    cls_name  : str
    _type     : int
    hint_type : int
    hint_str  : str
    usage     : int

    @staticmethod
    def construct(
            cls,
            default_value : Any,
            cls_name  : str,
            _type     : int,
            hint_type : int,
            hint_str  : str,
            usage     : int,
        )->Self:
        self = cls()
        self.default_value = default_value
        self.cls_name  = cls_name 
        self._type     = _type    
        self.hint_type = hint_type
        self.hint_str  = hint_str 
        self.usage     = usage    
        return self

class GdSignalDef():
    args         : list[dict]
    default_args : list
    flags        : int
    _id          : int
    name         : str
    
    def construct(cls,
            args         : list[dict],
            default_args : list,
            flags        : int,
            _id          : int,
            name         : str,
            )->Self:
        self = cls()
        self.args         = args
        self.default_args = default_args
        self.flags        = flags
        self._id          = _id
        self.name         = name
        return self

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

    @staticmethod
    def construct(
            cls,
            name : str,
            path : str,
            c_extends : str = "",
            properties : list[GdPropertyDef] = tuple(),
            signals : list[GdSignalDef] = tuple(),
            is_abstract : bool = False,
            language : str = "gdscript",
            )->Self:
        self = cls()
        self.name = name
        self.path = path
        self.extends = c_extends
        self.is_abstract = is_abstract
        self.langauge = language
        self._properties = properties
        self._signals = signals
        return self

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
    src_file : File = None#FileClassDefinition

    gd_project : Any

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
        if self.src_file:
            self.src_file.data_loaded.disconnect(self.load_fr_src_file)
        self.src_file = file
        file.data_loaded.connect(self.load_fr_src_file)
    
    def load_fr_src_file(self, context):
        if (self.src_file.data is None):
            self.src_file.load(context)
        for x in self.src_file.get_definitions():
            self.append(x)

class ClassDbEnforcable(ABC,SignalContainer):
    class_def : GdClassDef
    script_def : GdClassDef

    defintion_updated : Signal 

    def set_class_def(self, definition:GdClassDef):
        self.class_def = definition
        self.defintion_updated()

    def set_script_def(self, definition:GdClassDef):
        self.script_def = definition
        self.defintion_updated()

    @abstractmethod
    def validate(self):
        pass