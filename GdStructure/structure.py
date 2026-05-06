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
    _project         : GdTypeProject = None
    _file            : GdTypeResourceFile = None
    
    metadata         : dict[str, GdTypeValue]
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
    def import_as_tres(self,context:dict, lines:list[str], as_file:bool=False)->Self: 
        assert(self._project != None)
        assert(self._file != None)
        ''' Import from lines of file '''
        context["resource"] = self

        if as_file:
            assert( self.header_matches(lines[0]) )
            self.import_header(lines.pop(0))

        _my_section = []
        _current_section = _my_section
        _switched = False
        _sections :list[list[str]] = []

        for line in lines:
            if line == "":
                continue
            if line.startswith("["):
                if (not _switched) and (line == "[resource]") and as_file:
                    ## Section that represents local data
                    continue
                _sections.append(_current_section)
                _current_section = [line]
            else:
                _current_section.append(line)

        for line in _my_section:
            self.import_as_property(context, line)

        for section in _sections:
            header : str = section[0]
            _type : GdTypeResource = self._project.find_subresource_class_from_header(header)
            val = _type(self._project, self._file)
            self.sub_resources.append(val)
            val.import_as_tres(context, section, False)

        if as_file:
            self.post_import(context)
        
        del context["resource"]


    @abstractmethod
    def import_header(self, context, line:str):...

    @abstractmethod
    def import_property(self, context, line):...

    def post_import(self, context:dict)->None: 
        ''' Hook up references here '''
        context["resource"] = self
        self._post_import(context)
        self._post_import_properties(context)
        self._post_import_metadata(context)
        self._determine_definition(context)
        self._post_import_subresources(context)
        del context["resource"]

    def _post_import(self, context:dict)->None:
        ''' work on sub-tree or sub-data construction here
        Ie node relationships '''

    def _post_import_properties(self, context:dict)->None:
        for k,v in self.properties.values():
            if v is GdTypeValueReference:
                context["property_id"] = k
                v.post_import(context)
        del context["property_id"]

    def _post_import_metadata(self, context:dict)->None:
        for k,v in self.metadata.values():
            if v is GdTypeValueReference:
                context["property_id"] = k
                v.post_import(context)
        del context["property_id"]

    def _post_import_subresources(self, context:dict)->None:
        for v in self.sub_resources:
            v.post_import(context)

    @abstractmethod
    def _get_definition_id(self,)->str:
        ''' If a script exists return that UID, if not then use the class name '''
        if self.properties.has("script"):
            return self.properties["script"]
        elif self.metadata.has("_custom_type_script"):
            return self.metadata["_custom_type_script"]

    def _determine_definition(self, context:dict)->GdDefinitionClass:
        ''' Determine the defintion that this object represents an instance of '''
        if self._project == None:
            return None
        self._project.definitions.get(self.get_definition_id()) 

    @abstractmethod
    def pre_export(self, context:dict):
        ''' Fetch references here w/a '''
        context["resource"] = self
        self._pre_export_properties(context)
        context["resource"] = None

    def _pre_export_properties(self, context:dict):
        for k,v in self.properties.values():
            if v is GdTypeValueReference:
                context["property_id"] = k
                v.post_import(context)

    @abstractmethod
    def export_header(self, context, line:str):...
    
    @abstractmethod
    def export_property(self, context, line):...

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
    uuid_map    : dict[str, GdTypeResourceFile]
    path_map    : dict[str, GdTypeResourceFile]
    definitions : dict[str, GdDefinitionClass] ## By all of UID, PATH, CLASS_NAME
