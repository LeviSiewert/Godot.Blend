from __future__ import annotations
from typing import Any, Type
from ..primitives import *
from lark.visitors import Transformer, v_args
from lark import Token
from .gd_class_db import ClassDb

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

            if x._lark_key:
                if hasattr(_Transformer, x._lark_key):
                    raise Exception("Tranformer already has key populated", x._lark_key, x.__name__)
                setattr(_Transformer, x._lark_key, cls.generate_parser(x.parse_lark))

            if x._lark_key_explicit:
                if hasattr(_Transformer, x._lark_key_explicit):
                    raise Exception("Tranformer already has key populated", x._lark_key_explicit, x.__name__)
                setattr(_Transformer, x._lark_key_explicit, cls.generate_parser(x.parse_lark_explicit))
        
        return v_args(meta=True, inline=True)(_Transformer)
    

    def __init_subclass__(cls):
        cls._all_types.append(cls)

    def __init__(self):
        _raw_children = []

    def __repr__(self)->str:
        return self.__class__.__name__ + "()"

class VARIANT(GdType):
    _lark_key = ""
class NULL(GdType):
    _lark_key = ""

class GdProject():
    files : CollectionFile[GdFile]
    file_appended : Signal
    file_removed : Signal

    uuid_set : Signal
    path_set : Signal

    def __init__(self):
        self.class_db = ClassDb()
        self.files = CollectionFile()
        self.uuid_set = Signal(self, (self.files.uuid_set,))
        self.path_set = Signal(self, (self.files.path_set,))
        self.file_appended = Signal(self, (self.files.file_appended,))
        self.file_removed = Signal(self, (self.files.file_removed,))
        
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
    properties : Properties
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
        
        self.properties = Properties()
        self.sub_resources = Collection()

        self.res_added = Signal(self, (self.sub_resources.item_appended,))
        self.res_removed = Signal(self, (self.sub_resources.item_removed,))



class GdSubResource(GdType):
    _lark_key = "sub_resource"
    _type_key : str = ""        ##node, ect.

    _subres_by_key : dict[str, GdSubResource] = {}

    gd_type : ResourceDef
    properties : dict[GdValue]

    def set_gd_type(self, ty: ResourceDef):
        self.gd_type = ty


    def __init__(self):
        super().__init__()
        self.properties = {}

    def __getattr__(self, name):
        if name in self.properties.keys():
            return self.properties[name]
        elif self.gd_type:
            return self.gd_type.properties[name].default
        else:
            raise Exception("Could not find attribute!")

    def __setattr__(self, name, value):
        assert(name in self.gd_type.properties.keys())
        self.properties[name] = value

    def __init_subclass__(cls):
        cls._lark_key = ""
        if cls._type_key != "":
            assert(not (cls._type_key in cls._subres_by_key.keys()))
            cls._subres_by_key[cls._type_key] = cls
        return super().__init_subclass__()
    
    @classmethod
    def parse_lark(cls, tfm, meta,key:str, *properties:list[GdProperty] ):
        if sbcls := cls._subres_by_key.get(key, None):
            return sbcls.populate_lark(key, *properties)
        return cls.populate_lark(key, *properties)

    @classmethod
    def populate_lark(cls, key:str, *properties:list[GdProperty]):
        inst = cls()
        for k,v in properties.items():
            inst.properties[k] = v
        return inst

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
        inst = cls(name.value, value)
        if inst.value is list:
            inst.value = inst.value[0]
        return inst
    
    def __repr__(self)->str:
        return f"{self.__class__.__name__} ( {self.name} = {self.value} )" 

class GdValue(GdType):
    _has_typing : bool = False
    _lark_key = "value"
    
    typing : tuple[GdType] = (VARIANT,)
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