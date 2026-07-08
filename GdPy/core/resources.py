from __future__ import annotations
from typing import Type, Any

from .structure import _Resource, _File, StructContext, GdType, GdValue
from .collections import CollectionKey, Reference, Collection
from .property_collection import PropertyCollection
from .signals import Signal

class SubResource():
    context : StructContext
    owner : _Resource|None = None
    id : CollectionKey[str]

    format : int = 3
    type : GdType|None = None
    
    instance : _Resource = None
    instance_editable : bool = False

    overlay : SubResource|None = None
    overlay_is_thin : bool = False
    
    properties : PropertyCollection

    def __setup__(self):
        self.context = StructContext(sub_resource=self)
        self.id = CollectionKey(self, "id", None)
        self.properties = PropertyCollection()
        return self

    def __init__(self, /, type:str=None, format:int=None, id:str=None):
        self.__setup__()
        if not (id is None):
            self.id.set(id)
        if format:
            self.format = format
        self.type = type
    
    def __colkeys__(self,)->tuple[CollectionKey]:
        return (self.id,)

    @classmethod
    def construct(cls, id:str=None, properties:dict=None, _defered_apply_owner:bool=False, **kwargs):
        self = cls(id=id)
        if properties:
            self.properties.update(properties)

        if _defered_apply_owner:
            def set_owner_callback(scene:_Resource):
                if scene:
                    self.owner = scene
                    return Signal.REMOVE
            ##TODO: Verify this is only being called once.
            self.context.callback(key="resource", once=False, local_only=True, callback=set_owner_callback)

        for k,v in kwargs.items():
            if not (hasattr(self,k)):
                raise AttributeError(self, k, obj=self, name=k)
            setattr(self,k,v)
        return self
    
    def __eq__(self, value):
        if not isinstance(value, SubResource):
            return super().__eq__(value)
        return all((
            value.id == self.id,
            value.type == self.type,
            value.instance == self.instance,
            value.properties == self.properties,
            value.instance_editable == self.instance_editable,
        ))

class SubResourceCollection(Collection):
    unique_keys = ("id",)
    _type = SubResource

    def key_matcher(self, addr):
        return "id"


class SubResourceRef(Reference, GdValue): 
    key_categories = ("id",)
    typing = None

    def __init__(self, address = None, /, key_id = None, cached_value = None, collection=None, typing = None):
        self.typing = typing
        super().__init__(key_id, address, cached_value, collection)

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

from .structure import FileRef

class ResourceTres(_Resource):
    type : GdType|None|str = None
    format : int = None
    script : str = None #TEMP! resolve to from typing eventually w/a
    script_class : str = None #TEMP! resolve to from typing eventually w/a
    
    properties : PropertyCollection
    ext_resources : ExtResourceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection

    def __setup__(self):
        super().__setup__()
        self.properties = PropertyCollection(context=self.context)
        self.ext_resources = ExtResourceCollection(context=self.context)
        self.sub_resources = SubResourceCollection(context=self.context)
    
    def __init__(self, /, type:str=None, format:int=None, uid:str=None, script_class:str=None, file:str|_File=None):
        self.__setup__()
        if type:
            self.type = type
        if format:
            self.format = format
        if script_class:
            self.script_class = script_class
        if uid:
            self.uid.set(uid)
        if isinstance(file,str):
            self.file.store_address(file)
        elif isinstance(file, _File):
            self.file.store_value(file)
            self.file.store_address(file.path.addr)

    def __colkeys__(self,)->tuple[CollectionKey]:
        return (self.uid,)
        
    @classmethod
    def construct(cls, type:str=None, format:int=None, uid:str=None, script_class:str=None, file:str|_File=None, properties:dict=None, ext_resources:list=None, sub_resources:list=None, **kwargs):
        self = cls(type=type, format=format, uid=uid, script_class=script_class, file=file)
        if properties:
            self.properties.update(properties)
        if ext_resources:
            self.ext_resources.extend(ext_resources)
        if sub_resources:
            self.sub_resources.extend(sub_resources)
        for k,v in kwargs.items():
            if not (hasattr(self,k)):
                raise AttributeError(k, obj=self, name=k)
            setattr(self,k,v)
        return self

    def __eq__(self, value):
        if not isinstance(value, ResourceTres):
            return super().__eq__(value)
        return all((
            value.type == self.type,
            value.format == self.format,
            value.script == self.script,
            value.script_class == self.script_class,
            value.properties == self.properties,
            value.ext_resources == self.ext_resources,
            value.sub_resources == self.sub_resources,
        ))
    
class ExtResource():
    context : StructContext

    type : CollectionKey[str]
    uid : CollectionKey[str]
    path : CollectionKey[str]
    id : CollectionKey[int]

    def __setup__(self):
        self.context = StructContext()
        self.type = CollectionKey(self, "type", None)
        self.uid = CollectionKey(self, "uid", None)
        self.path = CollectionKey(self, "path", None)
        self.id = CollectionKey(self, "id", None)
    
    def __init__(self, type:str, uid:str, path:str, id:int,):
        self.__setup__()
        self.type.set(type)
        self.uid.set(uid)
        self.path.set(path)
        self.id.set(id)

    def __colkeys__(self,):
        return (
            self.uid,
            self.path,
            self.id,
            # self.type
            )
    def __repr__(self):
        return f"{self.__class__.__name__}({self.type},{self.id},{self.path},{self.id})"

    def __eq__(self, value):
        if isinstance(value, ExtResource):
            return all((
                self.type == value.type,
                self.uid == value.uid,
                self.path == value.path,
                self.id == value.id
            ))
        return super().__eq__(value)

class ExtResourceCollection(Collection):
    unique_keys = ("uid","path","id")
    # shared_keys = ("type",)

    def key_matcher(self, addr:str):
        if addr.startswith("res://"):
            return "path"
        if addr.startswith("uid://"):
            return "uid"
        return "id"

class ExtResourceRef(Reference, GdValue): 
    ''' Routed reference ID '''
    key_categories = ("id",)
    typing : GdType

    def __init__(self, address=None, cached_value=None, typing=None):
        self.typing = typing
        super().__init__(key_id="id", address=address, cached_value=cached_value)

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.context.callback("resource",self._on_context_updated)
        
    def _on_context_updated(self, value:Any):
        if value is None:
            self.set_collection(None)
        else:
            value : _Resource
            self.set_collection(value.ext_resources)
