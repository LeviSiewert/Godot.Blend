
# class GdTypeTransformer(lark.visitors.Transformer):
#     def type_name():
#         pass
#     pass
from lark.Visitors import Transfomer, v_args
from abc import ABC, abstractmethod
from typing import Any, Type

@v_args(meta=True)
class Transfomer(lark.Visitors.Transformer):
    def __default__():
        pass
    pass

class GdType(ABC):
    lark_key : str = ""

    def __init_subclass__(cls):
        if cls.lark_key != "": return
        if hasattr(cls, cls.lark_key): 
            raise Exception("cannot incorperate class to lark parser, collission of lark_key", cls.lark_key)
        setattr(cls, cls.lark_key, cls.lark_parse)

    @classmethod
    @abstractmethod
    def lark_parse(cls, transformer, meta, children)->Any:
        ## Lark parsing component. Return instance of this class
        return None

    @abstractmethod
    def lark_export()->list[str]:
        ## Call all children and format self to resulting strings
        return []

class GdTypeResource(GdType):
    ## Abstract class for incorperating Resources by header ids 
    lark_key = "resource"
    resource_id : str = ""
    subtypes : dict[str,Type] = {}

    @classmethod
    def lark_parse(cls, transformer, meta, children):
        type_cls = cls.subtypes.get(children[0], None)
        return type_cls.lark_parse(transformer, meta, children)
    
    def __init_subclass__(cls):
        if cls.resource_id == "": return
        cls.subtypes[cls.resource_id] = cls

