from __future__ import annotations
from typing import Any, Type
from ..primitives import *
from lark.visitors import Transformer, v_args
from lark import Token

from typing import List
## This structure is the minimum defintion of how a file should be parsed
## THe goal is to have a generic read into tree structure, then dynamically expand the definitions away from the base types.
## Once I am strucutrally correct, I will switch to a strict definition.

class GdTypeAnnoation():
    ''' To be expanted on later; will need to incorperate refs by UUID, ect '''
    type : Type
    def __init__(self, type:Type):
        self.type = type
    def __repr__(self):
        return f"<{self.type.__name__}>"
STRING = GdTypeAnnoation(str)
VARIANT = GdTypeAnnoation(Any)
NULL = GdTypeAnnoation(None)

class GdType():
    _all_types : list[Type] = []
    _lark_key     : str  = "__default__" ##Lark key && Function key
    _lark_key_explicit = ""
    _raw_children : list[Any]

    @classmethod
    def parse_lark(cls, tfm, meta, children)->Any:
        if len(children) == 0: 
            return None
        inst = cls()
        inst._raw_children = children
        return inst
    
    @staticmethod 
    def generate_parser(func)->Callable:
        ''' Required due to python's problem with lambda namespaces in loops '''
        def parser(*args):
            return func(*args)
        return parser

    @classmethod        
    def generate_transformer(cls)->Type[Transformer]:
        ## Construct a parser class and return it
        class _Transformer(Transformer):
            pass
        for x in cls._all_types:
            if hasattr(_Transformer, x._lark_key) and (x._lark_key != ""):
                raise Exception("Tranformer already has key populated", x._lark_key)

            if x._lark_key:
                setattr(_Transformer, x._lark_key, cls.generate_parser(x.parse_lark))

            if x._lark_key_explicit:
                setattr(_Transformer, x._lark_key_explicit, cls.generate_parser(x.parse_lark_explicit))
        
        return v_args(meta=True, inline=True)(_Transformer)
    

    def __init_subclass__(cls):
        cls._all_types.append(cls)

    def __init__(self):
        _raw_children = []

    def __repr__(self)->str:
        return self.__class__.__name__ + "()"

    # def print_tree(self, indent:int=0, insert:str=""):
    #     print(" " * indent, insert, self)
    #     for x in self._raw_children:
    #         if x is GdType:
    #             x.print_nested(indent+1, "|-")
    #         else:
    #             print(" "*indent+1, insert, x)


class Collection():
    items : list[Any]
    item_appended : Signal
    item_removed : Signal
    
    def __init__(self):
        items = []
        self.item_appended = Signal(self) 
        self.item_removed = Signal(self) 
    
    def append(self,item:Any):
        self.items.append(item)
        self.item_appended.emit(item)

    def remove(self,item:Any):
        if item in self.items:
            self.items.remove(item)
            self.item_removed.emit(item)

class CollectionFile[T](Collection):
    by_uuid : dict[str, T] = None
    by_path : dict[str, T] = None

    uuid_set : Signal[T, str]
    path_set : Signal[T, str]

    file_removed : Signal[T, str, str]
    file_added : Signal[T, str, str]

    def __init__(self):
        super().__init__()

        self.uuid_set = Signal(self)
        self.path_set = Signal(self)

        self.item_appended.connect(self._on_append)
        self.item_removed.connect(self._on_remove)

        self.by_path = {}
        self.by_uuid = {}

    def _on_append(self,item:T):
        item.uuid_changed.connect(self.uuid_set.emit, True)
        item.path_changed.connect(self.path_set.emit, True)
        if item.uuid != None:
            self.uuid_set.emit(item,None,item.uuid)
            self.by_uuid[item.uuid] = item
        if item.path != None:
            self.path_set.emit(item,None,item.path)
            self.by_path[item.path] = item
        self.file_added.emit(item, item.uuid, item.path)

    def _on_remove(self,item:T):
        item.uuid_changed.disconnect(self.uuid_set.emit)
        item.path_changed.disconnect(self.path_set.emit)
        if item.uuid in self.by_uuid.keys():
            self.by_uuid.remove(item.uuid)
        if item.path in self.by_path.keys():
            self.by_path.remove(item.path)
        self.file_removed.emit(item, item.uuid, item.path)
    
    
