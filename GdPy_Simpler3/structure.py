from __future__ import annotations
from typing import Any, Self, Callable
from weakref import ReferenceType, ref as _wref
from collections import UserDict

from .signal import Signal, _UNSET
from .context import Context as _Context
from .collection import CollectionKey, Collection

from enum import Enum


class Context(_Context):
    _slots_ = ("project", "resource", "root", "properties")


## Abstract type definitions used for display and type verification;
class GdDefSignal():...
class GdDefProperty():...
class GdDefType():
    id : CollectionKey[str]
    extends : None|Self = None

    properties : dict[str, GdDefProperty]
    signals : dict[str, GdDefSignal]

    def extends_chain(self, depth_first:bool):
        if (self.extends is None):
            yield self
            return
        if depth_first:
            yield from self.extends.get(self.context).extends_chain(depth_first)
            yield self
            return
        yield self
        yield from self.extends.get(self.context).extends_chain(depth_first)

    ...

# class GdDefType:

class _DynamicPromise[T:Any]():
    def resolve[D:Self|Any](self, context:Context, default:D=_UNSET)->Self|T:
        raise NotImplementedError()

class ResourceRefType(Enum):

    RID = ("project", "resources", True)
    File = ("project", "files", True)
    TypeDef = ("project", "types", True)

    Resource = ("project", "resources", False)
    SubResource = ("resource", "sub_resources", False)
    ExtResource = ("resource", "ext_resources", False)


class ResourceRef[S:Any,T:Any](_DynamicPromise):
    ''' Generic dynamic structural promise, as Resource, SubResource and ExtResource should be interchangeable'''
    context : Context

    swapped : Signal

    scope : str
    _scope_cached : ReferenceType[S] = _wref(_UNSET())
    _scope_locked = False

    col : str
    key : str

    def __init__(self, ref_type:ResourceRefType, key:str):
        self.context = Context()
        self.context.element_changed.connect(self._on_scope_updated, filter=lambda elem,_: self.scope == elem )

        self.scope = ref_type[0]
        self.col = ref_type[1]
        self._scope_locked = ref_type[2]
        self.key = key

    def resolve[D:Self|Any](self, context:Context, default:D=_UNSET)->Self|T:
        s = getattr(context, self.scope, _UNSET)
        if s is _UNSET: 
            return default

        c = getattr(s, self.col, _UNSET)
        if c is _UNSET: 
            return default

        i = c.get(self.key, _UNSET)
        if i is _UNSET: 
            return default
        
        return i
        
    def _on_scope_change(self, _, scope:None|S):
        cached_scope = self._scope_cached() 

        if scope is cached_scope:
            return

        if not (cached_scope is None):
            cached_scope.update_promises.disconnect(self._on_update_promises)
            
        if not (scope is None):
            scope.update_promises.connect(self._on_update_promises, filter = lambda s,c,k,*_: all((self.scope == s, self.col == c, self.key == k)) )
            self._scope_cached = _wref(scope)
        else:
            self._scope_cached = _wref(_UNSET())

    def _on_update_promises(self, _s,_c,_k, scope, col, key):
        if self._scope_locked and (_s != scope):
            return
        self.scope = scope
        self.col = col
        self.key = key
        if _s != scope:
            self._on_scope_change(scope, getattr(self.context,scope))

