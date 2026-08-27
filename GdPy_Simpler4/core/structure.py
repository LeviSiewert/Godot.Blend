from __future__ import annotations

from collections import UserDict, UserString

from fsspec import AbstractFileSystem
from typing import Iterable, Any, Type

from copy import copy

from .signals import Signal
from .context import Context as _Context
from .collection import Collection as _Collection, CollectionKey
from .structure_promise import RefType, StructReference, StructReferenceProperty 
from .defininitions import GdDefType, GdDefProperty, GdDefSignal

class _UNSET:...

class Context(_Context):
    _slots_ = ("project", "resource", "subresource", "ext_resource")

from enum import Enum

class CollectionOverlayMode(Enum):
    SUBITEM_OVERLAY_COPY = 0
    SUBITEM_PASSTHROUGH = 1

class Collection(_Collection):

    overlay : None|Collection = None
    overlay_itemmode = CollectionOverlayMode.SUBITEM_OVERLAY_COPY

    def __init__(self, key_attr, iterable = ..., context = None, key_is_string = True, key_resolve_incriment = False, key_formatter = None, mode:CollectionOverlayMode=CollectionOverlayMode.SUBITEM_OVERLAY_COPY):
        super().__init__(key_attr, iterable, context, key_is_string, key_resolve_incriment, key_formatter)

    def set_overlay(self, overlay:Collection|None, supress_signals:bool=False)->dict[str,tuple[Any]]:
        if self.overlay is overlay: return

        o_values = dict(self.items(include_overlay=True))

        if not (self.overlay is None):
            pass #disconnect

        self.overlay = overlay

        if not (self.overlay is None):
            pass #Connect

        if supress_signals:
            return

        n_values = dict(self.items(include_overlay=True))

        raise NotImplementedError()

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

    def provide_reftype_key(self)->tuple[None,None]:
        if not (self.id.key is None):
            return (RefType.EXT_RESOURCE, self.id.key)
        return (None,None)

    def _reference_callback(self):
        self.fullfillreferences(RefType.EXT_RESOURCE, self.id.key)

class File():
    context : Context

    path : CollectionKey[str]

    fullfill_references : Signal[RefType, str]

    _resource : StructReference[Resource]
    resource = StructReferenceProperty("_resource", RefType.RID)

    def __init__(self, path:str, resource:str|Resource|None=None):
        self.__setup__()
        self.path.key = path
        self.resource = resource

    def __setup__(self):
        self.context = Context()
        self.path = CollectionKey(src=self)
        self.fullfill_references = Signal(self)

    def provide_reftype_key(self)->tuple[RefType|None,str|None]:
        if (not (self.path.key is None)) and (not (self.context.project is None)):
            return (RefType.FILE, self.id.key)
        return RefType.DEFER, None

