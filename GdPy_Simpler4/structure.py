from __future__ import annotations

from collections import UserDict, UserString

from fsspec import AbstractFileSystem
from typing import Iterable, Any

from copy import copy

from .signals import Signal
from .context import Context
from .collection import Collection, CollectionKey
from .structure_promise import RefType, StructReference, StructReferenceProperty 
from .defininitions import GdDefType, GdDefProperty, GdDefSignal

class _UNSET:...

class Properties(UserDict):
    context : Context

    overlay : Properties|None = None

    added : Signal[str,Any]
    removed : Signal[str,Any]
    updated : Signal[str,Any,Any]

    def __setup__(self):
        self.context = Context() 
        self.added = Signal(self)
        self.removed = Signal(self)
        self.updated = Signal(self)
        self.data = {}

    def __init__(self, iterable=tuple(), /, context:Context=None):
        self.__setup__()
        self.context.set_extends(context)
        self.update(iterable)
        # super().__init__(iterable)

    def overlay_chain(self, depth_first:bool=False):
        if self.overlay is None:
            yield self
            return
        if depth_first:
            yield from self.overlay.overlay_chain(depth_first=depth_first)
            yield self
        else:
            yield self
            yield from self.overlay.overlay_chain(depth_first=depth_first)

    def set_overlay(self, overlay:Properties|None, supress_diff:bool=False)->tuple[list,list,list]:
        if self.overlay is overlay: 
            return 
        o_items = dict(self.items(resolve_reference=False, localize=False, use_overlay=True))
        # raise Exception(o_items)
        
        if not (self.overlay is None):
            self.overlay.added.disconnect(self._on_overlay_added)
            self.overlay.removed.disconnect(self._on_overlay_removed)
            self.overlay.updated.disconnect(self._on_overlay_updated)

        self.overlay = overlay

        if not (self.overlay is None):
            self.overlay.added.connect(self._on_overlay_added, weak=True)
            self.overlay.removed.connect(self._on_overlay_removed, weak=True)
            self.overlay.updated.connect(self._on_overlay_updated, weak=True)

        if supress_diff:
            return

        n_items = dict(self.items(resolve_reference=False, localize=False, use_overlay=True))

        added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
        removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
        updated = {k:(o_items[k],v) for k,v in n_items.items() if (k not in added.keys()) and (o_items[k] != n_items[k])}

        for k,v in added.items():
            self.added(k, v)
        for k,v in removed.items():
            self.removed(k, v)
        for k,(v0,v) in updated.items():
            self.updated(k,v0, v)

        #TODO: Try to optimize via caching keys or dict slices.
        # added   = tuple(((k,v) for k,v in n_items.items() if not (k in o_items.keys())))
        # removed = tuple(((k,v) for k,v in o_items.items() if not (k in n_items.keys())))
        # updated = tuple(((k, o_items[k], v) for k,v in n_items.items() if (k in o_items.keys() and (o_items[k] != v))))

        # for k,v in added:
        #     self.added(k,v)
        
        # for k,v in removed:
        #     self.removed(k,v)
        
        # for k,v0,v in updated:
        #     self.updated(k,v0,v)
        
        return {"added":added, "removed":removed, "updated":updated}

        

    def _on_overlay_added(self, key, value):
        if key in self.data.keys():
            return
        self.added(key, value)

    def _on_overlay_removed(self, key, value):
        if key in self.data.keys():
            return
        self.removed(key, value)

    def _on_overlay_updated(self, key, v0, value):
        if key in self.data.keys():
            return
        self.updated(key, v0, value)

    def __getitem__(self, key):
        return self._get(key)

    def get[D](self, key:str, default:D=None, localize:bool=True, use_overlay:bool=True, resolve_reference:bool=True)->Any|D:
        return self._get(key, default, localize, use_overlay, resolve_reference)
    
    def _get[D](self, key:str, default:D=_UNSET, localize:bool=True, use_overlay:bool=True, resolve_reference:bool=True, unset_ok:bool=False)->Any|D:
        """ Converts promises outgoing, unless required to return direct """
        if use_overlay:
            chain : Iterable[Properties] = self.overlay_chain()
        else:
            chain : Iterable[Properties] = tuple([self])

        traversed : list[Properties] = []

        for p in chain:
            traversed.append(p)

            v = p.data.get(key, _UNSET)
            if v is _UNSET:
                continue

            if (not isinstance(v, StructReference)) or (not resolve_reference):
                return v

            if not localize:
                return v.resolve(p.context)

            for _p in traversed:
                ## Look (local -> Src) for matching ID to return
                r = v.resolve(_p.context, v)
                if not (r is v):
                    return r
                
            return v

        if (default is _UNSET) and (not unset_ok):
            raise KeyError(key)
        
        return default

    def __delitem__(self, key):        
        o_item = self._get(key, default=_UNSET, unset_ok=True)
        super().__delitem__(key)
        self.deleted(key, o_item)    

    def __setitem__(self, key, item):
        return self._set(key, item)

    def set(self, key:str, item:Any):
        self._set(key, item)

    def _set(self, key:str, item:Any):
        o_item = self._get(key, default=_UNSET, unset_ok=True)

        if isinstance(item, StructReference):
            self.data[key] = item
            # self.data[key] = copy(item)
        elif isinstance(item, (Project,Resource,File)):
            self.data[key] = StructReference(obj = item)
        else:
            self.data[key] = item

        if o_item is _UNSET:
            self.added(key, item)
        else:
            self.updated(key, o_item, item)

    def keys(self, use_overlay:bool=True):
        yielded : list[str] = []

        if not use_overlay:
            yield from self.data.keys()
            return

        for k in self.data.keys():
            yielded.append(k)
            yield k

        for _p in self.overlay_chain():
            for k in _p.data.keys():
                if k in yielded: 
                    continue
                yielded.append(k)
                yield k

    def values(self, localize:bool=True, use_overlay:bool=True, resolve_reference:bool=True):
        for k in self.keys(use_overlay=use_overlay):
            yield self._get(k, localize=localize, use_overlay=use_overlay, resolve_reference=resolve_reference)
        
    def items(self, localize:bool=True, use_overlay:bool=True, resolve_reference:bool=True):
        for k in self.keys(use_overlay=use_overlay):
            yield (k, self._get(k, localize=localize, use_overlay=use_overlay, resolve_reference=resolve_reference))
        
