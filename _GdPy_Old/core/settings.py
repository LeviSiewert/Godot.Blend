from __future__ import annotations

from typing import Any

from .collections import Collection
from .property_collection import PropertyCollection
from .structure import _File, _Resource, StructContext

class ResourceSettings(_Resource):
    ''' .godot and .import styled files '''
    properties : PropertyCollection
    cat_resources : CategoryCollection

    def __setup__(self):
        super().__setup__()
        self.properties = PropertyCollection()
        self.cat_resources = CategoryCollection()

    @classmethod
    def construct(cls, format:int=None, uid:str=None, file:_File|str=None, properties:dict[str,Any]=None, cat_resources:list[Category]=None, **kwargs):
        self = cls(format=format, uid=uid, file=file)
        
        if cat_resources:
            self.cat_resources.extend(cat_resources)
        
        if properties:
            self.properties.update(properties)

        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise KeyError("Requires predefition of attribute:", self,k)
            setattr(self,k,v)

        return self

class Category():
    context : StructContext
    name : str
    properties : PropertyCollection
    def __setup__(self):
        self.context = StructContext(sub_resource=self)
        self.properties = PropertyCollection(context=self.context)
        return self

    def __init__(self, name):
        self.__setup__()
        self.name = name

    @classmethod
    def construct(cls, name:str, properties:dict[str,Any]=None, **kwargs):
        self = cls(name)

        if properties:
            self.properties.update(properties)

        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise KeyError("Requires predefition of attribute:", self,k)
            setattr(self,k,v)
        
        return self

class CategoryCollection(Collection):
    unique_keys = ("name",)
    
    def key_matcher(self, addr):
        return "name"