class Resource():
    context : Context

    ## as file:
    uid : CollectionKey[str]
    _file : StructReference[str, File]
    file = StructReferenceProperty("_file", RefType.FILE)
    sub_resources : Collection[str, Resource]
    ext_resources : Collection[str, ExtResource]

    _instance : StructReference[str, ExtResource]
    instance = StructReferenceProperty("_instance", RefType.EXT_RESOURCE)
    overlay : Resource|None = None
    overlay_updated : Signal[Resource|None]

    ## All:
    id : CollectionKey[str]
    gdtype : GdDefType
    properties : Properties

    fullfill_references : Signal[RefType, str]

    def __init__(self, id:str|None=None, uid:str|None=None, file:File|None=None, properties:Iterable|dict=tuple(), sub_resources:Iterable[Resource]=None, ext_resources:Iterable[ExtResource]=None, instance:Resource|File|ExtResource|None=None, setup_overlay:bool=True,):
        self.__setup__()
        self.id.key = id
        if uid or file:
            self.__setup_file__(uid=uid, file=file)
        self.properties.update(properties)


        if not (sub_resources is None):
            self.sub_resources.extend(sub_resources)
        if not (ext_resources is None):
            self.ext_resources.extend(ext_resources)

        self.set_instance(instance, set_overlay=setup_overlay)

    def set_instance(self, instance:Resource|File|ExtResource|None, set_overlay:bool=False):
        o_val = self.instance
        if instance is o_val:
            return
        if instance is None:
            self.instance = None
        elif isinstance(instance, ExtResource):
            self.instance = instance
        elif isinstance(instance, (File,Resource)):
            self.instance = ExtResource(id=None, file=instance)
        else:
            raise TypeError(instance, "expected:", Resource|File|ExtResource|None) 

        if not (self.overlay is None):
            self.set_overlay(None)
        if set_overlay and not( instance is None):
            self.set_overlay(self.instance.resource)

        self.instance_updated(self.instance)

    def set_overlay(self, overlay:Resource|None):
        self.overlay = overlay

        if not (overlay is None):
            self.properties.set_overlay(overlay.properties.overlay)
            if not self.is_subresource():
                self.sub_resources.set_overlay(overlay.sub_resources)
        else:
            self.properties.set_overlay(None)
            if not self.is_subresource():
                self.sub_resources.set_overlay(None)


        self.overlay_updated(overlay)

    def __setup__(self):
        self.context = Context(resource = self)
        self.instance_updated = Signal(self)
        self.overlay_updated = Signal(self)
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
        return (self.uid.key is None) and (self.file is None)
    
    def is_resource(self)->bool:
        return (not (self.uid.key is None)) or (not (self.file is None))

    def provide_reftype_key(self)->tuple[RefType|None,str|None]:
        if self.is_subresource() and (not (self.id.key is None)) and (not (self.context.resource is None)):
            return (RefType.SUB_RESOURCE, self.id.key)
        elif (not self.is_subresource()) and (not (self.uid.key is None)) and (not (self.context.project is None)):
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

    def __init__(self, name:str, id = None, uid = None, file = None, properties = tuple(), sub_resources = None, ext_resources = None, instance = None, setup_overlay = True, children:Iterable[Node]=tuple()):
        self.__setup__()
        self.name.key = name
        self.id.key = id
        if uid or file:
            self.__setup_file__(uid=uid, file=file)
        self.properties.update(properties)
            
        if not (sub_resources is None):
            self.sub_resources.extend(sub_resources)
        if not (ext_resources is None):
            self.ext_resources.extend(ext_resources)

        self.children.extend(children)

        self.set_instance(instance, set_overlay=setup_overlay)

    def __setup__(self):
        super().__setup__()
        self.name = CollectionKey(src = self)
        self.children = Collection(key_attr="name", context=self.context, key_resolve_incriment=True)
        self.signals = Collection(key_attr="id", context=self.context)

    def set_overlay(self, overlay:Resource|None):
        self.overlay = overlay

        if not (overlay is None):
            self.properties.set_overlay(overlay.properties.overlay)
            self.children.set_overlay(overlay.children)
            if not self.is_subresource():
                self.sub_resources.set_overlay(overlay.sub_resources)
        else:
            self.properties.set_overlay(None)
            self.children.set_overlay(None)
            if not self.is_subresource():
                self.sub_resources.set_overlay(None)

        self.overlay_updated(overlay)

    def __setup_file__(self, uid = None, file = None):
        self.nodes = Collection(key_attr="id", key_is_string=False)
        return super().__setup_file__(uid, file)

    def setup_instance(self):
        raise NotImplementedError()



# class NormalizeSession():
#     memo : dict

#     def normalize[N:Project|ExtResource|Resource|Node](self, 
#             node            : N,
#             /, 
#             singulate        : bool = False, 
#             localize         : bool = True,
#             instanciate_load : bool = False,
#             fix_instanciate  : bool = True,
#             check_recursion  : bool = True, 
#             in_place         : bool = True, 
#             scope            : Type  = None,
#             )->N: 
#         ''' 
#         :param singulate: 
#         Ensures that every node that is referenced in multiple scopes is copied into those scopes (w/a)
#         - IE: (R1.subresources["sr1"] is R2.subresources["sr1"]) ->> (R1.subresources["sr1"] == R2.subresources["sr1_copy"])
#         :param localize:
#         Ensures that every referenced node that *doesn't* exist in the scope is placed within that scope
#         - IE: 
#             - (R1.subresources["sr1"].properties["ref"] is sr2(free)) ->> (R1.subresources["sr1"].properties["ref"] -> R1.subresources["sr2"])
#             - (R1.subresources["sr1"].properties["ref"] is R2(Free)   ->> (R1.subresources["sr1"].properties["ref"] -> R1.ExtResources[...] -> P.Resources["R2"] is R2)
#         - Copies to local w/ singulate w/a
#         :param instanciate_load:
#         Ensures that all instances referenced are loaded
#         - IE 
#             - (R1.instance is StructRef(R0)) ->> (R1.instance is R0)
#         If project is not set, an error will occur
#         :param fix_instanciate: 
#         Ensures that any instanciate structure is fully initialized
#         - IE 
#             - (R1.instance is R0 && R1.overlay is None) ->> (R1.instance is R0 && R1.overlay is R0, R1.nodes...ect...)
#         :param check_recursion:
#         Checks that recursion rules within the godot structure are not broken;
#         OK:
#             Node <-> Node (As ref via nodepath)
#         NOT_OK:
#             Sr1 <-> Sr2 (Same scope)
#             R1 -> R2 -> R1
#         #TODO: Double check recurision & co-dependency rules.

#         :param in_place:
#         Manipulate tree in place, or return a deepcopy. 
#         A deepcopy will *not* be attached to a project/outer scope;
#             - a copy will not exist in outer scopes collections
#             - a copy will not have the context extended from the parent
#         Typically only used in exports

#         :param scope:
#         Limitiation in lateral action, usually set by first node's type.
#         - IE 
#             - R1.normalize(in_place=False, localize=True) ; where (R1.p["ref"]->R2) ; R2 is not coppied, but is localized w/a 
#         '''
        
#         raise NotImplementedError()
    