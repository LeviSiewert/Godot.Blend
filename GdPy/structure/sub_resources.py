from __future__ import annotations
from .core import GdResource, GdSubResource, PropertyCollection, ClassDbEnforcable, Collection
from typing import Self
from contextlib import contextmanager
from abc import abstractmethod
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

    @classmethod
    def new(cls, **kwargs)->Self:
        self = cls()
        for k,v in kwargs.items():
            assert(hasattr(self,k))
            setattr(self,k,v)
        return self

    @classmethod
    def parse_lark(cls, key, trfm, header_properties:PropertyCollection, body_properties:PropertyCollection):
        self = cls(_construct = True)
        for k,v in header_properties.items():
            assert(hasattr(self, k))
            setattr(self, "_"+k, v)
        self.properties = body_properties

    def get_struct_children(self):
        return self.properties.items()

class SubResourceExt(_SubResource):
    _type : str = None
    _path : str = None
    _uid : int = None
    _id : int = None
    
    @classmethod
    def lark_keys(cls):
        return ("sub_resource")

class SubResourceEdit(_SubResource):
    _type : str = None
    _path : str = None
    _uid : int = None
    _id : int = None
    
    @classmethod
    def lark_keys(cls):
        return ("edit_resource")

class SubResource(_SubResource, ClassDbEnforcable):
    _type : str = None
    _id : int = None

    @classmethod
    def lark_keys(cls):
        return ("sub_resource")

class SubResourceNode(_SubResource, ClassDbEnforcable):
    _name : str = None
    _type : str = None
    _parent : str = None
    _unique_id : int = None

    is_root : bool
    owner : GdResource
    parent : SubResourceNode
    children : list[SubResourceNode]

    @classmethod
    def lark_keys(cls):
        return ("node_resource")

class SubResourceCategory(_SubResource):
    _name : str = None

    @classmethod
    def lark_keys(cls):
        return ("prim_subcategory")
    
    @classmethod
    def parse_lark(cls, _key, trfm, name:str, body_properties:PropertyCollection):
        self = cls(_construct = True)
        self._name = name
        self.properties = body_properties

class ResourceContainer(_SubResource):
    _name : str = None

    @classmethod
    def lark_keys(cls):
        return ("prim_resource")
    
    @classmethod
    def parse_lark(cls, key, trfm, body_properties:PropertyCollection):
        self = cls(True)
        self.properties = body_properties

_all = (
    SubResourceExt,
    SubResourceEdit,
    SubResource,
    SubResourceNode,
    SubResourceCategory,
    ResourceContainer,
)