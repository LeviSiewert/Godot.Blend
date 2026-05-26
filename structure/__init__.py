from __future__ import annotations
from typing import Any, Type
from ..primitives import *
from lark.visitors import Transformer, v_args
from lark import Token

from typing import List
## This structure is the minimum defintion of how a file should be parsed
## THe goal is to have a generic read into tree structure, then dynamically expand the definitions away from the base types.
## Once I am strucutrally correct, I will switch to a strict definition.

class GdTypeAnnoation():
    ''' To be expanted on later; will need to incorperate refs by UUID, ect '''
    type : Type
    def __init__(self, type:Type):
        self.type = type
    def __repr__(self):
        return f"<{self.type.__name__}>"
STRING = GdTypeAnnoation(str)
VARIANT = GdTypeAnnoation(Any)
NULL = GdTypeAnnoation(None)

class GdType():
    _all_types : list[Type] = []
    _lark_key     : str  = "__default__" ##Lark key && Function key
    _lark_key_explicit = ""
    _raw_children : list[Any]

    @classmethod
    def parse_lark(cls, tfm, meta, children)->Any:
        if len(children) == 0: 
            return None
        inst = cls()
        inst._raw_children = children
        return inst
    
    @staticmethod 
    def generate_parser(func)->Callable:
        ''' Required due to python's problem with lambda namespaces in loops '''
        def parser(*args):
            return func(*args)
        return parser

    @classmethod        
    def generate_transformer(cls)->Type[Transformer]:
        ## Construct a parser class and return it
        class _Transformer(Transformer):
            pass
        for x in cls._all_types:
            if hasattr(_Transformer, x._lark_key) and (x._lark_key != ""):
                raise Exception("Tranformer already has key populated", x._lark_key)

            if x._lark_key:
                setattr(_Transformer, x._lark_key, cls.generate_parser(x.parse_lark))

            if x._lark_key_explicit:
                setattr(_Transformer, x._lark_key_explicit, cls.generate_parser(x.parse_lark_explicit))
        
        return v_args(meta=True, inline=True)(_Transformer)
    

    def __init_subclass__(cls):
        cls._all_types.append(cls)

    def __init__(self):
        _raw_children = []

    def __repr__(self)->str:
        return self.__class__.__name__ + "()"

    # def print_tree(self, indent:int=0, insert:str=""):
    #     print(" " * indent, insert, self)
    #     for x in self._raw_children:
    #         if x is GdType:
    #             x.print_nested(indent+1, "|-")
    #         else:
    #             print(" "*indent+1, insert, x)

class GdResource(GdType):
    _lark_key = "resource"

class GdTyping(GdType):
    _lark_key = "type"
    value : list

    @classmethod
    def parse_lark(cls, tfm, meta, type_a:Token=None, type_b:Token=None)->Any:
        inst = cls()
        inst.value = [type_a, type_b]
        return inst

class GdProperty(GdType):
    _lark_key = "property"
    name : str
    value : Any
    
    @classmethod
    def parse_lark(cls, tfm, meta, name:Token, value=None)->Any:
        inst = cls()
        inst.name = name.value
        inst.value = value
        if inst.value is list:
            inst.value = inst.value[0]
        return inst
    
    def __repr__(self)->str:
        return f"{self.__class__.__name__} ( {self.name} = {self.value} )" 


class GdValue(GdType):
    _has_typing : bool = False
    _lark_key = "value"
    
    typing : tuple[GdTypeAnnoation|GdType] = (VARIANT,)
    value  : Any = None

    def __init__(self, value=None,type=None):
        _raw_children = []
        if value != None:
            self.set_value(value)
        if type != None:
            self.set_type(type)

    def __repr__(self):
        if self._has_typing:
            return f"{self.__class__.__name__}[{self.typing}]({self.value})"
        return f"{self.__class__.__name__}({self.value})"
    
    @classmethod
    def parse_lark(cls, tfm, meta, *children:list[Token|Any])->Any:
        ''' "Thin" by default'''
        return children
    
    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return (self.value == value.value) and (self.typing == value.typing)
        return super().__eq__(value)


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

class GdValueExtResource(GdValue):
    _has_typing = True
    _lark_key = "extresource"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
class GdValueNodePath(GdValue):
    _lark_key = "nodepath"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
class GdValueSubResource(GdValue):
    _lark_key = "subresource"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst

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

class GdValueVector2(GdValueArray): _lark_key_explicit="" ; _lark_key = "vector2"
class GdValueVector3(GdValueArray): _lark_key_explicit="" ; _lark_key = "vector3"
class GdValueVector4(GdValueArray): _lark_key_explicit="" ; _lark_key = "vector4"
class GdValueVector2i(GdValueArray): _lark_key_explicit="" ; _lark_key = "vector2i"
class GdValueVector3i(GdValueArray): _lark_key_explicit="" ; _lark_key = "vector3i"
class GdValueVector4i(GdValueArray): _lark_key_explicit="" ; _lark_key = "vector4i"
class GdValueColor(GdValueArray): _lark_key_explicit="" ; _lark_key = "color"
class GdValueAABB(GdValueArray): _lark_key_explicit="" ; _lark_key = "aabb"
class GdValueQuaternion(GdValueArray): _lark_key_explicit="" ; _lark_key = "quaternion"
class GdValueTransform3D(GdValueArray): _lark_key_explicit="" ; _lark_key = "transform3d"
class GdValuePackedByteArray(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedbytearray"
class GdValuePackedInt32Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedint32array"
class GdValuePackedInt64Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedint64array"
class GdValuePackedFloat32Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedfloat32array"
class GdValuePackedFloat64Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedfloat64array"
class GdValuePackedStringArray(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedstringarray"
class GdValuePackedVector2Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedvector2array"
class GdValuePackedVector3Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedvector3array"
class GdValuePackedVector4Array(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedvector4array"
class GdValuePackedColorArray(GdValueArray): _lark_key_explicit="" ; _lark_key = "packedcolorarray"


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
    @classmethod
    def parse_lark(cls, tfm, meta, *children):
        return children
class _packed_vector3(GdValueArray):
    _lark_key = "packed_vector3"
    def parse_lark(cls, tfm, meta, *children):
        return children
class _packed_vector4(GdValueArray):
    _lark_key = "packed_vector4"
    def parse_lark(cls, tfm, meta, *children):
        return children
class _packed_color(GdValueArray):
    _lark_key = "packed_color"
    def parse_lark(cls, tfm, meta, *children):
        return children


gd_value_types : list[Type[GdValue]] = filter(lambda x: issubclass(x, GdValue), GdType._all_types)

# class GdValueArrayPacked(GdValueArray):
#     pass