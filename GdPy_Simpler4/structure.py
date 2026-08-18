from __future__ import annotations

from weakref import ref as wref, ReferenceType as WeakReferenceType
from typing import Any, Self, Callable
from enum import Enum

from .collection import Collection, CollectionKey
from .context import Context
from .signals import Signal

class _ResourceIO[K:str|int]():
    replace_references: Signal[StructReference.RefType, K, StructReference.RefType, K, _IO|Any]
    some_collection : Collection

class _IO[K:str|int]():
    some_key : CollectionKey[K]
    fullfill_references: Signal[Self, StructReference.RefType, K]
    def provide_reftype_key(self)->tuple[None|StructReference.RefType, None|K]: ...

class StructReference[K:str|int, V:_IO|Any]():
    ''' A reference type that can limited convert between types and be defered, requires resolving via context arguments '''

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

    sref : None|V = None 
    wref : None|WeakReferenceType[V] = None
    ref_type : RefType = RefType.DEFER
    key : str|None       ## Key for Collection

    def __init__(self, /, key:K|None=None, ref_type:RefType=RefType.DEFER, obj:V|None=None, ):
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
        else:
            self._on_fullfill_references(_ref_type, _key)


    def _on_fullfill_references(self, ref_type:StructReference.RefType, key:K):
        if self.ref_type == StructReference.RefType.DEFER:
            self.ref_type = ref_type

        elif not (self.ref_type[1] != ref_type[1]):
            if not self.ref_type[2]: #Locked reference type
                return
            self.ref_type = ref_type

        self.key = key

        if not (self.sref is None):
            self.wref = wref(self.sref)
            self.sref = None

    def _on_update_reference(self, filter:Callable, updater:Callable, new_object:None|V, ):
        if not filter(self):
            return
        obj :_IO= self.sref if (not (self.sref is None)) else self.wref()

        if not (obj is None):
            obj.fullfill_references.disconnect(self._on_fullfill_references)

        updater(self)

        if (self.key is None) and (not (new_object is None)):
            self.sref = new_object
            new_object.fullfill_references.connect(self._on_fullfill_references, once=True, weak=True)

        elif not (new_object is None):
            self.wref = wref(new_object)

    def resolve[D:Any|None](self, context:Context, default:D=None)->D|V:
        if (self.ref_type is StructReference.RefType.DEFER):
            if (self.sref is None):
                return default
            return self.sref

        scope : _ResourceIO = getattr(context,self.ref_type[0], None)
        if scope is None:
            return default

        col : Collection = getattr(scope, self.ref_type[1], None)
        if col is None:
            return default

        item : _IO = col.get(self.key, None)
        if item is None:
            return default

        if not (self.sref is None):
            self.sref = None
            self.wref = wref(item)
        

    # def _on_collection_append():
    #     ## Testing for fullfillment to attach update_reference to?
    #     pass