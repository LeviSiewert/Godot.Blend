from __future__ import annotations
from .primitives import Signal, SignalContainer
from abc import ABC, abstractmethod
from typing import Self, Any, Type, LambdaType
from .primitives import Signal, SignalContainer, Context
from .class_db import ClassDb, GdClassDef, GdPropertyDef
from .file_db import File, FileDb
from pathlib import Path

class GdProject():
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

    def context(self):
        c = Context()
        with c.w("project", self):
            yield c

class GdType(ABC, SignalContainer):
    @abstractmethod
    @classmethod
    def lark_keys(cls,)->tuple[str]: 
        ''' Return the lark key(s) that this class can parse'''
        return ("",)

    @abstractmethod
    @classmethod
    def parse_lark(cls, key:str, *args, **kwargs)->Self:
        return

    @abstractmethod
    @classmethod
    def parse_lark_test(cls, )->None:
        pass
    
    @abstractmethod
    @classmethod
    def construct(cls, value:Any)->Self:
        pass


    @abstractmethod
    def get_struct_children(self)->dict[str,tuple[GdType|Any]]:
        return {}
    
    @abstractmethod
    def set_struct_children(self, key:str, items:tuple):
        return

    def call_struct(self, func_id:str, args, kwargs, depth_first:bool=False, _filter:callable=lambda x: True):
        if not depth_first:
            getattr(self, func_id)(*args, **kwargs)

        for k,v in self.get_struct_children():
            for x in filter(_filter, v):
                if hasattr(x, "call_struct"):
                    x.call_struct(func_id, depth_first, *args, **kwargs)

        if depth_first:
            getattr(self, func_id)(*args, **kwargs)

    @abstractmethod
    def __eq__(self, value):
        return super().__eq__(value)


class GdResource(GdType):
    script : GdClassDef
    properties : dict[str, GdValue]
    
    def __init__(self):
        self.properties = {}
        super().__init__()

class GdValue(GdType):
    pass