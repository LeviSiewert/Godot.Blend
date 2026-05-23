from typing import Any, Type
from ..primitives import *
from lark.visitors import Transformer, v_args
from lark import Token

from typing import List
## This structure is the minimum defintion of how a file should be parsed
## THe goal is to have a generic read into tree structure, then dynamically expand the definitions away from the base types.
## Once I am strucutrally correct, I will switch to a strict definition.

class GdType():
    _all_types : list[Type] = []
    _lark_key     : str  = "__default__" ##Lark key && Function key
    _lark_key_explicit = ""
    
    _raw_children : list[Any]

    @classmethod
    def parse_lark(cls, meta, children)->Any:
        if len(children) == 0: 
            return None
        inst = cls()
        inst._raw_children = children
        return inst
    
    @staticmethod 
    def generate_parser(func)->Callable:
        def parser(*args):
            if len(args) == 1:
                return func(None, args[0])
            return func(*args)
        return parser

    @classmethod        
    def generate_transformer(cls)->Type[Transformer]:
        ## Construct a parser class and return it
        @v_args(meta=True)
        class _Transformer(Transformer):
            pass
        for x in cls._all_types:
            
            if hasattr(_Transformer, x._lark_key):
                raise Exception("Tranformer already has key populated", x._lark_key)
            if x._lark_key:
                setattr(_Transformer, x._lark_key, cls.generate_parser(x.parse_lark))
            if x._lark_key_explicit:
                setattr(_Transformer, x._lark_key, cls.generate_parser(x.parse_lark_explicit))
        
        return _Transformer
    
    def print_tree(self, indent:int=0, insert:str=""):
        print(" " * indent, insert, self)
        for x in self._raw_children:
            if x is GdType:
                x.print_nested(indent+1, "|-")
            else:
                print(" "*indent+1, insert, x)

    def __init_subclass__(cls):
        cls._all_types.append(cls)

    def __init__(self):
        _raw_children = []

    def __repr__(self)->str:
        return self.__class__.__name__ + "()"

# class GdResource(GdType):
#     _lark_key = "resource"

class GdTyping(GdType):
    _lark_key = "type"
    value : list

    @classmethod
    def parse_lark(cls, meta, children)->Any:
        inst = cls()
        inst.value = children
        return inst

class GdProperty(GdType):
    _lark_key = "property"
    name : str
    value : Any
    
    @classmethod
    def parse_lark(cls, meta, children)->Any:
        inst = cls()
        inst.name = children[0].value
        inst.value = children[1]
        if inst.value is list:
            inst.value = inst.value[0]
        return inst
    
    def __repr__(self)->str:
        return f"{self.__class__.__name__}:{self.name} \t = ({self.value})"


class GdValue(GdType):
    _lark_key = "value"
    
    typing : list[str] = None
    value  : Any = None

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.typing}]({self.value})"
    
    @classmethod
    def parse_lark(cls, meta, children:list[Token|Any])->Any:
        return children

    def _parse_lark_typing(self,token:Token):
        self.typing = token.value

    def _parse_lark_value(self,token:Token):
        self.value = token.value


class _GdValueFloat(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    _lark_key = "FLOAT"
    _primitive_types = [float]
    _primitive = True

    @classmethod
    def parse_lark(cls, meta, children:list[Token|Any])->Any:
        return float(children)

class _GdValueString(GdValue):
    ''' Primitive, refer to for interpretation, but not use '''
    _lark_key = "STRING"
    _primitive_types = [str]
    _primitive = True

    @classmethod
    def parse_lark(cls, meta, children:list[Token|Any])->Any:
        return str(children).strip('"')

class GdValueExtResource(GdValue):
    _lark_key = "extresource"
    ref : Any

    @classmethod
    def parse_lark(cls, meta, children:list[Token|Any])->Any:
        inst = cls()
        inst.value = str(children).strip('"')
        return inst
    
class GdValueArray(GdValue):
    value : list
    _lark_key = "array"
    _lark_key_explicit = "array_explicit"
    
    @classmethod
    def parse_lark(cls, meta, children:list[Token|Any]=[])->Any:
        inst = cls()
        return inst

    @classmethod
    def parse_lark_explicit(cls, meta, children:list[Token|Any]=[])->Any:
        inst = cls()
        return inst

class GdValueVector2(GdValueArray): _lark_key = "vector2"
class GdValueVector3(GdValueArray): _lark_key = "vector3"
class GdValueVector4(GdValueArray): _lark_key = "vector4"
class GdValueColor(GdValueArray): _lark_key = "color"
class GdValueAABB(GdValueArray): _lark_key = "aabb"
class GdValueQuaternion(GdValueArray): _lark_key = "quaternion"
class GdValueTransform3D(GdValueArray): _lark_key = "transform3d"
class GdValuePackedByteArray(GdValueArray): _lark_key = "packedbytearray"
class GdValuePackedInt32Array(GdValueArray): _lark_key = "packedint32array"
class GdValuePackedInt64Array(GdValueArray): _lark_key = "packedint64array"
class GdValuePackedFloat32Array(GdValueArray): _lark_key = "packedfloat32array"
class GdValuePackedFloat64Array(GdValueArray): _lark_key = "packedfloat64array"
class GdValuePackedStringArray(GdValueArray): _lark_key = "packedstringarray"
class GdValuePackedVector2Array(GdValueArray): _lark_key = "packedvector2array"
class GdValuePackedVector3Array(GdValueArray): _lark_key = "packedvector3array"
class GdValuePackedVector4Array(GdValueArray): _lark_key = "packedvector4array"
class GdValuePackedColorArray(GdValueArray): _lark_key = "packedcolorarray"


class _GdValueDictionaryPair(GdValue):
    _lark_key = "pair"
    def parse_lark(cls, children:list[Token|Any])->Any:
        return [children[0], children[1]]

class GdValueDictionary(GdValue):
    value : dict
    _lark_key = "dictionary"
    _lark_key_explicit = "dictionary_explicit"
    
    @classmethod
    def parse_lark(cls, meta, children:list[Token|Any]=[])->Any:
        inst = cls()
        inst.value = dict()
        for x in children:
            inst.value[x[0]] = x[1]
        return inst

    @classmethod
    def parse_lark_explicit(cls, meta, children:list[Token|Any])->Any:
        pass

class _packed_vector2(GdValueArray):
    _lark_key = "packed_vector2"
    @classmethod
    def parse_lark(cls, meta, children):
        return children
class _packed_vector3(GdValueArray):
    _lark_key = "packed_vector3"
    def parse_lark(cls, meta, children):
        return children
class _packed_vector4(GdValueArray):
    _lark_key = "packed_vector4"
    def parse_lark(cls, meta, children):
        return children



# class GdValueArrayPacked(GdValueArray):
#     pass