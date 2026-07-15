from __future__ import annotations

from typing import Any, Type
from weakref import ReferenceType as _WeakReferenceType, ref as weakref

from fsspec import AbstractFileSystem

from .context import StructContext as _StructContext
from .collections import Collection, CollectionKey, CollectionRef
from .property_collection import PropertyCollection
from .gdtype import GdType

from .transformer import (
    Transformer as _Transformer, 
    TransformerRuleset as _TransformerRuleset, 
    TransformerModule as _TransformerModule, 
    Context as _TransformerContext,
    TERMINAL as _TERMINAL,
    DEFAULT as _DEFAULT
)

class StructContext(_StructContext):
    _slots_ = ("project","file","resource","subresource")
    project : Project
    file : File
    resource : Resource
    subresource : Resource

class Project():
    file_system : AbstractFileSystem
    
    file_types : list[Type[File]]

    types : Collection[GdType] #GdType
    files : Collection[File]
    resources : Collection[Resource]

    def __setup__(self):
        self.context = StructContext(project=self)
        self.types = Collection("typeid", context=self.context)
        self.files = Collection("filepath", context=self.context)
        self.resources = Collection("uid", context=self.context) 
        self.settings = FileRef("res://project.godot", context=self.context)

    def __init__(self, file_system:AbstractFileSystem, file_types:list[Type[File]]):
        self.__setup__()
        self.file_system = file_system
        self.file_types = file_types

class ResourceRef(CollectionRef): #Key is UID
    def __setup__(self):
        self.context = _StructContext()
        def _callback(x: Project):
            if x is None: 
                self.set_col(None)
            else:
                self.set_col(x.resources)
        self.context.callback("project", callback=_callback)
    def __init__(self, key = None, col = None, cache = None, context = None):
        self.__setup__()
        super().__init__(key, col, cache)
        if context:
            self.context.set_extends(context)

class FileRef(CollectionRef):
    def __setup__(self):
        self.context = _StructContext()
        def _callback(x: Project):
            if x is None: 
                self.set_col(None)
            else:
                self.set_col(x.files)
        self.context.callback("project", callback=_callback)
    def __init__(self, key = None, col = None, cache = None, context = None):
        self.__setup__()
        super().__init__(key, col, cache)
        if context:
            self.context.set_extends(context)

class GdTypeRef(CollectionRef):
    def __setup__(self):
        self.context = _StructContext()
        def _callback(x: Project):
            if x is None: 
                self.set_col(None)
            else:
                self.set_col(x.types)
        self.context.callback("project", callback=_callback)
    def __init__(self, key = None, col = None, cache = None, context = None):
        self.__setup__()
        super().__init__(key, col, cache)
        if context:
            self.context.set_extends(context)


class File():
    ''' Grouping/Ownership for Resources in memory. '''
    _extensions_ : tuple[str]
    context : StructContext    

    is_loaded : bool = False
    
    filepath : CollectionKey[str]
    cached_uid : str|None = None

    meta_properties : PropertyCollection
    
    resource : ResourceRef

    # Cached only during import on context object, then deleted
    # _cached_sub_resource_map : dict[str, DeferedReference[Resource]]
    # _cached_ext_resource_map : dict[str, DeferedReference[Resource]]
    
    def __setup__(self):
        self.filepath=CollectionKey(self)
        self.context = StructContext(file=self)
        self.resource = ResourceRef(context=self.context)
        self.meta_properties = PropertyCollection(context=self.context)

    def __init__(self, filepath:str):
        self.__setup__()
        self.filepath.set_key(filepath)

    @classmethod
    def construct(cls, filepath, /, cached_uid:str|None=None, resource:str|Resource=None, properties:dict|None=None, _resource_defer_add:bool=False)->File:
        self = cls(filepath)

        if cached_uid:
            self.cached_uid = cached_uid

        if isinstance(resource,Resource):
            self.resource.set_cached(resource)
            if _resource_defer_add:
                def _callback(project:Project):
                    if not (resource in project.resources):
                        project.resources.append(resource)
                self.context.callback("project", _callback, once=True)
        elif isinstance(resource,str):
            self.resource.set_key(resource)
        elif (resource is None) and cached_uid:
            self.resource.set_key(cached_uid)

        if properties:
            self.meta_properties.update(properties)
        
        return self
    
    def create(self,):
        raise NotImplementedError()
    def read(self,):
        raise NotImplementedError()
    def update(self,):
        raise NotImplementedError()
    def delete(self,):
        raise NotImplementedError()
    def move(self,):
        raise NotImplementedError()
    
    def _on_created(self,):
        raise NotImplementedError()
    def _on_readed(self,):
        raise NotImplementedError()
    def _on_updated(self,):
        raise NotImplementedError()
    def _on_deleted(self,):
        raise NotImplementedError()
    def _on_moved(self,):
        raise NotImplementedError()

