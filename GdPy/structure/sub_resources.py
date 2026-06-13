from __future__ import annotations
from .core import GdResource, GdSubResource, PropertyCollection, ClassDbEnforcable, Collection
from typing import Self
from contextlib import contextmanager
from abc import abstractmethod
from .core.primitives import MultiKeyCollection
from .values import GdValuePackedStringArray
import random
import string

class _SubResource(GdSubResource):
    properties : PropertyCollection

    def __init__(self,_construct:bool=False):
        if not _construct:
            self.setup()            
        super().__init__()

    def setup(self):
        self.properties = PropertyCollection()

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def new(cls, **kwargs)->Self:
        self = cls()
        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise KeyError("Requires predefition of header attribute:", self,k)
            setattr(self,k,v)
        return self
    
    @classmethod
    def parse_lark(cls, key, trfm, header_properties:PropertyCollection, body_properties:PropertyCollection):
        self = cls(_construct = True)
        for k,v in header_properties.items.items():
            assert(hasattr(self, k))
            setattr(self, k, v)
        self.properties = body_properties
        return self


    def get_struct_children(self):
        return self.properties.items.values()
    
    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return self.properties == self.properties
        return super().__eq__(value)
    
    def __hash__(self):
        return super().__hash__()

class SubResourceExt(_SubResource):
    type : str = None
    path : str = None
    uid : int = None
    id : int = None

    @classmethod
    def lark_keys(cls):
        return ("ext_resource",)

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return all ([
                self.properties == value.properties,
                self.type == value.type,
                self.path == value.path,
                self.uid == value.uid,    
                self.id == value.id,    
            ])
        return super().__eq__(value)

    def __hash__(self):
        return super().__hash__()

class SubResourceEdit(_SubResource):
    type : str = None
    path : str = None
    uid : int = None
    id : int = None
    
    @classmethod
    def lark_keys(cls):
        return ("edit_resource",)
    
    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return all ([
                self.properties == value.properties,
                self.type == value.type,
                self.path == value.path,
                self.uid == value.uid,    
                self.id == value.id,    
            ])
        return super().__eq__(value)

    def __hash__(self):
        return super().__hash__()

class SubResource(_SubResource): #ClassDbEnforcable):
    type : str = None
    id : int = None

    @classmethod
    def lark_keys(cls):
        return ("sub_resource",)
    
    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return all ([
                self.properties == value.properties,
                self.type == value.type,  
                self.id == value.id,    
            ])
        return super().__eq__(value)

    def __hash__(self):
        return super().__hash__()

class SubResourceNode(_SubResource): #ClassDbEnforcable):
    name : str = None
    type : str = None
    node_paths : GdValuePackedStringArray = None
    parent : str = None
    unique_id : int = None

    is_root : bool = False
    tree : MultiKeyCollection = None
    owner : SubResourceNode = None
    _parent : SubResourceNode = None
    _children : list[SubResourceNode] = None

    @classmethod
    def lark_keys(cls):
        return ("node_resource",)

    def __init__(self, _construct = False):
        self._children = []
        super().__init__(_construct)

    def add_child(self,item:SubResourceNode):
        assert(item._parent == None)
        item._parent = self
        self._children.append(item)

    def remove_child(self,item:SubResourceNode):
        assert(item._parent is self)
        assert(item in self._children)
        item._parent = None
        self._children.remove(item)

    def set_owner(self,owner):
        self.owner = owner

    def set_tree(self,treecol):
        self.treecol = treecol

    def get_children(self)->tuple[SubResourceNode]:
        return tuple(self._children)

    def __repr__(self):
        return f"Node(name='{self.name}')"

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return all ([
                self.properties == value.properties,
                self.name == value.name,
                self.type == value.type,
                self.node_paths == value.node_paths,
            ])
        return super().__eq__(value)

    def __hash__(self):
        return super().__hash__()

class SubResourceCategory(_SubResource):
    name : str = None

    @classmethod
    def lark_keys(cls):
        return ("cat_resource",)
    
    @classmethod
    def parse_lark(cls, _key, trfm, name:str, body_properties:PropertyCollection):
        self = cls(_construct = True)
        self.name = name
        self.properties = body_properties
        return self

class ResourceContainer(_SubResource):
    name : str = None

    @classmethod
    def lark_keys(cls):
        return ("prim_resource",)
    
    @classmethod
    def parse_lark(cls, key, trfm, body_properties:PropertyCollection):
        self = cls(True)
        self.properties = body_properties
        return self


_all = (
    SubResourceExt,
    SubResourceEdit,
    SubResource,
    SubResourceNode,
    SubResourceCategory,
    ResourceContainer,
)