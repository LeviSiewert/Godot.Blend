from __future__ import annotations
from typing import Type, Any

from .structure import _Resource, StructContext, GdType, GdValue, ExtResourceCollection
from .collections import Key, Reference, Collection
from .property_collection import PropertyCollection


class SubResource():
    context : StructContext
    owner : _Resource|None = None
    id : Key[str]
    format : int = 3
    type : GdType|None = None
    
    instance : _Resource
    instance_editable : bool = False

    overlay : SubResource|None = None
    overlay_is_thin : bool = False
    
    properties : PropertyCollection

    def __setup__(self):
        self.context = StructContext(sub_resource=self)
        self.id = Key(self, "id", None)
        self.properties = PropertyCollection()
        return self

    def __init__(self, /, type:str=None, format:int=None, id:str=None):
        self.__setup__()
        if not (id is None):
            self.id.set(id)
        if format:
            self.format = format
        self.type = type
    
    def __colkeys__(self,)->tuple[Key]:
        return (self.id,)

    @classmethod
    def construct(cls, id:str=None, properties:dict=None, **kwargs):
        self = cls(id=id)
        if properties:
            self.properties.update(properties)
        for k,v in kwargs.items():
            if not (hasattr(self,k)):
                raise AttributeError(self, k, obj=self, name=k)
            setattr(self,k,v)
        return self

class SubResourceCollection(Collection):
    unique_keys = ("id",)
    _type = SubResource

    def key_matcher(self, addr):
        return "id"


class SubResourceRef(Reference, GdValue): 
    key_categories = ("id",)
    _type = SubResource

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.context.callback("resource",self._on_context_updated)

    def _on_context_updated(self, value:Any):
        if value is None:
            self.set_collection(None)
        else:
            value : ResourceTres
            self.set_collection(value.sub_resources)


class ResourceTres(_Resource):
    type : GdType|None|str = None
    format : int = None
    script : str = None #TEMP! resolve to from typing eventually w/a
    script_class : str = None #TEMP! resolve to from typing eventually w/a
    
    properties : PropertyCollection
    ext_resources : ExtResourceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection

    def __setup__(self):
        self.context = StructContext(resource=self)
        self.uid = Key(self, "uid", None)
        self.properties = PropertyCollection(context=self.context)
        self.ext_resources = ExtResourceCollection(context=self.context)
        self.sub_resources = SubResourceCollection(context=self.context)
        return self
    
    def __init__(self, /, type:str=None, format:int=None, uid:str=None, script_class:str=None):
        self.__setup__()
        if type:
            self.type = type
        if format:
            self.format = format
        if script_class:
            self.script_class = script_class
        if uid:
            self.uid.set(uid)

    def __colkeys__(self,)->tuple[Key]:
        return (self.uid,)
        
    @classmethod
    def construct(cls, properties:dict=None, ext_references:list=None, sub_resources:list=None, **kwargs):
        self = cls()
        if properties:
            self.properties.update(properties)
        if ext_references:
            self.ext_references.extend(ext_references)
        if sub_resources:
            self.sub_resources.extend(sub_resources)
        for k,v in kwargs.items():
            if not (hasattr(self,k)):
                raise AttributeError(k, obj=self, name=k)
            setattr(self,k,v)
        return self