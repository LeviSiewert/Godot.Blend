from __future__ import annotations

from weakref import ref as weakref, ReferenceType as WeakReferenceType
from typing import Any, Self, Callable
from enum import Enum

from .collection import Collection, CollectionKey
from .context import Context
from .signals import Signal

class _UNSET:...

class _UpdaterIO[K:str|int]():
    update_references: Signal[Callable, Callable, None|Any|_ItemIO]

class _ResourceIO[K:str|int]():
    some_collection : Collection

class _ItemIO[K:str|int]():
    some_key : CollectionKey[K]
    fullfill_references: Signal[Self, RefType, K]
    def provide_reftype_key(self)->tuple[None|RefType, None|K]: ...

class RefType():
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
    ''' A reference type that can limited convert between types and be defered, requires resolving via context arguments 
    Noteable behavior: 
        - Attaches to context.*.update_references for replacements
        - fullfill_references is a one shot connection 
        - _on_fullfill_references changes the internal strong reference to a weak reference
    
    Intent:
        - If an object is already owned by a scope, short and use that.
        - Items (V) being referenced should be owned by scope, (probably attaching themselves)
        - On object attachement to scope that owns it, fullfill_references is emited to populate references to itself
            ! non scoped owner in structure here could cause bugs, as IDs are relative to scope!
                - In particular cross Resource.sub_resources fullfillment
        - All objects within context, ie higher in the tree, should be *able* to update children's references 

    FUTURE:
        - Warnings around non-uniform reference fullfillment (object provide context on fullfillment?)

        ~ I dont like this implimentation, but it's the best I've come up with so far that fullfills most requirements:
            - Replaceable
            - Godot Analagous
            - Partial Loading allowed
            - Mutable between types
            - Doesnt rely on external container replacement of self
    '''
    context : Context

    sref : None|V = None 
    wref : WeakReferenceType[V] = weakref(_UNSET())
    ref_type : RefType = RefType.DEFER
    key : str|None       ## Key for Collection

    def __setup__(self):
        self.cached = {}
        self.context = Context()
        self.context.element_changed.connect(self._on_element_changed, weak=True)

    cached : dict[str, WeakReferenceType[_UpdaterIO]]

    def _on_element_changed(self, attr:str, element:_UpdaterIO|Any|None):
        if (ref:=self.cached.get(attr,None)) and hasattr(ref, "update_references"):
            ref().update_references.disconnect(self._on_update_references)
            del self.cached[attr]

        if (not (element is None)) and hasattr(element, "update_references"):
            self.cached[attr] = weakref(element)
            element.update_references.connect(self._on_update_references, weak=True)


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
        if (_ref_type is None) or (_ref_type == RefType.DEFER):
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
        if (self.ref_type == RefType.DEFER):
            if (self.sref is None):
                return default
            return self.sref
        elif not (self.sref is None):
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

class StructReferenceProperty[K:str|int, V:Any|None]():
    ref_type : RefType
    attr : str

    def __init__(self, key:str, ref_type:RefType):
        self.attr = key
        self.ref_type = ref_type

    def __set__(self, instance, value:K|V):
        promise : None|StructReference = getattr(instance, self.attr, None)
        if (promise is None) and (value is None):
            return
        elif (promise is None) and isinstance(value,(str,int)):
            setattr(instance, self.attr, StructReference(key=value, ref_type=self.ref_type))
            return
        elif (promise is None): 
            setattr(instance, self.attr, StructReference(obj=value, ref_type=self.ref_type))
            return
        elif (promise.sref is value) or (promise.wref() is value):
            return
        
        promise._on_update_references(lambda r:True, lambda r:..., new_object=value)
        
    def __get__(self, instance, owner)->K|V|StructReference:
        promise : None|StructReference = getattr(instance, self.attr, None)
        if promise is None:
            return None
        return promise.resolve(instance.context, promise)