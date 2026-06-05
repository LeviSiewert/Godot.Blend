from .core import GdProject, File, GdResource, GdType, GdValue
from .resources import *
from typing import Type, Any
from lark import Token #type:ignore

class GdValueExtResource(GdValue):
    _has_typing = True
    ref : Any
    
    @classmethod
    def lark_key()->tuple[str]: 
        return ("extresource",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
class GdValueNodePath(GdValue):
    ref : Any

    @classmethod
    def lark_key()->tuple[str]: 
        return ("nodepath",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
class GdValueSubResource(GdValue):
    ref : Any
    
    @classmethod
    def lark_key()->tuple[str]: 
        return ("subresource",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
_all : tuple[Type] = [
    GdValueExtResource,
    GdValueNodePath,
    GdValueSubResource
    ]