class ResourceRefProperty[T:Any|None]():
    ''' Store original until defered_promise is called, then replace w/ ResourceRef '''

    ref : ResourceRef

    def __init__(self, context:Context, type:ResourceRefType):
        self.context = context
        self.ref = ResourceRef(type)

    _resource : None|ResourceRef[T]|T = None
    _resource_cached : ResourceRef[T]

    def __get__(self)->None|T:
        if self._resource is None: 
            return None
        elif isinstance(self._resource, Resource):
            return res
        res = self._resource.resolve(self.context, None)
        if not (res is None):
            self._resource_cached = _wref(res)
        return res

    def __set__(self, val:None|Resource|ResourceRef[Resource])->None:
        ''' Flow is: defered_promise signal connection, store cache, connect/disconnect '''

        if self.resource is val:
            return

        if not (self._resource_cached() is None):
            self._resource_cached().defered_promise.disconnect(self._on_defered_promise, not_exist_ok=True)

        if (val is None):
            self._resource_cached = _wref(_UNSET)
            self.resource_updated(val)
            return

        elif isinstance(val, Resource):
            self._resource_cached = _wref(val)
            val.defered_promise.connect(self._on_defered_promise, once=True, weak=True)
            self._resource = val
            val._referenced_callback(self.context)
            self.resource_updated(val)

        elif isinstance(val, _DynamicPromise):
            val = copy(val)

            res = val.resolve(self.context)
            ## TODO: Disconnect cases w/ local self._resource_cached w/a 
            if not (res is None):
                self._resource_cached = _wref(res)
            self._resource = val

        else:
            raise TypeError()
        


class NodeRef(_DynamicPromise):
    ''' Short term; only update from changes in originating scene & localize ref in last scene
    longer term: propigation of all references in tree changes? 
    '''

    context : Context

    scope = "resource"

    def __init__(self, path:str):
        self.context = Context()
        self.path = path
        super().__init__()

    def resolve[D:Self|Any](self, context:Context, default:D=_UNSET)->Self:
        raise NotImplementedError()


class Project():
    context : Context

    resources : Collection[str, Resource]
    files : Collection[str, File]
    types : Collection[str, GdDefType]

    update_promises : Signal[str,str,str, str,str,str] #(Ref, Scope,Key) -> (Ref,Scope,Key)

    def __setup__(self):
        self.context = Context(project=self)

        self.update_promises = Signal(self)

        self.resources = Collection(key="uid",context=self.context)
        self.files = Collection(key="path",context=self.context)
        self.types = Collection(key="uid",context=self.context)

    def __init__(self):
        self.__setup__()



class File:
    context : Context

    path : CollectionKey[str]
    file : ResourceRefProperty[Resource]

    def __init__(self, resource:None|Resource=None):
        self.__setup__()
        self.resource = resource

    def __setup__(self):
        self.context = Context(file = self)
        self.file = ResourceRefProperty(self.context, ResourceRefType.File)
        self.path = CollectionKey()
        self.resource = ResourceRef(ResourceRefType.File, None)

    def _on_defered_promise(self, value):
        self.resource = value

    defered_promise : Signal[Self]

    def _referenced_callback(self,context:Context):
        ''' attach to context w/a '''

    def _dereferenced_callback(self,context:Context):
        pass 

class Resource:
    context : Context

    uid : CollectionKey[str]
    file : ResourceRefProperty[File]
    sub_resources : None|Collection[Resource]
    ext_resources : None|Collection[ExtResource]

    id : CollectionKey[str]
    properties : Properties

    defered_promise : Signal[Self]

    def __setup__(self):
        self.defered_promise = ()
        self.context = Context(subresource=self)
        self.file = ResourceRefProperty(self.context, ResourceRefType.File)

    def __init__(self, id:str|None=None, uid:str|None=None, file:File|None=None):
        self.__setup__()
        self.id = CollectionKey(id)

        if (uid or file):
            self.context.resource = self
            self.uid = CollectionKey(uid)
            self.file = file            
            self.sub_resources(context=self.context, key="id")
            self.ext_resources(context=self.context, key="id")
            # if resource:=self.context.resource:
            #     resource.update_promises(self, ) 
            

    def _referenced_callback(self,context:Context):
        ''' attach to context w/a '''

    def _dereferenced_callback(self,context:Context):
        pass 

class Node():

    name : CollectionKey[str]
    unique_id : CollectionKey[int]

# class Properties[K:str,V:Any](UserDict):
#     ''' Get localizes dynamic promises, and defaults to overlay.get when allowable. 
#     if the overlay.get is a DynamicPromise[ExtResource], resolve foreign
#     if the overlay.get is a DynamicPromise[SubResource], try to resolve it locally first in chain, then resolve backwards.
#     if the overlay.get is a DynamicPromise[Node] or DynamicPromise_NodePath, get the relative path within it's context and localize to it's root's first instance up the node tree
#         - consider caching fullpath & root
#     '''
#     context : Context
#     overlay : None|Self = None

