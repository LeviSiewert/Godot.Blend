from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Type
from __future__ import annotations

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
    type_key : str
    type_val : str
    default : GdTypeValue
    ## Class references used for drawing, reqs, similar:
    _expects_type : GdTypeValue  
    _type_key : GdTypeValue
    _type_val : GdTypeValue


class GdTypeDefScript(GdTypeDef):
    ''' Minimized version of a script, only requirements
    Planned to be hookable for blender draw, import and export.
    '''
    ## Technically should be a resource as it is in godot mem, but no
    extends : GdTypeDefScript
    class_name : str
    path : str
    uid : str
    properties : dict[str,GdTypeDefProperty]

## Base Types ##

class GdType(ABC, BaseModel):
    pass

## Value Types ##


class GdTypeValue(GdType):
    @abstractmethod
    def matches_string(string:str)->bool: pass
    @abstractmethod
    def import_string(context:dict, string:str): pass 
    @abstractmethod
    def export_string(context:dict)->str: pass

class GdTypeValueImplicit(GdTypeValue):
    
    pass

class String(GdTypeValueImplicit):
    """ Basic string type """

class StringName(String):
    ''' Subtype of string starting with &
    Benefits from defered referencing, joining
    '''

class StringUid(String):
    ''' Subtype of string starting with uid:// 
    Benefits from defered referencing, joining
    '''

class StringRes(String):
    ''' Subtype of string starting with res:// 
    Benefits from defered referencing, joining
    '''

class StringLID(String):
    ''' Subtype of string that is a local resource ID 
    Defered generation, callback 
    '''

class StringEID(String):
    ''' Subtype of string that is an external resource ID 
    Defered generation, callback 
    '''


class Float32(GdTypeValueImplicit):
    pass

class Integer32(GdTypeValueImplicit):
    pass

class Float64(GdTypeValueImplicit):
    pass

class Integer64(GdTypeValueImplicit):
    pass

class Array(GdTypeValueImplicit):
    _val_type = Type = Any

    def typed(self, val_type:Type):
        self._val_type = val_type

class DictionaryEntry(BaseModel):
    key : Any
    val : Any
class Dictionary(GdTypeValueImplicit):
    _key_type = Type = Any
    _val_type = Type = Any
    entries : Array[DictionaryEntry]
    
    def typed(self, key_type:Type, val_type:Type):
        _key_type = key_type
        _val_type = val_type


class GdTypeValueExplicit(GdTypeValue):
    """ Explicit value that follows the covention of f'{_key}("{value:_type}")' """
    _is_string_derivitve : bool = False
    
    def matches_string(self, string:str)->bool: 
        return string.startswith(self._key)
    
    def _strip_string_val(self, string:str)->str:
        if self._is_string_derivitve:
            return string[len(self._key):-2]
        else:
            return string[len(self._key):-1].strip('"')
        
    def _wrap_string_val(self, string:str)->str:
        if not self._is_string_derivitve:
            return f'{self._key}({string})'
        else:
            return f'{self._key}("{string}")'

class GdResourceReference(GdTypeValueExplicit):
    ''' Deffered value-generation callback for read-write as these values are structure dependent '''
    ## Convert references elsewhere

    @abstractmethod
    def import_reference(context:Dictionary): 
        ''' Called after import, use to generate value reference '''

    @abstractmethod
    def export_reference(context:Dictionary): 
        ''' Called after structure & key generation, pre-export '''

class GdTypeValueExplicitArray(GdTypeValueExplicit):
    _key : str ## Key for this object's type for type matching
    _type : Type ## Value type
    value : list[Any]
    _seperater : str = ","
    _is_string_derivitve = False
    _value_is_string_derivitve : bool = False

    def _strip_string_values(self, strings:list[str])->str:
        if not self._value_is_string_derivitve:
            return strings
        else:
            _strings : list[str] = []
            for x in strings:
                _strings.append(x.strip('"'))
            return _strings

    def _wrap_string_values(self, strings:list[str])->str:
        if self._value_is_string_derivitve:
            _strings : list[str] = []
            for x in strings:
                _strings.append(f'"{x}"')
            return self._wrap_string_val(self._seperater.join(_strings))
        else:
            return self._wrap_string_val(self._seperater.join(strings))
        