class Resource():
    ''' Any object that *can* be converted to and from disk '''
    context : StructContext

    is_file : bool = False
    uid : CollectionKey[str]
    file : FileRef|None = None
    subresources : Collection[Resource]
    ## Resource id, None if SubResource (Ie without file) or removed from resources

    ## Subresource id *only* for r/w dif stability & instance overlays. Changed on duplication
    id : CollectionKey[str|int] = None
    
    type : GdTypeRef
    script_type : GdTypeRef

    properties : PropertyCollection

    instance : ResourceRef|None = None
    instance_is_editable : bool = False
    overlay : Resource|None = None
    # overlay being thin means no changes have been made locally to properties
    # overlayed objects that are not an instance cannot change anything but their properties, and add children.


    def set_overlay(self, overlay:Resource|None, thin:bool=True):
        if overlay is None:
            self.overlay = overlay
            self.properties.set_overlay(None)
        else:
            self.overlay = overlay
            self.properties.set_overlay(overlay.properties)

    def set_instance(self, file:File|str|None, editable:bool=False):
        if isinstance(file, str):
            self.instance.set_key(file)
        elif isinstance(file, File):
            self.instance.set_cached(file)
        self.instance_is_editable = editable
        # self.construct_instance()

    def construct_instance(self):
        file = self.instance.get()
        if file is None:
            raise FileNotFoundError(self.instance.key)
        res = file.resource.get()
        if res is None:
            raise ResourceWarning("resource was not found!")
        self.set_overlay(res)

        c = _InstanceCopyContext()
        c.cached_local.set(...)
        ## As in cached transfomrations/matches??
        ## What about the subresources local that arnt known yet that should be the overlay source ??
        ## Use cache from file import, otherwise discover?
        ## Reconsider use of notating subresources in collection on parent resource.
        instance_copy.transform_tree(c, (self,res))


    def set_type(self, type:GdTypeRef):
        raise NotImplementedError()

    def set_script_type(self, script_type:GdTypeRef):
        raise NotImplementedError()

    def __setup__(self,):
        self.context = StructContext(subresource=self)
        self.uid = CollectionKey(self)
        self.id = CollectionKey(self)
        self.instance = FileRef(context=self.context)
        self.file = FileRef(context=self.context)
        self.properties = PropertyCollection(context=self.context)
        self.type = GdTypeRef(context=self.context)
        self.script_type = GdTypeRef(context=self.context)

        def _callback(k, file:File|None):
            if (file is None):
                try: del self.context.file
                except: pass
                try: del self.context.resource
                except: pass
            else:
                self.context.resource = self
                self.context.file = file
        self.file.updated.connect(_callback)

    def __init__(self):
        self.__setup__()

    def setup_as_file(self, uid:str=None, file:str|File=None):

        self.context.resource = self
        self.subresources = Collection("id", context=self.context)

        self.uid.set_key(uid)

        if isinstance(file, File):
            self.file.set_cached(file)
        else:
            self.file.set_key(file)

        if (self.context.project is None):
            self.context.callback("project", lambda x: x.project.resources.append(self))
        else:
            self.context.project.resources.append(self)

        self.is_file = True

    def remove_as_file(self):
        self.is_file = False
        self.context.project.resources.remove(self)

        items = tuple(self.subresources.data)
        self.subresources.clear()
        del self.context.resource

        if self.context.resource:
            for i in items:
                i.context.set_extends(self.context.resources.context)

        self.uid.set_key(None)
        self.file.set_key(None)

    @classmethod
    def construct(cls, /, id:str=None, uid:str=None, file:File=None, type:str|GdType=None, script_type:str|GdType=None, properties:dict|None=None, instance:str|File|Resource=None, inst_editable:bool=None, _instance_direct:bool=False, overlay:Resource=None, subresources:list[Resource]=None):
        self = cls()
        self.context.callback("resource", lambda x: setattr(self, "owner", x) )

        if id:
            self.id.set_key(id)

        if type:
            self.set_type(type)

        if script_type:
            self.set_script_type(script_type)

        if uid or file:
            self.setup_as_file(uid=uid, file=file)
            if subresources:
                self.subresources.extend(subresources)
        else:
            assert subresources is None

        if isinstance(instance, str) or isinstance(instance, File):
            self.set_instance(instance)
        elif isinstance(instance, Resource) and _instance_direct:
            self.set_overlay(instance)
        elif not (instance is None):
            raise Exception(instance)

        elif overlay:
            self.set_overlay(overlay)

        if properties:
            self.properties.update(properties)


        
        return self

class Node(Resource):
    owner : Node|None
    
    parent : Node|None
    name : CollectionKey[str]
    children : Collection[Node]
    
    def __setup__(self):
        super().__setup__()
        self.name = CollectionKey(self)
        self.children = Collection("name", context=self.context)

    @classmethod
    def construct(cls, /, name:str=None, id:int = None, uid = None, file = None, type = None, script_type = None, properties = None, instance = None, inst_editable = None, overlay = None, _parent:str|Node=None, _index:int|None=None, _children:list[Node]=None, _defer_nodetree=True):
        self = super().construct(id, uid, file, type, script_type, properties, instance, inst_editable, overlay)

        self.context.callback("resource", lambda x: setattr(self,"owner",x) )

        if not(name is None):
            self.name.set(name)
        elif not(type is None):
            self.name.set(type.name)
        else:
            self.name.set("Node")

        if _defer_nodetree:
            if not(_parent is None):
                if isinstance(_parent, str):
                    self.context.callback("resource", lambda x: x.get_node(_parent).append(self,_index) )
                else:
                    self.context.callback("resource", lambda x: _parent.append_child(self, _index) )
            if not(_children is None):
                    self.context.callback("resource", lambda x: self.extend_children(_children) )
        else:
            if not(_parent is None):
                assert not isinstance(_parent,str)
                _parent.append_child(self, _index)
            if not(_children is None):
                self.extend_children(_children)

        return self
    

class _InstanceCopyContext(_TransformerContext):
    pass
class InstanceCopy(_TransformerModule):
    _keys = (_DEFAULT,)
    def transform(self, c, node):
        raise NotImplementedError()

instance_copy = _Transformer((_TransformerRuleset("InstanceCopy", (InstanceCopy,)),),identifier="InstanceCopy")