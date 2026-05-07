from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Type, Any
from pydantic import BaseModel

class GdTypeVariant:
    ''' used as a passthrough for searching for other values, should ever be instanced '''
    pass


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
    _reference : Any #GdTypeResource

    @abstractmethod
    def post_import(context:dict):
        ''' Connect references w/a '''

    @abstractmethod
    def pre_export(context:dict):
        ''' Connect references w/a '''

## Explicit References ##

class NodePath(GdTypeValueExplicit, GdTypeValueReference):
    ''' Spacial node & optional property reference
    ie "" | "./../sibling_node:subvalue" '''
    _value_add_quotations = True
    _key : str = "NodePath"

class SubResourceRef(GdTypeValueExplicit, GdTypeValueReference):
    ''' refers to an ID defined in an sub_resource header
    ie SubResource("Sky_83rd1") '''
    _value_add_quotations = True
    _key : str = "SubResource"

class ExtResourceRef(GdTypeValueExplicit, GdTypeValueReference):
    ''' refers to an ID defined in an ext_resource header
    ie ExtResource("1_mxm6v") '''
    _value_add_quotations = True
    _key : str = "SubResource"

class FileResourceRef(GdTypeValueExplicit, GdTypeValueReference):
    ''' ie "res://..." or "uid://..." 
    uid is favored but both should technically be interchangable '''
    _value_add_quotations = True


## Implicit References ##

class StringFileResourceRef(GdTypeValueImplicit, GdTypeValueReference):
    ''' ie "res://..." or "uid://..." 
    uid is favored but both are interchangable. 
    '''
    _value_add_quotations = True


### Explicit Arrays ###


class String(GdTypeValueImplicit):
    _value_add_quotations : bool = True

class Float32(GdTypeValueImplicit):
    ...

class Integer32(GdTypeValueImplicit):
    ...

class Float64(GdTypeValueImplicit):
    ...

class Integer64(GdTypeValueImplicit):
    ...


### Explicit values:

class Dictionary(GdTypeValueExplicit):
    _key : str = "{"
    _key_type : Type[GdTypeValue|GdTypeVariant] = GdTypeVariant
    _val_type : Type[GdTypeValue|GdTypeVariant] = GdTypeVariant
    _value_add_quotations : bool = False
    
    def __init__(self, value:Any={}, key_type:Type=GdTypeVariant, val_type:Type=GdTypeVariant):
        self._key_type = key_type
        self._val_type = val_type
        
        if value is dict:
            pass
        elif value is str:
            pass

    class _DictionaryEntry(BaseModel):
        key : GdTypeValue
        val : GdTypeValue

class Array(GdTypeValueExplicit):
    _key : str = "["
    values : list[Any]
    _item_type : Type[GdTypeValue] = GdTypeVariant
    _value_add_quotations : bool = False
    
    def __init__(self, value:Any=[], item_type:Type=None):
        if item_type != None:
            self._item_type = item_type

        if value is list:
            if self.values != GdTypeVariant:
                for x in value:
                    assert(x is self._item_type)
            self.values = value
        else:
            super(value)

    def get_default(cls)->Type:
        return cls._item_type()

    def __getitem__(self, key:int):
        assert(key is int)
        if len(self.value) < key:
            value = self.get_default()
            self.values.append(value)
            return value
        return values[key]

    def __delitem__(self, key:int):
        assert(key is int)
        del self.values[key]

    def __setitem__(self, key:int, value:Any):
        assert(key is int)
        assert(value is self._item_type)
        self.values[key] = value

    def append(self,value:Any):
        return self.values.append(value)
        pass

    def clear(self,):
        return self.values.clear()

    def pop(self):
        return self.values.pop()
    
    def __iter__(self):
        return self.values.__iter__()

class _Array(Array):
    def __init__(self, value:Any=[]):
        super(value, None)

class Vector2(_Array):
    _key : str = "Vector2"
    _item_type : Type = Float64
class Vector3(_Array):
    _key : str = "Vector3"
    _item_type : Type = Float64
class Vector4(_Array):
    _key : str = "Vector4"
    _item_type : Type = Float64
class Vector2i(_Array):
    _key : str = "Vector2i"
    _item_type : Type = Integer64
class Vector3i(_Array):
    _key : str = "Vector3i"
    _item_type : Type = Integer64
class Vector4i(_Array):
    _key : str = "Vector4i"
    _item_type : Type = Integer64
class Quaternion(_Array):
    _key : str = "Quaternion"
    _item_type : Type = Float64
class Transform3D(_Array):
    _key : str = "Transform3D"
    _item_type : Type = Float64
class Color(_Array):
    _key : str = "Color"
    _item_type : Type = Float64
class AABB(_Array):
    _key : str = "AABB"
    _item_type : Type = Float64
class PackedByteArray(_Array):
    _key : str = "PackedByteArray"
    _item_type : Type = bytes
class PackedInt32Array(_Array):
    _key : str = "PackedInt32Array"
    _item_type : Type = int
class PackedInt64Array(_Array):
    _key : str = "PackedInt64Array"
    _item_type : Type = int
class PackedFloat32Array(_Array):
    _key : str = "PackedFloat32Array"
    _item_type : Type = float
class PackedFloat64Array(_Array):
    _key : str = "PackedFloat64Array"
    _item_type : Type = float
class PackedStringArray(_Array):
    _value_is_string_derivitve : bool = True
    _key : str = "PackedStringArray"
    _item_type : Type = str
class PackedVector2Array(_Array):
    _key : str = "PackedVector2Array"
    _item_type : Type = Vector2
class PackedVector3Array(_Array):
    _key : str = "PackedVector3Array"
    _item_type : Type = Vector3
class PackedVector4Array(_Array):
    _key : str = "PackedVector4Array"
    _item_type : Type = Vector4
class PackedColorArray(_Array):
    _key : str = "PackedColorArray"
    _item_type : Type = Color
