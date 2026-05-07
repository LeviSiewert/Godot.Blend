from __future__ import annotations
from pydantic import BaseModel
from .structure_values import GdTypeValue

class GdDefinitionProperty(BaseModel):
    ## PLANNED : Make as a Resource type for easier extraction from godot
    type : str
    hint : str
    default : str
    _default : GdTypeValue
    _value_type : GdTypeValue

class GdDefinitionClass(BaseModel):
    ''' Imported definition for internal classes and scripts '''
    ## PLANNED : Make as a Resource type for easier extraction from godot
    extends : str
    class_name : str
    properties: dict[str, GdDefinitionProperty]
    uid : str

    _extends : GdDefinitionClass
    _handlers : dict[str, GdHandler]

class GdHandler(ABC):
    ''' Inheritable class for controlling the conversion between a host application and this structure '''
    program : str
    uid : str

class ProgramHandlerEntry():
    program_id : str = ""
    handlers : list[GdHandler]

    ## CACHE:
    _by_uid : dict[str, GdHandler]
    _by_res : dict[str, GdHandler]
    _by_class_name : dict[str, GdHandler]

    def __init__(self, program_id:str):
        self.program_id = program_id

    def append(self,val:GdHandler):
        self.handlers.append(val)
        if val.uid:
            self._by_uid[val.uid] = val
        if val.res:
            self._by_res[val.res] = val
        if val.class_name:
            self._by_class_name[val.class_name] = val

    def find_class_handler(self, cls:GdDefinitionClass)->GdHandler:
        by_class_name = self.by_class_name.get(cls.class_name, None) 
        if by_class_name: return by_class_name
        by_res = self._by_res.get(cls.res, None)
        if by_res: return by_res
        by_uid = self._by_uid.get(cls.uid, None)
        if by_uid: return by_uid

        if cls._extends:
            return self.find_class_handler(cls._extends)
        else:
            raise LookupError()

class ProgramHandlerDb():
    _entries : dict[str, ProgramHandlerEntry]
    def __init__(self):
        self._entries = {}
    
    def append(self, entry:ProgramHandlerEntry):
        self._entries[entry.program_id] = entry

    def __getitem__(self, key:str)->ProgramHandlerEntry:
        for x in self._entries:
            if x.program_id == key:
                return x
        return None

    def __setitem__(self, key:str, value:GdHandler):
        for x in self._entries:
            if x.program_id == key:
                x.append(value)
        _inst = ProgramHandlerEntry(key)
        _inst.append(value)
        self._entries[key] = _inst

        return None


class ClassDb():
    ''' Holds all class definitions and handlers '''
    classes : list[GdDefinitionClass]
    handlers: ProgramHandlerDb
    
    _by_uid : dict[str, GdDefinitionClass]
    _by_res : dict[str, GdDefinitionClass]
    _by_class_name : dict[str, GdDefinitionClass]

    def __init__(self):
        self._by_uid = {}
        self._by_res = {}
        self._by_class_name = {}
        self.classes = []
        self.handlers = ProgramHandlerDb()

    def append(self,item: GdDefinitionClass):
        self.classes.append(item)
        if item.class_name:
            self._by_class_name[item.class_name] = item
        if item.uid:
            self._by_uid[item.uid] = item
        if item.res:
            self._by_res[item.res] = item