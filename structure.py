from pydantic import BaseModel
from abc import ABC, abstractmethod

## Definition Types ##

class GdTypeDef(ABC, BaseModel):
    @abstractmethod
    def matches_string(string:str)->bool: pass

class GdTypeDefProperty(GdTypeDef):
    ''' Minimized version of a property, only requirements
    Planned to be hookable for blender draw, import and export.
    '''
    key : str
    expects_type : str
    _expects_type : GdTypeValue ## Used for drawing


class GdTypeDefScript(GdTypeDef):
    ''' Minimized version of a script, only requirements
    Planned to be hookable for blender draw, import and export.
    '''
    ## Technically should be a resource as it is in godot mem, but no
    extends : GdTypeDefScript
    class_name : str
    
    path : str
    uid : str

    expected_properties : dict[str,GdTypeDefProperty]

## Types:

class GdType(ABC, BaseModel):
    pass

## Value Types:

class GdTypeValue(GdType):
    value : str

    @abstractmethod
    def matches_string(string:str)->bool: pass
    @abstractmethod
    def import_string(context:dict, string:str): pass 
    @abstractmethod
    def export_string(context:dict)->str: pass

class UidString(GdTypeValue):
    pass

class ResString(GdTypeValue):
    pass


class Float(GdTypeValue):
    pass
class Integer(GdTypeValue):
    pass

class Dictionary(GdTypeValue):
    pass

class Transform3D(GdTypeValue):
    pass

class Vector2(GdTypeValue):
    pass
class Vector3(GdTypeValue):
    pass
class Vector4(GdTypeValue):
    pass

class Vector2i(GdTypeValue):
    pass
class Vector3i(GdTypeValue):
    pass
class Vector4i(GdTypeValue):
    pass

class Quaternion(GdTypeValue):
    pass

class _GdResourceReference(GdTypeValue):
    pass

class PackedStringArray(GdTypeValue):
    pass
class PackedBytArray(GdTypeValue):
    pass

class NodePath(_GdResourceReference):
    pass
class ExtResourceRef(_GdResourceReference):
    pass
class SubResourceRef(_GdResourceReference):
    pass

## Objects: 

class GdTypeProperty(GdType):
    name : str
    value : GdTypeValue

    @abstractmethod
    def import_string(): pass 
    @abstractmethod
    def export_string()->str: pass 

class GdTypeSection(GdType):
    properties : list[GdTypeProperty]

class GdTypeSubObject(GdTypeSection):
    header_name : str
    _type_definition : GdTypeDef

    @abstractmethod
    def matches_header(): ...
    @abstractmethod
    def import_header(): ...
    @abstractmethod
    def export_header(): ...

    @abstractmethod
    def import_body_lines(): ...
    @abstractmethod
    def export_body_lines(): ...

class GdTypeExtResource(GdTypeSubObject):
    ''' Reference to external file '''
    _header_id : str = "ext_resource"

    type : str ## Script | PackedScene | ...
    path : str ## res://...
    uid : str ## uid://...
    id : str ## local short id, ie 10_rlxyv
    _file : GdTypeFile

class GdTypeSubResource(GdTypeSubObject):
    ''' Generic Sub Resource '''
    _header_id : str = "sub_resource"
    _type_definition : GdTypeDefScript
    type : str ## Godot's integrated base type 
    id : str ## file's resource id

class GdTypeEditable(GdTypeSubObject):
    ''' Reference/flag that an object is a local overwrite '''
    _header_id : str = "editable"
    
    path : str
    _ext_resource : ExtResourceRef

class GdTypeNode(GdTypeSubObject):
    ''' Generic Node Type '''
    _header_id : str = "node"

    type : str ## Name of ibuilt node type.
    name : str ## Name of node. Only unique in peers
    parent : str ## Path relative to scene root. if "." this is the root
    index : str  ## str(int), index in parent. TODO: May allow special flags (first, last, ect)
    uid : UidString  ## uuid:// ...
    unique_id : int  ## TODO: Exact purpose unknown. Perhaps runtime inst?
    instance : ExtResourceRef ## if !null, this is an instance of this external resource's file
    node_paths : PackedStringArray ## Array of all property names that are NodePath instances

    _parent : GdTypeNode
    _children : GdTypeNode

    _inst_editable : GdTypeEditable
        ## Value overrides may be stored here

## File Types ##

class GdTypeFile(GdType):
    _header_id : str
    _last_updated : int
    _reference_only : bool
    
    @abstractmethod
    def matches_header(): ...
    @abstractmethod
    def import_header(): ...
    @abstractmethod
    def export_header(): ...

    @abstractmethod
    def import_body_lines(): ...
    @abstractmethod
    def export_body_lines(): ...


class GdTypeFileResource(GdTypeFile):
    ''' resource.tres '''
    _header_id : str = "gd_scene"
    type : int
    format : int
    uid : UidString
    properties : list[GdTypeProperty]
    sub_resources : list[GdTypeSubObject] ## All other included objects

class GdTypeFileTscn(GdTypeFile):
    ''' scene.tscn | escn '''
    _header_id : str = "gd_scene"
    format : int
    uid : UidString
    sub_resources : list[GdTypeSubObject] ## All other included objects

class GdTypeFileProject(GdTypeFile):
    ''' project.godot '''
    path : str

    properties : list[GdTypeProperty]
    sections : list[GdTypeSection]


## Project management ##

class GdTypeProject():
    ''' Entire project representation, UID mapping, File management, ect '''
    
    pass
