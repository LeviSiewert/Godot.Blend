from __future__ import annotations

from weakref import ref, ReferenceType as _RefType
from string import ascii_letters
from typing import Any, Iterable

from .context import StructContext
from .signals import Signal

import random

class _UNSET:...

class CollectionKey():
    collection : Collection
    
    src : Any
    key : str|_UNSET
    key_updated : Signal[str]

    def __setup__(self,):
        self.key_updated = Signal()

    def __init__(self, src, key:str=_UNSET):
        pass

    def set(self, key):
        if self.collection:
            return self.collection.set(key=key, value=self.source)
        self.key = key
        self.key_updated(key)

    def get(self):
        return self.key
    
    def __eq__(self, value:Any):
        if isinstance(value,str):
            return value == self.key
        
        if isinstance(value, CollectionKey):
            return all((
                self.key == value.key
            ))

        return super().__eq__(value)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.key})"

class CollectionRef[T:Any]():
    ''' Weak Caching Reference, context is used to find the collection. '''

    collection : Collection
    context : StructContext
    
    cached_key : str = None
    cached_object : _RefType[Any] = None

    def __setup__(self,):
        self.context = StructContext()
        self.context.callback('...', lambda x: self.set_collection(x))
        ## Override calback with scope & collection reference

    def __init__(self, key:str|None=None, obj:T|None=None, context:StructContext|None=None):
        self.__setup__()
        self.store_key(key)
        self.store_obj(obj)
        self.context.set_extends(context)


    def get[D](self, default:D=_UNSET)->T|D:
        ...

    def search(self):
        ...


    def set_collection(self, col:Collection[T]|None):
        ...


    def store_key(self, key:str|None):
        ...

    def store_obj(self, obj:T|None):
        ...


    def is_valid(self,)->bool:
        ...


class Collection[T:Any]():
    ''' A collection of objects that are self-keyed, and through context can be soft-referenced by a CollectionRef 
    Self keying done through a CollectionRef.
    argued key_attr is what is used to request the CollectionKey from the object
    '''

    context : StructContext
    data : list[T]
    refs : list[CollectionRef]

    def __setup__(self,):
        self.context = StructContext()

    def __init__(self, key_attr:str, context:StructContext):
        self.__setup__()
        self.context.set_extends(context)
        self.key_attr = key_attr


    def append(self, val:T):
        ...

    def remove(self, val:T):
        ...

    def duplicate(self, val:T)->T:
        ...

    def resolve_key_collision(self, k, l:T, r:T):
        ...

    def append_reference(self, ref:CollectionRef):
        ref.set_collection(self)
    def _append_reference(self, ref:CollectionRef):
        ...


    def remove_reference(self, ref:CollectionRef):
        ref.set_collection(None)
    def _remove_reference(self, ref:CollectionRef):
        ...

