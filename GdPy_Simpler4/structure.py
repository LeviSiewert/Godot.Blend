from __future__ import annotations

from weakref import ref as weakref, ReferenceType as WeakReferenceType
from typing import Any, Self, Callable
from enum import Enum

from .collection import Collection, CollectionKey
from .context import Context
from .signals import Signal

class _UNSET:...

class _ProjectIO[K:str|int]():
    update_references: Signal[Callable, Callable, None|Any|_ItemIO]

class _ResourceIO[K:str|int]():
    some_collection : Collection

class _ItemIO[K:str|int]():
    some_key : CollectionKey[K]
    fullfill_references: Signal[Self, RefType, K]
    def provide_reftype_key(self)->tuple[None|RefType, None|K]: ...

class RefType(Enum):
    ## Free for first fullfillment
    DEFER        = None
    ## Locked reference types;
    RID          = ("project" , "resources"    , False)
    FILE         = ("project" , "files"        , False)
    ## Unlocked Reference types;
    RESOURCE     = ("project" , "resources"    , True ) # -> ext_resource when saved, sub_resource when embedded
    EXT_RESOURCE = ("resource", "ext_resources", True ) # -> Subresource when embedded
    SUB_RESOURCE = ("resource", "sub_resources", True ) # -> resource | ext_resource when saved/coppied as.

class StructReference[K:str|int, V:_ItemIO|Any]():
    ''' A reference type that can limited convert between types and be defered, requires resolving via context arguments '''
    context : Context

    sref : None|V = None 
    wref : WeakReferenceType[V] = weakref(_UNSET())
    ref_type : RefType = RefType.DEFER
    key : str|None       ## Key for Collection

    def __setup__(self):
        self.context = Context()
        self.context.callback("project", self._on_project_updated, weak=True)


    p_cached : WeakReferenceType = weakref(_UNSET())
    def _on_project_updated(self, _, project:_ProjectIO|Any|None):
        p_cached : _ProjectIO|Any|None = self.p_cached()
        if not (p_cached is None):
            p_cached.update_references.disconnect(self._on_update_references)

        if not (project is None):
            self.p_cached = weakref(project)
        else:
            del self.p_cached

        if not (project is None):
            project.update_references.connect(self._on_update_references, weak=True)

    def __init__(self, /, key:K|None=None, ref_type:RefType=RefType.DEFER, obj:V|None=None, ):
        self.__setup__()

        if not (key is None):
            assert not (ref_type is None)
            assert (obj is None)

        if not (obj is None):
            assert (key is None)

        self.ref_type = ref_type
        self.key = key 

        if (obj is None):
            return
        _ref_type, _key = obj.provide_reftype_key()
        if (_ref_type is None):
            obj.fullfill_references.connect(self._on_fullfill_references, once=True, weak=True)
            self.sref = obj
        else:
            self._on_fullfill_references(_ref_type, _key)
            self.wref = weakref(obj)


    def _on_fullfill_references(self, ref_type:RefType, key:K):
        if self.ref_type == RefType.DEFER:
            self.ref_type = ref_type

        elif not (self.ref_type[1] != ref_type[1]):
            if not self.ref_type[2]: #Locked reference type
                return
            self.ref_type = ref_type

        self.key = key

        if not (self.sref is None):
            self.wref = weakref(self.sref)
            self.sref = None

    def _on_update_references(self, filter:Callable, updater:Callable, new_object:None|V=None ):
        if not filter(self):
            return
        obj :_ItemIO= self.sref if (not (self.sref is None)) else self.weakref()

        if not (obj is None):
            obj.fullfill_references.disconnect(self._on_fullfill_references)

        updater(self)

        if (self.key is None) and (not (new_object is None)):
            self.sref = new_object
            new_object.fullfill_references.connect(self._on_fullfill_references, once=True, weak=True)

        elif not (new_object is None):
            self.wref = weakref(new_object)

    def resolve[D:Any|None](self, context:Context, default:D=None)->D|V:
        if (self.ref_type is RefType.DEFER):
            if (self.sref is None):
                return default
            return self.sref

        scope : _ResourceIO = getattr(context,self.ref_type[0], None)
        if scope is None:
            return default

        col : Collection = getattr(scope, self.ref_type[1], None)
        if col is None:
            return default

        item : _ItemIO = col.get(self.key, None)
        if item is None:
            return default

        if not (self.sref is None):
            self.sref = None
            self.wref = weakref(item)

        return item
        

    # def _on_collection_append():
    #     ## Testing for fullfillment to attach update_reference to?
    #     pass