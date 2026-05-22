from typing import Any, Type
from ..primitives import *
from lark.visitors import Transformer, v_args

## This structure is the minimum defintion of how a file should be parsed
## THe goal is to have a generic read into tree structure, then dynamically expand the definitions away from the base types.
## Once I am strucutrally correct, I will switch to a strict definition.

class GdType():
    _all_types : list[Type] = []
    _lark_key     : str  = "__default__" ##Lark key && Function key
    _raw_children : list[Any]

    @classmethod
    def parse_lark(cls, line, children)->Any:
        inst = cls.new()
        inst._raw_children = children
        return inst
    
    @classmethod        
    def generate_transformer(cls)->Type[Transformer]:
        ## Construct a parser class and return it
        @v_args()
        class _Transformer(Transformer):
            pass
        for x in cls._all_types:
            def parser(*args,**kwargs)->Any:
                return x.parse_lark(*args,**kwargs)
            setattr(_Transformer, x._lark_key, parser)
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

    def __str__(self)->str:
        return self.__class__.__name__ + ":" + self._lark_key + "()"


class GdResource(GdType):
    _lark_key = "resource"
class GdProperty(GdType):
    _lark_key = "property"
class GdValue(GdType):
    _lark_key = "value"