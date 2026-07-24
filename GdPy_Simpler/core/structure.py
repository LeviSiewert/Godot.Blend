from __future__ import annotations

from typing import Any, Type
from weakref import ReferenceType as _WeakReferenceType, ref as weakref

from fsspec import AbstractFileSystem

from .context import StructContext as _StructContext
from .collections import Collection, CollectionKey, CollectionRef
from .property_collection import PropertyCollection, _ResourceFlag, _FileFlag, DelayedReference
from .gdtype import GdType

from .signals import Signal

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

class FileSystemSignalProvider():
    created : Signal[str]
    removed : Signal[str]
    updated : Signal[str]
    deleted : Signal[str]
    moved : Signal[str, str]

    def __setup__(self):
        self.created = Signal(self)
        self.removed = Signal(self)
        self.updated = Signal(self)
        self.deleted = Signal(self)
        self.moved = Signal(self)

    def __init__(self):
        self.__setup__()

class Project():
    file_system : AbstractFileSystem|None
    file_system_signals : FileSystemSignalProvider|None

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

    def __init__(self, file_system:AbstractFileSystem|None=None, signals:FileSystemSignalProvider|None=None, file_types:list[Type[File]]=None, search=True):
        self.__setup__()
        self.file_system = file_system
        self.file_types = file_types
        
        if search:
            assert not (file_system is None)
            self.search()

        if signals:
            assert not (file_system is None)
            self.file_system_signals = signals

    def search(self):
        assert not (self.file_system is None)
        ''' Find all files on disc relevent and populate self.files w/ '''
        raise NotImplementedError()
        

    @classmethod
    def construct(cls, file_system:AbstractFileSystem|None=None, signals:FileSystemSignalProvider|None=None, file_types:list[Type[File]]=tuple(), resources:tuple[Resource]=None, files:tuple[File]=None, search=False):
        self = cls(file_system=file_system, signals=signals, file_types=file_types, search=False)

        if files:
            self.files.extend(files)

        if resources:
            self.resources.extend(filter(lambda x: (x.uid.key or x.file.key or x.file._cached()),  resources))

        if search:
            self.search()

        return self

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

class ExtResource():
    ''' Meta-promise object? '''
    
    updated : Signal[None, Resource]

    def __setup__(self):
        self.context = _StructContext()

    def __init__(self, /, res_id:str, file_id:str, id:str):
        self.__setup__()


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


class File(_FileFlag):
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

class Resource(_ResourceFlag):
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

        c = _InstanceOverlayContext()
        c.existing.set({res.id.key:res for res in self.subresources})
        instance_copy.transform_tree(c, res)

    def copy_overlay(self, existing:dict|None=None):
        c = _InstanceOverlayContext()
        if not (existing is None):
            c.existing.set(existing)
        c.root.set(self)
        return instance_copy.transform_tree(c, self)

    def clone(self, deep=True)->Resource:
        ## Duplicate-collapse entire tree & overlays into simple nodes while localizing references.
        ## Deep: uncertain desired traversal change. Clone all instances would be under default.
        raise NotImplementedError()

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

        def _callback(resource:Resource|None):
            ''' Attach to current resource subresources
            Assumption: Resource ownership should be enforced behaviorally in 
                - PropertyCollection s
                - values.Dictionarys
                - values.Arrays
            '''

            if not (resource is None):
                if not (self.id.col is resource.subresources) and not (self.id.col is None):
                    self.id.col.remove(self)
                    ## Can happen in normal operation... but isn't advisable?
                    ## push warning? To determine.
                if not self in resource.subresources: 
                    resource.subresources.append(self)                    

            elif not (self.id.col is None):
                ## Possible Failure state here? 
                self.id.col.remove(self)

        self.context.callback("resource", _callback)

    def __init__(self):
        self.__setup__()

    def _file_set_callback(self, k,v):
        self.context.file = v

    def setup_as_file(self, uid:str=None, file:str|File=None):

        self.subresources = Collection("id", context=self.context, propigate_context=False)
        self.context.resource = self

        self.uid.set_key(uid)

        self.file.updated.connect(self._file_set_callback) 

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

        try: del self.context.resource
        except: pass

        if self.context.resource:
            for i in items:
                i.context.set_extends(self.context.resources.context)

        self.file.updated.disconnect(self._file_set_callback)
        try: self.context.file
        except: pass
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
                for r in subresources:
                    ## subresources no longer provides context
                    ## later context is swapped on use, such as via properties
                    r.context.set_extends(self.context)
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
    def construct(cls, /, name:str=None, children:tuple[Node]=None, defer_children:bool=True, id = None, uid = None, file = None, type = None, script_type = None, properties = None, instance = None, inst_editable = None, _instance_direct = False, overlay = None, subresources = None):
        self = super().construct(id, uid, file, type, script_type, properties, instance, inst_editable, _instance_direct, overlay, subresources)
        ## Order of operations:
        ## Name, children (or attach callback)
        ## everthing else in construct?
        ## if not file, assert no subresources? 
        return self

    # @classmethod
    # def construct(cls, /, name:str=None, id:int = None, uid = None, file = None, type = None, script_type = None, properties = None, instance = None, inst_editable = None, overlay = None, _parent:str|Node=None, _index:int|None=None, _children:list[Node]=None, _defer_nodetree=True):
    #     self = super().construct(id, uid, file, type, script_type, properties, instance, inst_editable, overlay)

    #     self.context.callback("resource", lambda x: setattr(self,"owner",x) )

    #     if not(name is None):
    #         self.name.set(name)
    #     elif not(type is None):
    #         self.name.set(type.name)
    #     else:
    #         self.name.set("Node")

    #     if _defer_nodetree:
    #         if not(_parent is None):
    #             if isinstance(_parent, str):
    #                 self.context.callback("resource", lambda x: x.get_node(_parent).append(self,_index) )
    #             else:
    #                 self.context.callback("resource", lambda x: _parent.append_child(self, _index) )
    #         if not(_children is None):
    #                 self.context.callback("resource", lambda x: self.extend_children(_children) )
    #     else:
    #         if not(_parent is None):
    #             assert not isinstance(_parent,str)
    #             _parent.append_child(self, _index)
    #         if not(_children is None):
    #             self.extend_children(_children)

    #     return self


