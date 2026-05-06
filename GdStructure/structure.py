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

### Direct Minimal Value types ###

class GdTypeValue(ABC, BaseModel):
    _value_add_quotations : bool = False
    
    value : Any

    def __init__(self, value:Any):
        if value is str:
            assert(self.can_convert_from_str(value))
            self.convert_fr_string(value)
        else:
            raise ValueError("Could not construct from type!", value.__class__)

    @classmethod
    @abstractmethod
    def can_convert_from_str(cls, target:str)->bool:
        pass

    @abstractmethod
    def convert_fr_string(self,val:str):
        pass
    
    @abstractmethod
    def convert_to_string(self,)->str:
        pass

    def __str__(self)->str:
        return self.convert_to_string()

class GdTypeValueImplicit(GdTypeValue):    
    ''' String representation of 'val'  '''

class GdTypeValueExplicit(GdTypeValue):
    ''' String representation of '_key(val)'  '''
    _key : str = "UNSET"

    @classmethod
    def can_convert_from_str(cls,val:str)->bool:
        return val.startswith(cls._key)
    
    @abstractmethod
    def convert_fr_string(self, val:str):
        pass
    
    @abstractmethod
    def convert_to_string(self,)->str:
        pass

class GdTypeValueReference(GdTypeValueImplicit):    
    ''' References dont contain a 'key("val")' representation, but may still be req to update like so '''
    _reference : GdTypeResource

    @abstractmethod
    def post_import(context:dict):
        ''' Connect references w/a '''

    @abstractmethod
    def pre_export(context:dict):
        ''' Connect references w/a '''


### Direct Minimal Resource types ###

class GdTypeResource(ABC):
    _header_id       : str = "_UNSET"     ## Header key, ie 'gd_scene'
    _header_contents : list[str] = []     ## what properties are exported to the header
    _references      : list[GdTypeValueReference]  ## References that point to self, consider as weakrefs
    _definition      : GdDefinitionClass  ## Class defintion for api.
    _project         : GdTypeProject 
    _file            : GdTypeResourceFile 
    
    properties       : dict[str, GdTypeValue]
    sub_resources    : list[GdTypeResource]

    def __init__(self, project:GdTypeProject, file:GdTypeResourceFile=None):
        self._project = project
        self._file = file

        self.properties    = {}
        self.sub_resources = []
        self._references   = []

    @classmethod
    def header_matches(cls, context:dict, header:str)->bool:
        ''' Determine if the input header string matches the current type '''
        return header.startswith("["+cls._header_id)

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
    _file = None

    def __init__(self, project:GdTypeProject):
        self._project = project
        
        self.properties    = {}
        self.sub_resources = []
        self._references   = []

    
class GdTypeProject():
    files       : list[GdTypeResourceFile]
    uuid_map    : dict[str,GdTypeResourceFile]
    path_map    : dict[str,GdTypeResourceFile]
    definitions : dict[str,GdDefinitionClass]
