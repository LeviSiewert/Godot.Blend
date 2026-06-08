from .core import GdProject, File, GdResource, GdType, GdValue
from .resources import *
from typing import Type, Any
from lark import Token #type:ignore

class GdValueExtResource(GdValue):
    _cache_layers = ("extresource",)
    _has_typing = True
    ref : Any
    
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("extresource",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
    def set_value(self, value):
        return
    
class GdValueNodePath(GdValue):
    _cache_layers = ("nodepath",)
    ref : Any

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("nodepath",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
    def set_value(self, value):
        return
    
class GdValueSubResource(GdValue):
    _cache_layers = ("subresource",)
    ref : Any
    
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("subresource",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
    def set_value(self, value):
        return
    
class GdValueResourceID(GdValue):
    _cache_layers = ("ResourceId",)
    ref : Any
    
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("rid",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        if not (address is None):
            inst.value = str(address).strip('"')
        return inst

    def set_value(self, value):
        return    

_all : tuple[Type] = [
    GdValueExtResource,
    GdValueNodePath,
    GdValueSubResource,
    GdValueResourceID,
    ]