### INSTANCE-OVERLAY TRANSFORMER ###

from contextvars import ContextVar
from collections import UserDict, UserList
from copy import copy

class _InstanceOverlayContext(_TransformerContext):
    existing : ContextVar[dict[str|int,Resource]]
    converted : ContextVar[dict[Resource,Resource]]
    root : ContextVar[Resource|None]
    def __init__(self):
        super().__init__()
        self.converted = ContextVar("converted", default={})
        self.existing = ContextVar("existing", default={})
        self.root = ContextVar("root", default=None)

class InstanceOverlay_Default(_TransformerModule):
    _keys = (_DEFAULT,)
    def transform(self, c, node):
        return copy(node)

class InstanceOverlay_Refs(_TransformerModule):
    _keys = (CollectionRef,)
    def transform(self, c, node):
        return copy(node)

class InstanceOverlay_Array(_TransformerModule):
    _keys = (UserList,)

    def transform(self, c, node):
        ''' If has any converted children, return copy w/ all items and updated index '''
        yield node
        new = node.__class__()
        new.extend(c.children.get())
        return new

class InstanceOverlay_Dictionary(_TransformerModule):
    _keys = (UserDict,)

    def transform(self, c, node):
        ''' If has any converted children, return copy w/ all items and updated index '''
        yield node
        new = node.__class__()
        new.update(c.children.get())
        return new
        
class InstanceOverlay_Resource(_TransformerModule):
    _keys = (Resource,)
    def transform(self, c, node:Resource):
        ''' Find return already converted w/a, overlay existing w/a, create thin overlay otherwise'''

        if node.is_file and (not (node is c.root.get())):
            ## Fullfilled reference to a resource-file
            ## Structural delimiter
            return node
        
        if not ((converted := c.converted.get().get(node, None)) is None):
            return converted

        if not ((existing := c.existing.get().get(node.id.key, None)) is None):
            existing.set_overlay(node)
            new_node = existing
        else:
            new_node = Resource.construct(
                id = node.id.key,
                type=node.type.key,
                script_type=node.script_type.key,
                overlay=node,
            )

        _existing_props_keys = new_node.properties.keys()

        def filter(k, v)->bool:
            if k in _existing_props_keys:
                return False 
            if isinstance(v, (UserDict, UserList)):
                return v.contains_subresource()
            if isinstance(v, Resource):
                return (not v.is_file)
            return False

        yield {k:v for k,v in node.properties.items() if filter(k,v)}
        new_node.properties.update(c.children.get())

        c.converted.get()[node] = new_node

        return new_node

instance_copy = _Transformer(
    _TransformerRuleset("InstanceOverlay", (
        InstanceOverlay_Default, 
        InstanceOverlay_Refs, 
        InstanceOverlay_Array, 
        InstanceOverlay_Dictionary, 
        InstanceOverlay_Resource,
    )), 
    identifier="InstanceOverlay"
)

# class InstanceOverlay(_TransformerModule):
#     _keys = (_DEFAULT,)
#     def transform(self, c, node):
#         if isinstance(node, Resource):
#             res = yield from self.transform_resource(c, node)
#             return res
#         elif isinstance(node, File):
#             res = yield from self.transform_file(c, node)
#             return res
#         elif isinstance(node, PropertyCollection):
#             res = yield from self.transform_propcol(c, node)
#             return res
#         elif isinstance(node, UserDict):
#             res = yield from self.transform_dictionary(c, node)
#             return res
#         elif isinstance(node, UserList):
#             res = yield from self.transform_array(c, node)
#             return res

#     def transform_resource(self, c, node:Resource):
#         if node.is_file:
#             pass

#     def transform_file(self, c, node:File):
#         return node
#     def transform_propcol(self, c, node):
#         pass
#     def transform_dictionary(self, c, node):
#         pass
#     def transform_array(self, c, node):
#         pass
    

