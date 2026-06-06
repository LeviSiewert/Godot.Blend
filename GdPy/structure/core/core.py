from __future__ import annotations
from .primitives import Signal, SignalContainer
from abc import ABC, abstractmethod
from typing import Self, Any, Type
from .primitives import Signal, SignalContainer, Context, Collection
from .class_db import ClassDb, GdClassDef, GdPropertyDef
from .file_db import File, FileDb
from pathlib import Path
from contextlib import contextmanager

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

    @contextmanager
    def context(self):
        c = Context()
        with c.w("project", self):
            yield c

class GdType(ABC, SignalContainer):
    @classmethod
    @abstractmethod
    def lark_keys(cls,)->tuple[str]: 
        ''' Return the lark key(s) that this class can parse'''
        return ("",)

    @classmethod
    @abstractmethod
    def parse_lark(cls, key:str, *args, **kwargs)->Self:
        return

class GdResource(GdType):
    definition : GdClassDef
    definition_updated : Signal[GdClassDef]

    properties : dict[str, GdValue]
    
    def __init__(self, properties:dict=None):
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties
        super().__init__()

    @abstractmethod
    def get_struct_children(self)->dict[str,tuple[GdType|Any]]:
        return {}
    
    def set_struct_children(self, key:str, items:Any):
        setattr(key, items)

    def call_struct(self, func_id:str, args, kwargs, depth_first:bool=False, _filter:callable=lambda x: True):
        if not depth_first:
            if hasattr(self, func_id):
                getattr(self, func_id)(*args, **kwargs)

        for k,v in self.get_struct_children():
            for x in filter(_filter, v):
                if hasattr(x, "call_struct"):
                    x.call_struct(func_id, depth_first, *args, **kwargs)

        if depth_first:
            if hasattr(self, func_id):
                getattr(self, func_id)(*args, **kwargs)

class GdValue(GdType):
    def __init__(self, value:Any=None):
        self.set_value(value)

    @abstractmethod
    def set_value(self, value)->None:
        pass

    # @abstractmethod
    # def __eq__(self, value)->bool:
    #     return super().__eq__(value)

class GdProperty(GdType):
    name : str
    value : GdValue
