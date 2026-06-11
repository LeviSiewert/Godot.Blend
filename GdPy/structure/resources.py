from __future__ import annotations
from .core import GdResource, GdProperty, GdType, Context, GdClassDef, Collection
from typing import Type
from contextlib import contextmanager


## Resource (File) Types:

class GdResourceFile(GdResource):
    sub_resources : Collection[GdResource]
    ext_resources : Collection[GdExtResource]

    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_resource",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_resource",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:dict[str,GdProperty], ext_res:list[GdExtResource], sub_res:list[GdSubResource], prim_resource:_GdResourceFileBody):
        raise Exception("not yet defined!")

class GdResourceFileScene(GdResource):
    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_scene",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_scene",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:dict[str,GdProperty], ext_res:list[GdExtResource], sub_res:list[GdSubResource], node_res:list[GdSubResourceNode], edit_res:list[GdSubResource]):
        raise Exception("not yet defined!")

class GdResourceFileImport(GdResource):
    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_settings",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_settings",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:dict[str,GdProperty], categories:list[_GdResourseSubcategory]):
        raise Exception("not yet defined!")
    

## SubResources:


class GdSubResource(GdResource):
    type : str
    id   : str

    @classmethod
    def lark_keys(cls):
        return ("sub_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        raise Exception("undefined so far!")
   
    @contextmanager
    def _add_context(self, ctx:Context):
        with ctx.w("sub_resource",self):
            yield

class _GdResourceFileBody(GdSubResource):
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

class _GdResourseSubcategory(GdSubResource):
    """Utility class best served as an instance in the parser"""

    value : list
    key : str

    @classmethod
    def lark_keys(cls):
        return ("prim_subcategory",)
    
    @classmethod
    def parse_lark(cls, _key, tfm, key, resource_body):
        return cls(key, resource_body)

    def __init__(self, key, value):
        self.key = key
        self.value = value

class GdExtResource(GdSubResource):
    @classmethod
    def lark_keys(cls):
        return ("ext_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        raise Exception("undefined so far!")

class GdEditResource(GdSubResource):
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
    GdResourceFile,
    GdResourceFileScene,
    GdResourceFileImport,
    _GdResourceFileBody,
    _GdResourseSubcategory,
    GdSubResource,
    GdExtResource,
    GdEditResource,
    GdSubResourceNode,
)
