from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Self, Generator, Iterable, Any
from pydantic import BaseModel
from .structure_definitions import *
from .structure_values import GdTypeValue, GdTypeValueReference
from ..primitives import Signal
## Definition Types (for later hooking) ##

### Direct Minimal Value types ###


### Direct Minimal Resource types ###

SUBRESOURCE_SORT_ORDER : list[str] = [
    ## TSCN
    "ext_resource",
    "sub_resource",
    "node",
    "editable",

    ## project.godot
    "application",
    "input",
    "physics",
    "rendering",
]

class GdTypeResource(ABC):
    _header_id       : str = "_UNSET"     ## Header key, ie 'gd_scene'
    _generates_header      : bool = True
    _header_contents : list[str] = []     ## what properties are exported to the header
    _references      : list[GdTypeValueReference]  ## References that point to self, consider as weakrefs
    _definition      : GdDefinitionClass  ## Class defintion for api.
    _project         : GdTypeProject = None
    _file            : GdTypeResourceFile = None
    
    _use_resource_section : bool = False

    type             : str
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
        ## TODO: Does not yet accomidate expanded/implicit header such as in projects.godot
        #  
        assert(self._project != None)
        assert(self._file != None)
        ''' Import from lines of file '''
        context["resource"] = self

        if as_file and self._generates_header:
            assert( self.header_matches(lines[0]) )
            self.import_header(lines.pop(0))

        _my_section = []
        _current_section = _my_section
        _sections :list[list[str]] = []

        for line in lines:
            if line == "":
                continue
            if line.startswith("["):
                if (line == "[resource]"):
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

    def import_header(self, line:str):  
        ''' Import values in header to values on this object 
        Ie : [gd_resource type="AnimationNodeBlendTree" format=3 uid="uid://d1qo8u4mjospu"]
        '''

        words = self._split_header(line)
        assert(words.pop(0) == self._header_id)

        for line in words:
            k,v = self._import_property(line)
            assert(k in self._header_contents)
            self.set(k,v)

    @staticmethod
    def _split_header(line:str)->list[str]:
        line = line.strip("[]")
        _in_string : bool = False
        _in_value : bool = False
        
        words : list[str] = []
        for l in line:
            _word : str = ""
            if (l in "\'\""):
                _in_string = not _in_string
            elif (l in "\(\)") and (not _in_string):
                _in_value = not _in_value
            elif (l == " ") and (len(_word) != 0) and (not _in_value) and (not _in_string):
                words.append(_word)
                continue
            else:
                _word =+ l
        words.append(_word)
        return words

    def import_property(self, line:str):
        ''' Import string as a dict[str,val] to self.properties or self.metadata 
        Override if subobjects-subproperties are expected 
        '''

        k,v = self._import_property(line)

        if k.startswith("metadata/"):
            self.metadata[k[9:-1]] = v 
        else:
            self.properties[k] = v 

    def _import_property(self, line:str)->tuple[str, GdTypeValue]:
        k,v = line.split("=")
        k = k.strip()
        v = v.strip()

        _type = self._project.find_value_class_from_string(v)
        val = _type(v)
        return k, val

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
        pass

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
        else:
            return self.type

    def _determine_definition(self, context:dict)->GdDefinitionClass:
        ''' Determine the defintion that this object represents an instance of '''
        if self._project == None:
            return None
        self._project.definitions.get(self.get_definition_id()) 

    ## Pre Export / Export prep ##

    def pre_export(self, context:dict):
        ''' Fetch references here w/a '''
        context["resource"] = self
        self._pre_export(context)
        self._pre_export_properties(context)
        self._pre_export_metadata(context)
        self._pre_export_sub_resources(context)
        context["resource"] = None
    
    def _pre_export(self, context:dict):
        pass

    def _pre_export_properties(self, context:dict):
        for k,v in self.properties.values():
            if v is GdTypeValueReference:
                context["property_id"] = k
                v.pre_import(context)

    def _pre_export_metadata(self, context:dict):
        for k,v in self.metadata.values():
            if v is GdTypeValueReference:
                context["property_id"] = k
                v.pre_import(context)

    def _pre_export_subresources(self, context:dict):
        for v in self.sub_resources:
            v._pre_export(context)

    ## Export Helpers ##

    def get_exported_header(self, context:dict)->str:
        return f'[{self._header_id} {" ".join(self._iter_export_header_values)}]'

    def _iter_export_header_values(self, use_spaces:bool=False)->Generator:
        for k in self._header_contents:
            value = self.get(k)
            if value == None: continue
            yield self._export_property(k, value, use_spaces)

    def get_exported_properties(self, context:dict)->list[str]:
        properties : list[str] = [] 
        for x in self._iter_export_property_values():
            properties.append(x)

    def _iter_export_property_values(self, use_spaces:bool=True)->Generator:
        for k,v in self.properties.values():
            yield self._export_property(k,v,use_spaces)
        for k,v in self.metadata.values():
            yield self._export_property("metadata/"+k,v,use_spaces)

    def export_property(self, context, key:str, value:GdTypeValue)->str:
        return self._export_property(key, value)

    @staticmethod
    def _export_property(k:str,v:GdTypeValue,use_spaces:bool=True):
        if use_spaces:
            return f'{k} = {str(v)}'
        return f'{k}={str(v)}'
        
    ## Export itself ##

    @abstractmethod
    def export_as_tres(self, context:dict, as_file:bool=False)->list[str]:
        ''' Export to file lines '''
        # TODO: This does not account super neatly for project.godot's slightly different format that uses [sections], loose properties and no primary header

        context["resource"] = self

        _header : Iterable[str]
        if self._generates_header:
            _header : list[str] = [self.get_exported_header(context), ""]
        else:
            _header = self._iter_export_header_values()
            

        _properties : Generator = self._iter_export_property_values()
        _sub_resources : Generator = self._iter_export_sub_resources(context)
        
        lines = [_header, ""]

        if as_file and self._use_resource_section:
            lines.append("[resource]")
        
        lines.extend(_properties)
        lines.append("")

        for section in _sub_resources:
            lines.extend(section)
            lines.append("")
        
        del context["resource"]
    
        return lines

    def _iter_export_sub_resources(self,context:dict)->Generator:
        _sorted = self.sub_resources.sorted(lambda x: SUBRESOURCE_SORT_ORDER.index(x.header_id) )
        
        
        for x in _sorted:
            yield x.export_as_tres(context, False)

    @abstractmethod
    def get_by_local_res_id(self, path:str)->GdTypeResource:
        pass

class GdTypeResourceFile(GdTypeResource):
    _file = None

    def __init__(self, project:GdTypeProject):
        self._project = project
        
        self.properties    = {}
        self.sub_resources = []
        self._references   = []


class FileDb():
    ''' Holds all tscn, tres & asset files '''
    files : list[GdTypeResourceFile]
    _by_uid : dict[str, GdTypeResourceFile]
    _by_res : dict[str, GdTypeResourceFile]

    def __init__(self):
        self.files = []
        self._by_uid = {}
        self._by_res = {}

    def append(self,item: GdDefinitionClass):
        self.classes.append(item)
        if item.uid:
            self._by_uid[item.uid] = item
        if item.res:
            self._by_res[item.res] = item

    
class GdTypeProject():
    classes : ClassDb
    files : FileDb

    def __init__(self):
        self.files = FileDb()
        self.classes = ClassDb()