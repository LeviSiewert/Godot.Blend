from .core import GdProject, File, GdResource, GdType, GdValue
from .resources import *
from typing import Type, Any
from lark import Token #type:ignore

class GdValueExtResource(GdValue):
    _cache_layers = ("postload_extresource",)
    _has_typing = True
    ref : Any
    
    address : str = None
    value : GdResource = None ##GdExtResource object

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("extresource",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.address = str(address).strip('"')
        return inst
    
    def set_value(self, value):
        return

    def postload(self, c:Context):
        if not self.address: return
        res = c.resource.get()
        self.value = res.get_extresource(c, self.address)
        # res.get_subresource(c, self.address)

class GdValueNodePath(GdValue):
    _cache_layers = ("postload_nodepath",)
    ref : Any
    address : str = None
    value : GdSubResource = None

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("nodepath",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.address = str(address).strip('"')
        return inst
    
    def set_value(self, value):
        return
    
    def postload(self, c:Context):
        if not self.address: return
        res = c.resource.get()
        res.get_nodepath(c, self.address)

class GdValueSubResource(GdValue):
    _cache_layers = ("postload_subresource",)
    ref : Any
    address : str = None
    value : GdSubResource = None

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("subresource",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.address = str(address).strip('"')
        return inst
    
    def set_value(self, value):
        return
    
    def postload(self, c:Context):
        if not self.address: return
        res = c.resource.get()
        self.value = res.get_subresource(c, self.address)
    
class GdValueResourceID(GdValue):
    _cache_layers = ("postload_rid",)
    ref : Any
    address : str = None
    value : File = None

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("rid",)

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        if not (address is None):
            inst.address = str(address).strip('"')
        return inst

    def set_value(self, value):
        return    

    def postload(self, c:Context):
        if not self.address: return
        file_db = c.file_db.get()
        self.value = file_db.get_file(self.address, null_ok=True)

_all : tuple[Type] = [
    GdValueExtResource,
    GdValueNodePath,
    GdValueSubResource,
    GdValueResourceID,
    ]
