from __future__ import annotations

from collection import UserDict, UserString

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

    overlay : Properties|None

    def __init__(self, iterable, /, context:Context):
        self.context = Context() 
        self.context.set_extends(context)
        super().__init__(iterable)

    def __getitem__(self, key):
        return self._get(key)

    def get[D](self, key:str, default:D=_UNSET, localize:bool=True, use_overlay:bool=False, resolve_reference:bool=True)->Any|D:
        return self._get(key, default, localize, use_overlay, resolve_reference)
    
    def _get[D](self, key:str, default:D=_UNSET, localize:bool=True, use_overlay:bool=False, resolve_reference:bool=True)->Any|D:
        """ Converts promises outgoing, unless required to return direct """
        if use_overlay:
            chain : Iterable[Properties] = self.overlay_chain()
        else:
            chain : Iterable[Properties] = (self, )

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

        if default is _UNSET:
            raise KeyError(key)
        
        return default

    def __setitem__(self, key, item):
        return self._set(key, item)

    def set(self, key:str, item:Any):
        self._set(key, item)

    def _set(self, key:str, item:Any):
        if isinstance(item, StructReference):
            self.data[key] = item
            # self.data[key] = copy(item)
        elif isinstance(item, (Project,Resource,File)):
            self.data[key] = StructReference(obj = item)
        else:
            self.data[key] = item

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

    _file : StructReference[str, File] = None
    _resource : StructReference[str, Resource] = None
    file = StructReferenceProperty("_file", RefType.FILE)
    resource = StructReferenceProperty("_resource", RefType.RID)

    def __init__(self, id:str|None=None, file:str|Resource|None=None, resource:str|Resource|None=None):
        self.context = Context(ext_resource=self)

        self.id = CollectionKey(src = self, key = id)

        self.file = file
        self.resource = resource

class File():
    context : Context

    path : CollectionKey[str]

    _resource : StructReference[Resource]
    resource = StructReferenceProperty("_resource", RefType.RID)

    def __setup__(self):
        self.context = Context()
        self.path = CollectionKey(src=self)

    def __init__(self, path:str, resource:str|Resource|None=None):
        self.__setup__()
        self.path = path
        self.resource = resource

class Resource():
    context : Context

    ## as file:
    uid : CollectionKey[str]
    _file : StructReference[str, File]
    file = StructReferenceProperty("_file", RefType.File)
    sub_resources : Collection[str, Resource]
    ext_resources : Collection[str, ExtResource]

    ## All:
    id : CollectionKey[str]
    gdtype : GdDefType
    properties : Properties

    def __init__(self, id:str|None=None, uid:str|None=None, file:File|None=None, properties:Iterable|dict=tuple()):
        self.__setup__()
        self.id.key = id
        if uid or file:
            self.__setup_file__(uid=uid, file=file)
        self.properties.update(properties)

    def __setup__(self):
        self.context = Context(resource = self)

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