#     key_set : Signal[K,V]
#     key_rem : Signal[K,V]
#     key_updated : Signal[K,V]

#     def set_overlay(self, overlay:None|Self=None, supress_updates:bool=False):
#         o_items = dict(self.items())
#         if not (self.overlay is None):
#             self._disconnect_overlay(self.overlay)

#         self.overlay = overlay

#         if not (self.overlay is None):
#             self._connect_overlay(self.overlay)

#         if supress_updates:
#             return
#         self.overlay_updated()

#         n_items = dict(self.items())

#         added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
#         removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
#         changed = {k:v for k,v in n_items.items() if (not (n_items.get(k,None) is o_items.get(k,None)))}

#         for k,v in added.items():
#             self._on_overlay_key_set(k,v)

#         for k,v in removed.items():
#             self._on_overlay_key_rem(k,v)

#         for k,v in changed.items():
#             self._on_overlay_key_updated(k,v)

#     def _connect_overlay(self, overlay):
#         overlay.key_set.connect(self._on_overlay_key_set, weak=True)
#         overlay.key_rem.connect(self._on_overlay_key_rem, weak=True)
#         overlay.key_updated.connect(self._on_overlay_key_updated, weak=True)
#     def _disconnect_overlay(self, overlay):
#         overlay.key_set.disconnect(self._on_overlay_key_set)
#         overlay.key_rem.disconnect(self._on_overlay_key_rem)
#         overlay.key_updated.disconnect(self._on_overlay_key_updated)


#     def _on_overlay_key_set(self, k, v): ...
#     def _on_overlay_key_rem(self, k, v): ...
#     def _on_overlay_key_updated(self, k, v): ...
    

#     def _fmt_res(self, src:Self, item:Any|DynamicPromise, localize:bool=True, resolve:bool=True):
#         if isinstance(item, DynamicPromise): 
#             if localize and resolve:
#                 item = item.resolve(self.context)
#             elif resolve:
#                 item = item.resolve(src.context)
#         return item

# class Resource():
#     context : Context

#     id : CollectionKey[str]
#     properties : Properties

#     instance : None|Self|DynamicPromise[Self] = None
#     overlay : None|Self|DynamicPromise[Self] = None
#     # _users : list[ReferenceType[Resource|Node]]

#     GdDefType : None|GdDefType|DynamicPromise[GdDefType] = None

#     uid : CollectionKey[str]
#     file : DynamicPromise[File]|File
#     sub_resources : Collection[Resource]
#     ext_resources : Collection[ExtResource]

#     def is_subresource():...

#     def set_instance(self, instance:File):...
#     def embed_instance():...

#     def set_overlay(self, overlay:Self):...
#     def _embed_overlay():...
#     def _is_overlay_thin():...

#     def set_gdtype(self, gdtype:GdDefType):...
#     def get_gdtype_errors():...
#     def _resolve_gdtype_errors():...

#     def get_errors_structure(self,):...

#     def set_promises(self):...
#     def get_promises(self):...
#     def swap_promises(self):...
#     def _on_promises(self, filter:Callable, setter:Callable, depth:str):...

#     def _reference_callback(self, f_context:Context):... # Called by collection, check to integrated structure/set context
#     def _on_project_set(self, project:Project):...
#     def _on_resource_set(self, resource:Resource):...




# class GdSignal():
#     context : Context
#     fr : DynamicPromise[Node]
#     to : DynamicPromise[Node]
#     ...

# class Node(Resource):
#     nodes : Collection[int, Node]
#     children : Collection[str, Node]

#     connections : GdSignal

# class ExtResource():
#     context : Context
#     id : CollectionKey[str]
#     _resource : DynamicPromise[Resource]|Resource 
#     _file : DynamicPromise[File]|File