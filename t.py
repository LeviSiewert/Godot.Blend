from __future__ import annotations
from collections import UserDict
from typing import Any, Callable, Generator
from weakref import ReferenceType, ref as _wref
from enum import Enum

class DifAction(Enum):
    DIF = 0 ## Identical local scope, changed children
    SET = 1 ## Replaced child, immutable type.
    ADD = 2 ## New child
    REM = 3 ## Rem child
    RE_KEY = 4 ## Reordered/Rekeyed children. Rekey, append/set new, reorder, finally sub-tree updates.
    # REF_IMPLIED = 5 ## Reference that remains the same, but was implied in changes elsewhere? 

class DifNode[T:Any]():
    ''' Reminder: This will be generated & integrated via tree transformers. '''
    cur : T|None
    new : T|None
    action : DifAction
    children : dict[str,DifNode] | list[DifNode]
    
    

class Signal[T:Any]():
    ''' On call, fwd call to all connected subscribers, disconnect or append arguments based on options'''
    subscribers : list[ReferenceType[Callable]]
    def connect(self, c:Callable, **options)->None:...
    def disconnect(self, c:Callable, **options)->None:...
    def __call__(self, *args, **kwargs):...

class Context():
    ''' Context object, attribute fallback through extends chain. Values set/changed along chain propigate to children. (including removed as None) '''
    _extends : Context
    _slots_ : tuple[str]
    def extend(self, c:Context|None)->None:...
    def callback(self, id:str, c:Callable, **options)->None:...


class Collection[K,V](UserDict):
    ''' Bidirectional dictionary, with allowence of key on object itself '''
    context : Context
    _inverse : dict
    _refs : list[ReferenceType[CollectionRef]] ## References asc with this collection
    
    kv_updated : Signal[K,V]
    
    overlay : Collection

    def __setup__(self):
        self.context = Context()
    def __init__(self, context:Context, object_key_attr:str|None=None, set_context:bool=False, new:Callable|None=None ):
        self.__setup__()
        self.context.extend(context)
        ...

    def __setitem__(self, key:K, item:V)->None:...
    def __getitem__(self, key:K|V)->V|K:...
    def __delitem__(self, key:K|V):...

    def _generate_key(self, obj:V)->K:...
    def _resolve_key_collision(self, key:K, l_obj:V, r_obj:V)->K:...

    def append(self, obj:V):...
    def remove(self, obj:V|K):...
    def replace(self, old:V|K, new:V|K):...

    def new(self, *args, **kwargs)->V:...

    def get(self, key:K, include_overlay:bool=True):...
    def items(self, include_overlay:bool=True)->Generator[tuple[K,V]]:...
    def values(self, include_overlay:bool=True)->Generator[V]:...
    def keys(self, include_overlay:bool=True)->Generator[K]:...

    def set_overlay(self, overlay:Collection|None):...


class CollectionRef[K:str,V:Any]():
    ''' Reference to a collection, collection can be Null.
    Once attached, references are "sticky" by default, switching internal key to match object.
    Otherwise if a cached object is provided and not a key, the key will be found from cached object.
    Behavior such as swapping references must be done on the collection itself.
    TODO:Cases for `key`&`cached` where `self.cached()`!=`self.col[self.key]` and similar must be explored
    '''
    updated : Signal[K,V]
    replace : Signal[V]
    col : Collection
    key : K
    cached : ReferenceType[V] = _wref(object())

    def __init__(self, key, cached:T=None, replace:bool=False):...
    def set_col(self,col:Collection):...
    def set_key(self,key:K):...
    def set_cache(self,cached:V):...
    def get(self,)->V|None:...

class CollectionKeyContextual[K:str]():
    ''' Collection key that can be used by an object to "hold" it's key '''
    updated : Signal[K]
    col : Collection
    def set(self, k:K)->K:...

class _CollectionRefContextual(CollectionRef):
    ''' Collection reference that supports context, with a callback doing `self.set_col(getattr(_scope, _scope_attr, None))` '''
    context : Context
    _scope : str #IE Resource
    _scope_attr : str #IE .subresources
    _replace : bool #IE call signal self.replace

class FileRef(_CollectionRefContextual):
    _scope = "project"
    _scope_attr = "files"
    _replace = False

class ResourceRef(_CollectionRefContextual):
    _scope = "project"
    _scope_attr = "resources"
    _replace = False

class SubResourceRef(_CollectionRefContextual):
    ''' Construction helper, should be replaced when load is successfull '''
    _scope = "resource"
    _scope_attr = "sub_resources"
    _replace = True ### TODO: Calls self.replace(val) when found

class ExtResourceRef(_CollectionRefContextual):
    ''' Construction helper, should be replaced when load is successfull '''
    _scope = "resource"
    _scope_attr = "ext_resources"
    _replace = False ### TODO: forward update of src to replace signal! 


class Properties[K:str,V](UserDict):
    context : Context
    overlay : Properties

    def __setup__(self):
        self.context = Context()

    def __setitem__(self, key:K, item:V)->None:...
    def __getitem__(self, key:K)->V:...
    def __delitem__(self, key:K):...
    
    def get(self, key:K, include_overlay:bool=True):...
    def items(self, include_overlay:bool=True)->Generator[tuple[K,V]]:...
    def values(self, include_overlay:bool=True)->Generator[V]:...
    def keys(self, include_overlay:bool=True)->Generator[K]:...

    def _replace_callback(self, k, v)->None:...

    def set_overlay(self, overlay:Collection|None):...


class Project():
    context : Context
    files : Collection[str|File,File|str]
    resources : Collection[str|Resource,Resource|str]  
    def __setup__(self):
        self.context = Context()
        self.files = Collection(self.context, set_context=True)
        self.resources = Collection(self.context, set_context=True)

class File():
    context : Context
    path : CollectionKeyContextual[str]
    res : ResourceRef
    
    last_updated : int

    def get_disc_uid()->str|None:...

    def load():... ## load from disc, apply to project, and dif integration as req
    def _load()->Resource:...
    def _generate_dif():...
    def _integrate_dif():...

    def dump():... ## create or update as required
    def _dump()->str|bytes:...

    def create():...
    def remove():...
    def update():...
    def delete():...
    def move():...

    def on_fs_created():...
    def on_fs_removed():...
    def on_fs_updated():...
    def on_fs_deleted():...
    def on_fs_moved():...

    @classmethod
    def __collection_new__(cls)->File:...

class ExtResource[T:Resource]():
    context : Context

    id : CollectionKeyContextual[str]
    file_ref : FileRef
    res_ref : ResourceRef
    
    def get(self,)->T|None:...

    @classmethod
    def __collection_new__(cls)->ExtResource:...

class Resource():
    context : Context

    ## As a file:
    file : None|FileRef[File] = None
    uid : None|CollectionKeyContextual[str] = None
    sub_resources : None|Collection[str,Resource] = None
    ext_resources : None|Collection[str,ExtResource] = None

    ## As a subresource:
    id : CollectionKeyContextual[str]|None

    ## As all:
    properties : Properties
    instance : None|ExtResourceRef = None
    overlay : None|Resource = None

    @classmethod
    def __collection_new__(cls)->Resource:...

class Node(Resource):
    node_context : Context 

    ## As a file:
    ... #Stuff Inherited fr Resource
    nodes : None|Collection[int,Node]

    ## as all:
    ... #Stuff Inherited fr Resource
    overlay : None|Node = None
    children : Collection[str,Node]
