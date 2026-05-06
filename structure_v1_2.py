from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Self
from pydantic import BaseModel
## Definition Types (for later hooking) ##

class GdDefinitionProperty(BaseModel):
    type : str
    hint : str
    default : str
    _default : GdTypeValue
    _value_type : GdTypeValue

class GdDefinitionClass(BaseModel):
    ''' Imported definition for internal classes and scripts '''
    extends : str
    _extends : GdDefinitionClass

    class_name : str
    properties: dict[str, GdDefinitionProperty]
    path : str
    uid : str

### Direct Minimal types:

class GdTypeValue(ABC):
    @abstractmethod
    def __str__()->str:
        pass

class GdTypeValueReference(GdTypeValue):    
    ''' FUTURE: References should contextually export differently based on various factors '''
    _reference : GdTypeResource


class GdTypeResource(ABC):
    _header_id       : str
    _header_contents : list[str] = []
    _references      : list[GdTypeValueReference]
    _project         : GdTypeProject
    _parent          : GdTypeResource

    properties    : dict[str, GdTypeValue]
    sub_resources : list[GdTypeResource]

    def __init__(self):
        self.properties    = {}
        self.sub_resources = []
        self._references   = []

    @staticmethod
    @abstractmethod
    def header_matches(context:dict, header:str)->bool:
        ''' Determine if the input header string matches the current type '''

    @staticmethod
    @abstractmethod
    def import_as_tres(context:dict, lines:list[str], as_file:bool=False)->Self: 
        ''' Import from lines of file '''

    @abstractmethod
    def determine_definition(self, context:dict)->GdDefinitionClass:
        ''' Determine the defintion that this object represents an instance of '''

    @abstractmethod
    def post_import(self, context:dict)->None: 
        ''' Hook up references here '''

    @abstractmethod
    def pre_export(self, context:dict):
        ''' Fetch references here w/a '''
    
    @abstractmethod
    def export_as_tres(self, context:dict, as_file:bool=False)->list[str]:
        ''' Export to file lines '''

    @abstractmethod
    def find_by_local_id(self)->list[str]:
        ''' Export to file lines '''


class GdTypeResourceFile(GdTypeResource):
    pass

class GdTypeProject():
    files       : list[GdTypeResourceFile]
    uuid_map    : dict[str,GdTypeResourceFile]
    path_map    : dict[str,GdTypeResourceFile]
    definitions : dict[str,GdDefinitionClass]

### Implimentation:

class GdTypeResourceFileTres(GdTypeResourceFile):
    _header_id       = "gd_resource"
    _header_contents = ["format", "uid"]
    type : str      ## base internal type.
    format : int    ## int denoting version
    uid : str       ## uid://

class GdTypeResourceFileTscn(GdTypeResourceFile):
    _header_id       = "gd_scene"
    _header_contents = ["format", "uid"]
    format : int    ## int denoting version
    uid : str       ## uid://
    _path : str     ## res://

class GdTypeSubResource(GdTypeResource):
    _header_id = "sub_resource"
    _header_contents = ["type", "id"]

class GdTypeSubResourceNode(GdTypeSubResource):
    _header_id = "node"
    _header_contents = ["name", "type", "parent", "id", "unique_id"]
    
    name : str
    type : str
    unique_id: int
    node_paths : list[str]
    parent : str
    
    _children : list[GdTypeSubResourceNode]

class GdTypeSubResourceExternal(GdTypeSubResource):
    _header_id = "ext_resource"
    type : str
    uid : str
    path : str
    id : str

class GdTypeSubResourceEditable(GdTypeSubResource):
    _header_id = "editable"
    path : str
