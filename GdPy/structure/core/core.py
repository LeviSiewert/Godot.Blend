from __future__ import annotations
from .primitives import Signal, SignalContainer
from abc import ABC, abstractmethod
from typing import Self, Any, Type
from .primitives import Signal, SignalContainer, Context, Collection, CacheTreeNode
from .class_db import ClassDb, GdClassDef, GdPropertyDef,ClassDbEnforcable
from .file_db import File, FileDb
from .property_collection import PropertyCollection
from pathlib import Path
from contextlib import contextmanager

class GdProject():
    _cache_layers = ("*",)
    _context_key = "project"

    file_db : FileDb
    class_db : ClassDb

    path : Path
    file_proj : Path

    def __init__(self, path:str, file_db:FileDb, class_db:ClassDb):
        self.path = Path(path)
        assert(self.path.exists())

        self.file_proj = self.path / "project.godot"
        assert(self.file_proj.exists())

        self.file_db = file_db
        self.class_db = class_db

        file_db.gd_project = self
        class_db.gd_project = self

    @contextmanager
    def context(self):
        c = Context()
        with c.w("project", self):
            yield c

class GdType(ABC, SignalContainer):
    _cache_layers : tuple = tuple()
    _context_key : str|None = None

    @classmethod
    @abstractmethod
    def lark_keys(cls,)->tuple[str]: 
        ''' Return the lark key(s) that this class can parse'''
        return ("",)

    @classmethod
    @abstractmethod
    def parse_lark(cls, key:str, tfrm, *args, **kwargs)->Self:
        return

class GdResource(GdType):
    _cache_layers = ("postload_resource",)
    _context_key = "resource"

    @abstractmethod
    def get_struct_children(self)->tuple[GdType|Any]:
        return tuple()

class GdSubResource(GdType):
    _cache_layers = ("postload_subresource",)
    _context_key = "subresource"

    @abstractmethod
    def get_struct_children(self)->tuple[GdType|Any]:
        return tuple()
    
class GdValue(GdType):
    _context_key = "value"

    def get_struct_children(self)->tuple[GdType|Any]:
        return tuple()

    @abstractmethod
    def set_value(self, value)->None:
        pass

    def __repr__(self,):
        return f"{self.__class__.__name__}({str(self.value)})"

    # @abstractmethod
    # def __eq__(self, value)->bool:
    #     return super().__eq__(value)

# class GdProperty(GdType):
#     _context_key = "property"
#     name : str
#     value : GdValue

#     def get_struct_children(self)->tuple[GdType|Any]:
#         if isinstance(self.value, GdType):
#             return (self.value,)
#         return tuple()
    

