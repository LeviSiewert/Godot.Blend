from __future__ import annotations
from typing import Type, Any

from .structure import _Resource, StructContext, GdType, GdValue, ExtResourceRefCollection
from .collections import Key, Reference, Collection
from .property_collection import PropertyCollection


class SubResource():
    context : StructContext
    owner : _Resource|None = None
    unique_id : Key[str]
    type : GdType|None = None
    
    instance : _Resource
    instance_editable : bool = False

    overlay : SubResource|None = None
    overlay_is_thin : bool = False
    
    properties : PropertyCollection

    def __setup__(self):
        self.context = StructContext(sub_resource=self)
        self.unique_id = Key(self, "unique_id", None)
        self.properties = PropertyCollection()
        return self

    def __init__(self, /, owner:_Resource|None=None, overlay:SubResource=None, type:Type=None, instance:_Resource=None, instance_editable:bool=False, unique_id:Any=None):
        self.__setup__()
        if not (unique_id is None):
            self.unique_id.set(unique_id)

        self.set_owner(owner)
        self.set_type(type)
        
        if instance:
            assert(overlay is None)
            self.set_overlay(instance.data.root)
            self.instance = instance
            self.instance_editable = instance_editable
        elif overlay:
            self.set_overlay(overlay)


class SubResourceCollection(Collection):
    unique_keys = ("unique_id",)
    _type = SubResource


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
    type : GdType|None|str
    format : int
    script : str #TEMP! resolve to from typing eventually w/a
    script_class : str #TEMP! resolve to from typing eventually w/a
    
    properties : PropertyCollection

    ext_resources : ExtResourceRefCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection

    def __setup__(self):
        self.properties = PropertyCollection()
        self.ext_resources = ExtResourceRefCollection()
        self.sub_resources = SubResourceCollection()
        return self
    
    def __init__(self, type, format, uid, script_class:str=None):
        self.type = type
        self.script_class = script_class
        super().__init__(format=format, uid=uid)