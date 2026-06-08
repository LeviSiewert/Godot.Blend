from __future__ import annotations
from .core import GdResource, GdType, GdValue, Signal
from typing import Self, Type, Any
from lark import Token #type: ignore 

## PRIMITIVES

class _GdValueInf(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("INF",)

    @classmethod
    def parse_lark(cls, key:str, tfm, child:Token)->Any:
        return float("inf")

class _GdValueNull(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("NULL",)

    @classmethod
    def parse_lark(cls, key:str, tfm, child:Token)->Any:
        return None
    
class _GdValueFloat(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("FLOAT",)

    @classmethod
    def parse_lark(cls, key:str, tfm, child:Token)->Any:
        return float(child)

class _GdValueString(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("STRING",)
    
    @classmethod
    def parse_lark(cls, key:str, tfm, child:Token)->Any:
        return str(child).strip('"')

class _GdValueInteger(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("NUMBER",)

    @classmethod
    def parse_lark(cls, key:str, tfm, child:Token)->Any:
        return int(child)

class GdValueStringName(GdValue):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("STRINGNAME",)

    @classmethod
    def parse_lark(cls, key:str, tfm, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"&')
        return inst
        
    def set_value(self, value):
        self.value = str(value)

class GdValueArray(GdValue):
    value : list
    types : tuple[Type[GdValue|Any]]

    item_appended : Signal
    item_removed : Signal
    
    def __init__(self, val:Any=None, types:tuple=None):
        if not (types is None):
            self.types = types
        if val != None:
            self.set_value(val)
        else:
            self.value = []

    def set_types(self, types:tuple[Type[GdValue|Any]]):
        self.types = types

    def set_value(self, value):
        self.value = []
        for x in value:
            self.append(x)

    def append(self, item:Any):
        if self.types:
            assert(isinstance(item,self.types))
        self.value.append(item)
        self.item_appended(item)
        
    def remove(self, item:Any):
        self.value.remove(item)
        self.item_removed(item)

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("array","array_explicit")
    
    @classmethod
    def parse_lark(cls, key:str, *args, **kwargs)->Any:
        if key == "array":
            return cls._parse_implicit(*args, **kwargs)
        elif key == "array_explicit":
            return cls._parse_explicit(*args, **kwargs)
        else:
            raise Exception("Could not determine key", key)

    @classmethod
    def _parse_explicit(cls, tfm, meta, key, int_array:GdValueArray):
        return int_array
    
    @classmethod
    def _parse_implicit(cls, tfm, meta, *children:list[Token|Any]):
        pass
        inst = cls()
        inst.value = children
        return inst

class _inherit_GdValueArray(GdValueArray):
    def __init__(self, val:Any=None):
        super().__init__(val)

class GdValueVector2(_inherit_GdValueArray):
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector2",)
class GdValueVector3(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector3",)
class GdValueVector4(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector4",)
class GdValueVector2i(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector2i",)
class GdValueVector3i(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector3i",)
class GdValueVector4i(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector4i",)
class GdValueRect2(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("rect2",)
class GdValueRect2i(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("rect2i",)
class GdValuePlane(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("plane",)
class GdValueColor(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("color",)
class GdValueAABB(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("aabb",)
class GdValueQuaternion(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("quaternion",)
class GdValueTransform2D(_inherit_GdValueArray):
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("Transform2d",)
class GdValueBasis(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("basis",)
class GdValueTransform3D(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("transform3d",)
class GdValuePackedByteArray(_inherit_GdValueArray): 
    types = (int,str)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedbytearray",)
class GdValuePackedInt32Array(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedint32array",)
class GdValuePackedInt64Array(_inherit_GdValueArray): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedint64array",)
class GdValuePackedFloat32Array(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedfloat32array",)
class GdValuePackedFloat64Array(_inherit_GdValueArray): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedfloat64array",)
class GdValuePackedStringArray(_inherit_GdValueArray): 
    types = (str,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedstringarray",)
class GdValuePackedVector2Array(_inherit_GdValueArray): 
    types = (GdValueVector2,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedvector2array",)
class GdValuePackedVector3Array(_inherit_GdValueArray): 
    types = (GdValueVector3,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedvector3array",)
class GdValuePackedVector4Array(_inherit_GdValueArray): 
    types = (GdValueVector4,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedvector4array",)
class GdValuePackedColorArray(_inherit_GdValueArray): 
    types = (GdValueColor,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedcolorarray",)


class _GdValueDictionaryPair(GdValue):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("pair",)
    @classmethod
    def parse_lark(cls, key:str, meta, pre, value)->Any:
        return tuple([pre, value])

class GdValueDictionary(GdValue):
    value : dict
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("dictionary","dictionary_explicit")
    
    @classmethod
    def _parse_lark(cls, key:str, *args, **kwargs)->Any:
        if key == "dictionary":
            return cls._parse_implicit(*args, **kwargs)
        elif key == "dictionary_explicit":
            return cls._parse_explicit(*args, **kwargs)
        else:
            raise Exception("Cannot find key", key)

    @classmethod
    def _parse_implicit(cls, tfm, meta, *children:list[Token|Any])->Any:
        inst = cls()
        inst.value = dict()
        for x in children:
            if x is None: continue
            inst.value[x[0]] = x[1]
        return inst
    
    @classmethod
    def _parse_explicit(cls, tfm, meta, int_dict:Self)->Any:
        return int_dict
        
class _packed_vector2(GdValueArray):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packed_vector2",)
    @classmethod
    def parse_lark(cls, key:str, tfm, meta, *children):
        return children

class _packed_vector3(GdValueArray):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packed_vector3",)
    @classmethod
    def parse_lark(cls, key:str, tfm, meta, *children):
        return children

class _packed_vector4(GdValueArray):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packed_vector4",)
    @classmethod
    def parse_lark(cls, key:str, tfm, meta, *children):
        return children

class _packed_color(GdValueArray):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packed_color",)
    @classmethod
    def parse_lark(cls, key:str, tfm, meta, *children):
        return children

_all : tuple[Type] = (
    _GdValueInf,
    _GdValueNull,
    _GdValueFloat,
    _GdValueString,
    _GdValueInteger,
    GdValueStringName,
    GdValueArray,
    GdValueVector2,
    GdValueVector3,
    GdValueVector4,
    GdValueVector2i,
    GdValueVector3i,
    GdValueVector4i,
    GdValueRect2,
    GdValueRect2i,
    GdValuePlane,
    GdValueColor,
    GdValueAABB,
    GdValueQuaternion,
    GdValueBasis,
    GdValueTransform2D,
    GdValueTransform3D,
    GdValuePackedByteArray,
    GdValuePackedInt32Array,
    GdValuePackedInt64Array,
    GdValuePackedFloat32Array,
    GdValuePackedFloat64Array,
    GdValuePackedStringArray,
    GdValuePackedVector2Array,
    GdValuePackedVector3Array,
    GdValuePackedVector4Array,
    GdValuePackedColorArray,
    _GdValueDictionaryPair,
    GdValueDictionary,
    _packed_vector2,
    _packed_vector3,
    _packed_vector4,
    _packed_color,
)