class Vector2(GdTypeValueExplicitArray):
    _key : str = "Vector2"
    _type : Type = Float64
    value : list[Float64]
class Vector3(GdTypeValueExplicitArray):
    _key : str = "Vector3"
    _type : Type = Float64
    value : list[Float64]
class Vector4(GdTypeValueExplicitArray):
    _key : str = "Vector4"
    _type : Type = Float64
    value : list[Float64]
class Vector2i(GdTypeValueExplicitArray):
    _key : str = "Vector2i"
    _type : Type = Integer64
    value : list[Integer64]
class Vector3i(GdTypeValueExplicitArray):
    _key : str = "Vector3i"
    _type : Type = Integer64
    value : list[Integer64]
class Vector4i(GdTypeValueExplicitArray):
    _key : str = "Vector4i"
    _type : Type = Integer64
    value : list[Integer64]
class Quaternion(GdTypeValueExplicitArray):
    _key : str = "Quaternion"
    _type : Type = Float64
    value : list[Float64]
class Transform3D(GdTypeValueExplicitArray):
    _key : str = "Transform3D"
    _type : Type = Float64
    value : list[Float64]
class Color(GdTypeValueExplicitArray):
    _key : str = "Color"
    _type : Type = Float64
    value : list[Float64]
class AABB(GdTypeValueExplicitArray):
    _key : str = "AABB"
    _type : Type = Float64
    value : list[Float64]
class PackedByteArray(GdTypeValueExplicitArray):
    _key : str = "PackedByteArray"
    _type : Type = bytes
    value : list[bytes]
class PackedInt32Array(GdTypeValueExplicitArray):
    _key : str = "PackedInt32Array"
    _type : Type = int
    value : list[int]
class PackedInt64Array(GdTypeValueExplicitArray):
    _key : str = "PackedInt64Array"
    _type : Type = int
    value : list[int]
class PackedFloat32Array(GdTypeValueExplicitArray):
    _key : str = "PackedFloat32Array"
    _type : Type = float
    value : list[float]
class PackedFloat64Array(GdTypeValueExplicitArray):
    _key : str = "PackedFloat64Array"
    _type : Type = float
    value : list[float]
class PackedStringArray(GdTypeValueExplicitArray):
    _value_is_string_derivitve : bool = True
    _key : str = "PackedStringArray"
    _type : Type = str
    value : list[str]
class PackedVector2Array(GdTypeValueExplicitArray):
    _key : str = "PackedVector2Array"
    _type : Type = Vector2
    value : list[Vector2]
class PackedVector3Array(GdTypeValueExplicitArray):
    _key : str = "PackedVector3Array"
    _type : Type = Vector3
    value : list[Vector3]
class PackedVector4Array(GdTypeValueExplicitArray):
    _key : str = "PackedVector4Array"
    _type : Type = Vector4
    value : list[Vector4]
class PackedColorArray(GdTypeValueExplicitArray):
    _key : str = "PackedColorArray"
    _type : Type = Color
    value : list[Color]


class NodePath(GdResourceReference):
    _is_string_derivitve = True
    _key : str = "NodePath"
class ExtResourceRef(GdResourceReference):
    _is_string_derivitve = True
    _key : str = "ExtResource"
class SubResourceRef(GdResourceReference):
    _is_string_derivitve = True
    _key : str = "SubResource"
    

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
    path : StringRes ## res://...
    uid : StringUid ## uid://...
    id : StringEID ## local short id, ie 10_rlxyv
    _file : GdTypeFile

class GdTypeSubResource(GdTypeSubObject):
    ''' Generic Sub Resource '''
    _header_id : str = "sub_resource"
    _type_definition : GdTypeDefScript
    type : str ## Godot's integrated base type 
    id : StringLID ## file's local resource id

class GdTypeEditable(GdTypeSubObject):
    ''' Reference/flag that an object is a local overwrite '''
    _header_id : str = "editable"
    
    path : StringRes
    _ext_resource : ExtResourceRef

class GdTypeNode(GdTypeSubObject):
    ''' Generic Node Type '''
    _header_id : str = "node"

    type : str ## Name of ibuilt node type.
    name : str ## Name of node. Only unique in peers
    parent : str ## Path relative to scene root. if "." this is the root
    index : str  ## str(int), index in parent. TODO: May allow special flags (first, last, ect)
    uid : StringUid  ## uuid:// ...
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