class GdProject():
    files : CollectionFile[GdFile]
    
    file_appended : Signal
    file_removed : Signal

    uuid_set : Signal
    path_set : Signal

    def __init__(self):
        self.files = CollectionFile()
        self.uuid_set = Signal(self, (self.files.uuid_set,))
        self.path_set = Signal(self, (self.files.path_set,))
        self.file_appended = Signal(self, (self.files.file_appended,))
        self.file_removed = Signal(self, (self.files.file_removed,))
        
        
class GdFile(GdType):
    _lark_key = "file"
    
    uuid : str|None = None
    uuid_set : Signal[str]
    
    path : str|None = None
    path_set : Signal[str]
    
    @classmethod
    def parse_lark(cls, tfm, meta, file):
        return file

class GdFileResource(GdFile):
    _lark_key = "file_resource"

    res_added : Signal[GdSubResource]
    res_removed : Signal[GdSubResource]

    comments : list[str]
    header_props : list[GdProperty]
    sub_resources : Collection[GdSubResource]
    ## Collection needs to spawn ID/Namespaces

    @classmethod
    def parse_lark(cls, tfm, meta, comments_and_properties:list[str|GdProperty], sub_resources:list[GdSubResource] ):
        inst = cls()
        for x in comments_and_properties:
            if isinstance(x,str):
                inst.comments.append(x)
            else:
                inst.header_props.append(x)

        for x in sub_resources:
            inst.sub_resources.append(x)
        
        return inst

    def __init__(self):
        self.comments = []
        self.header_props = []
        self.sub_resources = Collection()
        self.sub_resources.item_appended.connect(self.res_added.emit)
        self.sub_resources.item_removed.connect(self.res_removed.emit)

class GdSubResource(GdType):
    _lark_key = "sub_resource"
    gdid : str = "node"
    uuid : str = "" 
    properties : list[GdProperty]

class GdTyping(GdType):
    _lark_key = "type"
    value : list

    @classmethod
    def parse_lark(cls, tfm, meta, type_a:Token=None, type_b:Token=None)->Any:
        inst = cls()
        inst.value = [type_a, type_b]
        return inst

class GdProperty(GdType):
    _lark_key = "property"
    name : str
    value : Any
    
    def __init__(self, name:str, value:Any=None):
        self.name = name
        self.value = value

    @classmethod
    def parse_lark(cls, tfm, meta, name:Token, value=None)->Any:
        inst = cls()
        inst.name = name.value
        inst.value = value
        if inst.value is list:
            inst.value = inst.value[0]
        return inst
    
    def __repr__(self)->str:
        return f"{self.__class__.__name__} ( {self.name} = {self.value} )" 

class GdValue(GdType):
    _has_typing : bool = False
    _lark_key = "value"
    
    typing : tuple[GdTypeAnnoation|GdType] = (VARIANT,)
    value  : Any = None

    def __init__(self, value=None,type=None):
        _raw_children = []
        if value != None:
            self.set_value(value)
        if type != None:
            self.set_type(type)

    def __repr__(self):
        if self._has_typing:
            return f"{self.__class__.__name__}[{self.typing}]({self.value})"
        return f"{self.__class__.__name__}({self.value})"
    
    @classmethod
    def parse_lark(cls, tfm, meta, *children:list[Token|Any])->Any:
        ''' "Thin" by default'''
        return children
    
    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return (self.value == value.value) and (self.typing == value.typing)
        return super().__eq__(value)


class GdValueExtResource(GdValue):
    _has_typing = True
    _lark_key = "extresource"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
class GdValueNodePath(GdValue):
    _lark_key = "nodepath"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst
    
class GdValueSubResource(GdValue):
    _lark_key = "subresource"
    ref : Any

    @classmethod
    def parse_lark(cls, tfm, meta, type:GdType, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"')
        return inst