class Project():
    context : Context
    files : Collection[str, File]
    resources : Collection[str, Resource]
    types : Collection[str, GdDefType]

    file_system : AbstractFileSystem
    file_system_Signals : type

    def __setup__(self):
        self.context = Context(project = self)
        self.files = Collection(key_attr="path", context=self.context)
        self.resources = Collection(key_attr="uid", context=self.context)
        self.types = Collection(key_attr="composite", context=self.context)

    def __init__(self, fs:AbstractFileSystem):
        self.__setup__()
        self.file_system = fs

class ExtResource():
    context : Context
    id : CollectionKey[str]

    fullfill_references : Signal[RefType, str]

    _file : StructReference[str, File] = None
    _resource : StructReference[str, Resource] = None
    file = StructReferenceProperty("_file", RefType.FILE)
    resource = StructReferenceProperty("_resource", RefType.RID)

    def __setup__(self):
        self.context = Context(ext_resource=self)
        self.id = CollectionKey(src = self, key = None)
        self.fullfill_references = Signal(self)

    def __init__(self, id:str|None=None, file:str|Resource|None=None, resource:str|Resource|None=None):
        self.__setup__()
        self.id.key = id

        self.file = file
        self.resource = resource

class File():
    context : Context

    path : CollectionKey[str]

    fullfill_references : Signal[RefType, str]

    _resource : StructReference[Resource]
    resource = StructReferenceProperty("_resource", RefType.RID)

    def __init__(self, path:str, resource:str|Resource|None=None):
        self.__setup__()
        self.path = path
        self.resource = resource

    def __setup__(self):
        self.context = Context()
        self.path = CollectionKey(src=self)
        self.fullfill_references = Signal(self)

class Resource():
    context : Context

    ## as file:
    uid : CollectionKey[str]
    _file : StructReference[str, File]
    file = StructReferenceProperty("_file", RefType.FILE)
    sub_resources : Collection[str, Resource]
    ext_resources : Collection[str, ExtResource]

    ## All:
    id : CollectionKey[str]
    gdtype : GdDefType
    properties : Properties

    fullfill_references : Signal[RefType, str]

    def __init__(self, id:str|None=None, uid:str|None=None, file:File|None=None, properties:Iterable|dict=tuple()):
        self.__setup__()
        self.id.key = id
        if uid or file:
            self.__setup_file__(uid=uid, file=file)
        self.properties.update(properties)

    def __setup__(self):
        self.context = Context(resource = self)

        self.fullfill_references = Signal(self)

        self.id = CollectionKey(src=self,key=None)
        self.uid = CollectionKey(src=self,key=None)
        self.properties = Properties(context=self.context)

    def __setup_file__(self, uid:str|None=None, file:str|File|None=None):
        self.sub_resources = Collection(key_attr = "id", context=self.context)
        self.ext_resources = Collection(key_attr = "id", context=self.context)        

        self.file = file
        self.uid.key = uid
        self.context.resource = self

    def is_subresource(self)->bool:
        return (self.uid._key is None)

    def provide_reftype_key(self)->tuple[RefType|None,str|None]:
        if self.is_subresource() and not (self.id.key is None) and (not (self.context.Resource is None)):
            return (RefType.SUB_RESOURCE, self.id.key)
        elif (not self.is_subresource()) and (not self.uid.key) and (not (self.context.Project is None)):
            return (RefType.RESOURCE, self.uid.key)
        return (RefType.DEFER, None)

class NodePath(UserString):... 

class GdSignal():
    context : Context
    fr : NodePath
    to : NodePath

    def __init__(self, fr:NodePath, to:NodePath):
        self.fr = fr
        self.to = to
        self.context = Context()
    
class Node(Resource):

    _instance : StructReference[str, Node]
    instance = StructReferenceProperty("_instance", RefType.EXT_RESOURCE)
    overlay : None|Node = None

    nodes : Collection[int, Node]

    name : CollectionKey[str]
    children : Collection[str, Node]
    signals : Collection[str, GdSignal]

    def __setup__(self):
        super().__setup__()
        self.name = CollectionKey(src = self)
        self.children = Collection(key_attr="name", context=self.context, key_resolve_incriment=True)
        self.signals = Collection(key_attr="id", context=self.context)

    def __setup_file__(self, uid = None, file = None):
        self.nodes = Collection(key_attr="id", key_is_string=False)
        return super().__setup_file__(uid, file)

    def __init__(self, name=None, id = None, uid = None, file = None, properties = tuple()):
        self.name.key = name
        super().__init__(id, uid, file, properties)

    def setup_instance(self):
        raise NotImplementedError()