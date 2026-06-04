from __future__ import annotations
from ..primitives import Signal, SignalContainer
from abc import ABC, abstractmethod
from typing import Self, Any, Type, LambdaType

class STOP(): pass

class File():
    uuid : str
    path : str
    data : Any

class GdProject():
    files : Collection[File]
    class_db : Collection[GdClassDef]

    def __init__():
        pass

class GdPropertyDef():
    default : GdValue

class GdClassDef():
    uuid : str
    path : str
    extends : GdClassDef
    properties : list[GdPropertyDef]

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
            stop = getattr(self, func_id)(*args, **kwargs)
            if stop is STOP: return

        for x in filter(_filter, self.get_struct_children()):
            if hasattr(x, "call_struct"):
                x.call_struct(func_id, depth_first, *args, **kwargs)

        if depth_first:
            getattr(self, func_id)(*args, **kwargs)

    @abstractmethod
    def __eq__(self, value):
        return super().__eq__(value)


class GdResource(GdType):
    script : GdScriptDef
    properties : dict[str, GdValue]
    
    def __init__(self):
        self.properties = {}
        super().__init__()

class GdValue(GdType):
    pass