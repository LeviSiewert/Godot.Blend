from __future__ import annotations
from typing import Any, Self, Callable
from weakref import ReferenceType, ref as _wref
from collections import UserDict

from .signal import Signal, _UNSET
from .context import Context as _Context
from .collection import CollectionKey, Collection




class Context(_Context):
    _slots_ = ("project", "resource", "root", "properties")
    
class DynamicPromise[T:Any]():
    ''' Structural reference, usually to a collection, that is resolved on fetch when in a propcol'''

    cached : ReferenceType[T] = None

    def resolve(self, context:Context)->Self|T:
        raise NotImplementedError()

class _ScopeIO():
    remap_ref : Signal[str,str,str|int, str,str,str|int]
    

class DynamicPromiseStructural[S:_ScopeIO|Any, K:str|int, I:Any](DynamicPromise):
    context : Context

    scope : str # make property to allow signal swapping via getattr(self.context, self.scope)
    cached_scope : ReferenceType[S|None] = _wref(_UNSET())

    col : str
    key : K

    def __setup__(self,):
        self.context = Context()
        self.context.element_changed.connect(self._on_context_element_changed)

    def _reference_callback(self, context:Context):
        self.context.set_extends(context)

    def _dereference_callback(self, context:Context):
        pass

    def _on_context_element_changed(self, elem:str, obj:I):

        if (self.scope != elem): 
            return
        
        c_scope = self.cached_scope()

        if (obj is c_scope):
            return

        if not (c_scope is None):
            c_scope.remap_ref.disconnect(self._on_remap_call)

        if not (obj is None): 
            obj.remap_ref.connect(self._on_remap_call)
            self.cached_scope = _wref(obj)
        else:
            self.cached_scope = _wref(_UNSET)

    def _on_remap_call(self, m_scope:str,m_col:str,m_key:str, scope:str, col:str, key:str):
        if any((self.scope != m_scope, self.col != m_col, self.key != m_key,)):
            return

        self.col = col
        self.key = key
        self.scope = scope
        self._on_context_element_changed(scope, getattr(self.context, scope))

## Gd Type Definitions:

class GdDefProperty:
    ...

class GdDefSignal:
    ...

class GdDefType:
    id : CollectionKey[str]
    extends : None|DynamicPromise[GdDefType] = None

    properties : dict[str, GdDefProperty]
    signals : dict[str, GdDefSignal]

    def extends_chain(self, reverse:bool):...

    ...

## STRUCUTRE:

class Project():
    resources : Collection[str, Resource]
    files : Collection[str, File]
    types : Collection[str, GdDefType] 

class File():
    path : CollectionKey[str]
    resource : DynamicPromise[Resource]|Resource

class Properties[K:str,V:Any](UserDict):
    ''' Get localizes dynamic promises, and defaults to overlay.get when allowable. 
    if the overlay.get is a DynamicPromise[ExtResource], resolve foreign
    if the overlay.get is a DynamicPromise[SubResource], try to resolve it locally first in chain, then resolve backwards.
    if the overlay.get is a DynamicPromise[Node] or DynamicPromise_NodePath, get the relative path within it's context and localize to it's root's first instance up the node tree
        - consider caching fullpath & root
    '''
    context : Context
    overlay : None|Self = None

    key_set : Signal[K,V]
    key_rem : Signal[K,V]
    key_updated : Signal[K,V]

    def set_overlay(self, overlay:None|Self=None, supress_updates:bool=False):
        o_items = dict(self.items())
        if not (self.overlay is None):
            self._disconnect_overlay(self.overlay)

        self.overlay = overlay

        if not (self.overlay is None):
            self._connect_overlay(self.overlay)

        if supress_updates:
            return
        self.overlay_updated()

        n_items = dict(self.items())

        added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
        removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
        changed = {k:v for k,v in n_items.items() if (not (n_items.get(k,None) is o_items.get(k,None)))}

        for k,v in added.items():
            self._on_overlay_key_set(k,v)

        for k,v in removed.items():
            self._on_overlay_key_rem(k,v)

        for k,v in changed.items():
            self._on_overlay_key_updated(k,v)

    def _connect_overlay(self, overlay):
        overlay.key_set.connect(self._on_overlay_key_set, weak=True)
        overlay.key_rem.connect(self._on_overlay_key_rem, weak=True)
        overlay.key_updated.connect(self._on_overlay_key_updated, weak=True)
    def _disconnect_overlay(self, overlay):
        overlay.key_set.disconnect(self._on_overlay_key_set)
        overlay.key_rem.disconnect(self._on_overlay_key_rem)
        overlay.key_updated.disconnect(self._on_overlay_key_updated)


    def _on_overlay_key_set(self, k, v): ...
    def _on_overlay_key_rem(self, k, v): ...
    def _on_overlay_key_updated(self, k, v): ...
    

    def _fmt_res(self, src:Self, item:Any|DynamicPromise, localize:bool=True, resolve:bool=True):
        if isinstance(item, DynamicPromise): 
            if localize and resolve:
                item = item.resolve(self.context)
            elif resolve:
                item = item.resolve(src.context)
        return item

class Resource():
    context : Context

    id : CollectionKey[str]
    properties : Properties

    instance : None|Self|DynamicPromise[Self] = None
    overlay : None|Self|DynamicPromise[Self] = None
    # _users : list[ReferenceType[Resource|Node]]

    GdDefType : None|GdDefType|DynamicPromise[GdDefType] = None

    uid : CollectionKey[str]
    file : DynamicPromise[File]|File
    sub_resources : Collection[Resource]
    ext_resources : Collection[ExtResource]

    def is_subresource():...

    def set_instance(self, instance:File):...
    def embed_instance():...

    def set_overlay(self, overlay:Self):...
    def _embed_overlay():...
    def _is_overlay_thin():...

    def set_gdtype(self, gdtype:GdDefType):...
    def get_gdtype_errors():...
    def _resolve_gdtype_errors():...

    def get_errors_structure(self,):...

    def set_promises(self):...
    def get_promises(self):...
    def swap_promises(self):...
    def _on_promises(self, filter:Callable, setter:Callable, depth:str):...

    def _reference_callback(self, f_context:Context):... # Called by collection, check to integrated structure/set context
    def _on_project_set(self, project:Project):...
    def _on_resource_set(self, resource:Resource):...




class GdSignal():
    context : Context
    fr : DynamicPromise[Node]
    to : DynamicPromise[Node]
    ...

class Node(Resource):
    nodes : Collection[int, Node]
    children : Collection[str, Node]

    connections : GdSignal

class ExtResource():
    context : Context
    id : CollectionKey[str]
    _resource : DynamicPromise[Resource]|Resource 
    _file : DynamicPromise[File]|File