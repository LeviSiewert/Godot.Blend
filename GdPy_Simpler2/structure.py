from __future__ import annotations

from collections import UserDict
from typing import Any

from .core import Users, Signal, Context

class Collection[K:str|int,V:Resource|File](UserDict):
    data : dict[K,CollectionWrapper[V]]
    owner : None|Project|Resource|File|Any = None ## Attach/set if not None
    user : None|Project|Resource|File|Any = None ## Attach/set if not None
    
class CollectionWrapper[T]():...

class CollectionKey[K:str|int, V:Any]():
    ''' External Controller for a Collection's object '''
    src : V
    col : Collection

class Promise[T:Any]():
    ''' Replace this object with what is passed out
    Noteable: Inherited by Resource to replace Resource w/ CollectionWrapper[Resource]
    '''
    _promise_replace : Signal[T]
    def __setup__(self,):
        self._promise_replace = Signal(self)
    def __init__(self):
        self.__setup__()
class _StructuralPromise(Promise):
    ''' Collection promise with default representation '''
    context : Context
    scope : str 
    attr : str 
    id : int|str
    default_rep : str

    def __init__(self, scope, attr, id, default_rep:str):
        self.__setup__() 
        self.scope = scope
        self.attr = attr
        self.id = id
        self.default_rep = default_rep
        self.context = self.context()
        self.context.callback(scope, self._test_replace, weak=True)

    def _test_replace(self, obj:Any|None):
        if obj is None:
            return
        col : Collection = getattr(obj, self.attr)
        val : CollectionWrapper = col.promise(id)
        if (val._w_obj is None):
            val.replace.connect(self.replace, weak=True)
        else:
            self.replace(val)
def SubResource(id:str): return _StructuralPromise("Resource", "sub_resources", id, f"SubResource({id})")
def ExtResource(id:str): return _StructuralPromise("Resource", "ext_resources", id, f"ExtResource({id})")
def RID(id:str): return _StructuralPromise("Project", "resources", id, f"RID({id})")

class Properties(UserDict):
    ''' Attach context w/a ?? '''
    ...

class ExtResource():
    id : CollectionKey[str]
    file : File
    resource : Resource

class Resource():
    ''' When context is set,'''
    context : Context
    owner : Resource|Project|None
    users : Users

    id : CollectionKey[str]
    properties: Properties

    instance : None|ExtResource = None
    overlay : None|Resource = None

    ## as File
    uid : None|CollectionKey[str] = None
    file : None|File = None
    ext_resources : None|Collection[str,'ExtResource'] = None
    sub_resources : None|Collection[str,'Resource'] = None

class Node():
    owner : Project|Node|None

    ## As File
    nodes : Collection[int,'Node']

    ## As all:
    unique_id : CollectionKey[int]
    name : CollectionKey[str]
    children : Collection['Node']

class File():
    owner : Project
    users : Users
    path : CollectionKey[str]
    resource : None|Resource

class Project():
    pass