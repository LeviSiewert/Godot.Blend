from __future__ import annotations
from .core import GdResource, GdProperty, GdType, Context, GdClassDef, Collection
from typing import Type
from contextlib import contextmanager

class GdResourceFile(GdResource):
    sub_resources : Collection[GdResource]
    
    script_class : str
    format       : str
    type         : str
    uid          : str

    @contextmanager
    def _add_context(self,ctx:Context, *args,**kwargs):
        with ctx.w("file_resource",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("gd_resource",)

    @classmethod
    def parse_lark(cls, key:str, tfm, resource_header, sub_resources):
        self = cls()
        
        _ext_res = filter(lambda x: isinstance(x, GdExtResource))
        _edit_res = filter(lambda x: isinstance(x, GdEditResource))
        _sub_res = filter(lambda x: isinstance(x, GdSubResource))
        _props = filter(lambda x: isinstance(x, GdResourceFileBody))

        raise Exception("undefined so far!")

    def __init__(self,
            type         : str,
            script_class : str,
            format       : str,
            uid          : str,
            properties : dict = None,
            sub_resources : Collection = None,
            ):
        self.type = type
        self.script_class = script_class
        self.format = format
        self.uid = uid
        super().__init__(properties)
        if self.sub_resources is None:
            self.sub_resources = Collection()
        else:
            self.sub_resources = sub_resources

    def attach_definition(self, context:Context):
        script = self.properties.get("script",None)
        if not script: return
        context.project.get().class_db[script]
        self.set_definition()

    def set_definition(self, class_def:GdClassDef):
        self.definition = class_def
        self.definition_updated(class_def)

class GdResourceFileBody(GdResource):
    """Utility class best served as an instance in the parser"""

    value : list

    @classmethod
    def lark_keys(cls):
        return ("prim_resource",)
    
    @classmethod
    def parse_lark(cls, key, tfm, resource_body):
        return cls(resource_body)

    def __init__(self, key, value):
        self.value = value

class GdResourseSubcategory(GdResource):
    """Utility class best served as an instance in the parser"""

    value : list

    @classmethod
    def lark_keys(cls):
        return ("prim_subcategory",)
    
    @classmethod
    def parse_lark(cls, key, tfm, resource_body):
        return cls(resource_body)

    def __init__(self, key, value):
        self.value = value



class GdSubResource(GdResource):
    type : str
    id   : str

    @classmethod
    def lark_keys(cls):
        return ("sub_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        raise Exception("undefined so far!")

    def __init__(
            self,
            type : str,
            id   : str,
            properties : dict = None,
            ):
        self.type = type 
        self.id   = id
        super().__init__(properties)
   
    def attach_definition(self, context:Context):
        script = self.properties.get("script",None)
        if not script: return
        context.project.get().class_db[script]
        self.set_definition()

    def set_definition(self, class_def:GdClassDef):
        self.definition = class_def
        self.definition_updated(class_def)

class GdExtResource(GdResource):
    @classmethod
    def lark_keys(cls):
        return ("ext_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        raise Exception("undefined so far!")

class GdEditResource(GdResource):
    @classmethod
    def lark_keys(cls):
        return ("edit_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        raise Exception("undefined so far!")

class GdSubResourceNode(GdSubResource):
    @classmethod
    def lark_keys(cls):
        return ("node_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        raise Exception("undefined so far!")

_all : tuple[Type] = (
    GdResourceFileBody,
    GdResourseSubcategory,
    GdResourceFile,
    GdSubResource,
    GdExtResource,
    GdEditResource,
    GdSubResourceNode,
)
