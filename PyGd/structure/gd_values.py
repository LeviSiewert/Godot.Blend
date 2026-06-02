from __future__ import annotations
from .gd_type import *

''' Implementation of GdValue Structure '''


class _GdValueNull(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    _lark_key = "NULL"
    _primitive_types = [float]
    _primitive = True

    @classmethod
    def parse_lark(cls, tfm, child:Token)->Any:
        return None
    
class _GdValueFloat(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    _lark_key = "FLOAT"
    _primitive_types = [float]
    _primitive = True

    @classmethod
    def parse_lark(cls, tfm, child:Token)->Any:
        return float(child)

class _GdValueString(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    _lark_key = "STRING"
    _primitive_types = [float]
    _primitive = True

    @classmethod
    def parse_lark(cls, tfm, child:Token)->Any:
        return str(child).strip('"')

class _GdValueInteger(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    _lark_key = "NUMBER"
    _primitive_types = [int]
    _primitive = True

    @classmethod
    def parse_lark(cls, tfm, child:Token)->Any:
        return int(child)

class GdValueStringName(GdValue):
    _lark_key = "STRINGNAME"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"&')
        return inst
    
class GdValueArray(GdValue):
    value : list
    _lark_key = "array"
    _lark_key_explicit = "array_explicit"
    
    @classmethod
    def parse_lark(cls, tfm, meta, *children:list[Token|Any])->Any:
        inst = cls()
        inst.value = children
        return inst

    @classmethod
    def parse_lark_explicit(cls, tfm, meta, type, inst:GdValueArray)->Any:
        ## Explicit here is just a wrapper.
        inst.type = type
        return inst

class GdValueVector2(GdValueArray): 
    _lark_key = "vector2"
    _lark_key_explicit="" 
class GdValueVector3(GdValueArray): 
    _lark_key = "vector3"
    _lark_key_explicit="" 
class GdValueVector4(GdValueArray): 
    _lark_key = "vector4"
    _lark_key_explicit="" 
class GdValueVector2i(GdValueArray): 
    _lark_key = "vector2i"
    _lark_key_explicit="" 
class GdValueVector3i(GdValueArray): 
    _lark_key = "vector3i"
    _lark_key_explicit="" 
class GdValueVector4i(GdValueArray): 
    _lark_key = "vector4i"
    _lark_key_explicit="" 
class GdValueColor(GdValueArray): 
    _lark_key = "color"
    _lark_key_explicit="" 
class GdValueAABB(GdValueArray): 
    _lark_key = "aabb"
    _lark_key_explicit="" 
class GdValueQuaternion(GdValueArray): 
    _lark_key = "quaternion"
    _lark_key_explicit="" 
class GdValueTransform3D(GdValueArray): 
    _lark_key = "transform3d"
    _lark_key_explicit="" 
class GdValuePackedByteArray(GdValueArray): 
    _lark_key = "packedbytearray"
    _lark_key_explicit="" 
class GdValuePackedInt32Array(GdValueArray): 
    _lark_key = "packedint32array"
    _lark_key_explicit="" 
class GdValuePackedInt64Array(GdValueArray): 
    _lark_key = "packedint64array"
    _lark_key_explicit="" 
class GdValuePackedFloat32Array(GdValueArray): 
    _lark_key = "packedfloat32array"
    _lark_key_explicit="" 
class GdValuePackedFloat64Array(GdValueArray): 
    _lark_key = "packedfloat64array"
    _lark_key_explicit="" 
class GdValuePackedStringArray(GdValueArray): 
    _lark_key = "packedstringarray"
    _lark_key_explicit="" 
class GdValuePackedVector2Array(GdValueArray): 
    _lark_key = "packedvector2array"
    _lark_key_explicit="" 
class GdValuePackedVector3Array(GdValueArray): 
    _lark_key = "packedvector3array"
    _lark_key_explicit="" 
class GdValuePackedVector4Array(GdValueArray): 
    _lark_key = "packedvector4array"
    _lark_key_explicit="" 
class GdValuePackedColorArray(GdValueArray): 
    _lark_key = "packedcolorarray"
    _lark_key_explicit="" 


class _GdValueDictionaryPair(GdValue):
    _lark_key = "pair"
    def parse_lark(cls, meta, key, value)->Any:
        return tuple([key, value])

class GdValueDictionary(GdValue):
    value : dict
    _lark_key = "dictionary"
    _lark_key_explicit = "dictionary_explicit"
    
    @classmethod
    def parse_lark(cls, tfm, meta, *children:list[Token|Any])->Any:
        inst = cls()
        inst.value = dict()
        for x in children:
            if x is None: continue
            inst.value[x[0]] = x[1]
        return inst

    @classmethod
    def parse_lark_explicit(cls, tfm, meta, type, inst:GdValueDictionary)->Any:
        ## Explicit here is just a wrapper.
        inst.type = type
        return inst
        

class _packed_vector2(GdValueArray):
    _lark_key = "packed_vector2"
    _lark_key_explicit = ""
    @classmethod
    def parse_lark(cls, tfm, meta, *children):
        return children
class _packed_vector3(GdValueArray):
    _lark_key = "packed_vector3"
    _lark_key_explicit = ""
    def parse_lark(cls, tfm, meta, *children):
        return children
class _packed_vector4(GdValueArray):
    _lark_key = "packed_vector4"
    _lark_key_explicit = ""
    def parse_lark(cls, tfm, meta, *children):
        return children
class _packed_color(GdValueArray):
    _lark_key = "packed_color"
    _lark_key_explicit = ""
    def parse_lark(cls, tfm, meta, *children):
        return children