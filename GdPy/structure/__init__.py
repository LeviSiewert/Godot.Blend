from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Self, Any, Type, LambdaType
from ..primitives import Signal, SignalContainer
from .gd_definitions import ClassDb, GdClassDef, GdPropertyDef
from .file_db import File, FileDb
from pathlib import Path

class GdProject():
    files : FileDb
    class_db : ClassDb

    path : Path

    def __init__(self, path:str):
        self.path = Path(path)
        assert(self.path.exists())

        self.files = FileDb()
        self.class_db = ClassDb()

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
    def get_struct_children(self)->tuple[GdType|Any]:
        return tuple()

    def call_struct(self, func_id:str, args, kwargs, depth_first:bool=False, _filter:callable=lambda x: True):
        if not depth_first:
            getattr(self, func_id)(*args, **kwargs)

        for x in filter(_filter, self.get_struct_children()):
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