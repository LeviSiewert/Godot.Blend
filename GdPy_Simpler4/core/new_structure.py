from __future__ import annotations

from .collection import Collection, CollectionKey, CollectionKeyProperty
from .context import Context as _Context
from .signals import Signal, DISCONNECT

from random import randint
from typing import Any, Self, Iterable
from enum import Enum
from collection import UserDict
from weakref import ref as wref, ReferenceType

class _UNSET:...

class Context(_Context):
    _slots_ = ("project", "resource", "subresource", "ext_resource")


class Promise[T:Any]:
    class Type(Enum):
        FILE = "FILE"
        RESOURCE = "RESOURCE"
        SUB_RESOURCE = "SUB_RESOURCE"
        EXT_RESOURCE = "EXT_RESOURCE" ## Resolves to a resource
        EXT_RESOURCE_DIRECT = "EXT_RESOURCE_DIRECT" ## As in actual Ext_Resource object. Used pretty mmuch only in construction!

    key : str|int|dict
    o_type : Promise.Type

    def __init__(self, key:str|int|dict, o_type:Promise.Type):
        match o_type:
            case Promise.Type.EXT_RESOURCE:
                assert isinstance(key, dict)
            case _:
                assert isinstance(key, str)
        self.key = key
        self.o_type = o_type

    def __repr__(self):
        return f"Promise({self.o_type.lower()}, {self.key})"

    def resolve[D](self, context:Context, /, default:D=None)->D|T:
        match self.o_type:
            case Promise.Type.FILE:
                container = context.project 
                if (container is None): return
                result = container.files.get(self.key,default=None)

            case Promise.Type.RESOURCE:
                container = context.project
                if (container is None): return
                result = container.resources.get(self.key,default=None)

            case Promise.Type.EXT_RESOURCE:
                container = context.project 
                if (container is None): return
                result = container.resolve_ext_resource(**self.key, default=None)

            case Promise.Type.SUB_RESOURCE:
                container = context.resource
                if (container is None): return
                result = container.sub_resources.get(self.key, default=None)

            case Promise.Type.EXT_RESOURCE_DIRECT:
                container = context.resource
                if (container is None): return
                result = container.ext_resources.get(self.key, default=None)

        if result is None:
            return default
        return result

class PromiseContextual(Promise):
    ''' Container for replace callback from context, used in Properties
    Also Basic for PromiseProperty, acting as a callback.
    '''
    context : Context
    replace : Signal

    def __init__(self, key, o_type, context):
        self.context = context
        super().__init__(key, o_type)

    TODO

class PromiseProperty():
    ''' Instance this per object! Has a callback '''
    obj : Any
    attr : str
    context : Context
    callback : str

    def __init__(self, obj, attr:str, context:Context, callback_id:str, p_type:Promise.Type):
        self.obj = obj 
        self.attr = attr
        self.context = context
        self.p_type = p_type

    def __get__(self, _instance, _owner)->Any|Promise|None:
        if obj:=getattr(self.obj, self.attr, None) is None:
            return None
        elif isinstance(obj, Promise):
            return obj.resolve(self.obj.context, default=obj)
        else:
            return obj

    def __set__(self, _instance, value:Promise|str|Any|None):
        if isinstance(value, str, int):
            value = Promise(value, self.p_type)

        if isinstance(value, Promise):
            value = Promise.resolve(self.context, default=value)

        setattr(self.obj, self.attr, value)
        getattr(self.obj, self.callback)(value)

        self.diconnect()
        if isinstance(value, Promise):
            self.connect()

    _cached_collection : ReferenceType[Collection] = wref(_UNSET())
    _cached_collection_b : ReferenceType[Collection] = wref(_UNSET())

    def disconnect(self):
        ''' disconnect from cached collection if/a '''
        if (self.p_type is Promise.Type.EXT_RESOURCE):
            col = self._cached_collection()
            if not (col is None):
                col.appended.disconnect(self._check_appended)
                col.renamed.disconnect(self._check_renamed)
            col = self._cached_collection_b()
            if not (col is None):
                col.appended.disconnect(self._check_appended)
                col.renamed.disconnect(self._check_renamed)
        else:
            col = self._cached_collection()
            if not (col is None):
                col.appended.disconnect(self._check_appended)
                col.renamed.disconnect(self._check_renamed)

    def connect(self):
        ''' Fetch from local context (owners's context), connect if/a '''

        _map = {
            Promise.Type.FILE : ["project", "files"],
            Promise.Type.RESOURCE : ["project", "resources"],
            Promise.Type.EXT_RESOURCE : ["project", None],
            Promise.Type.SUB_RESOURCE : ["resource", "sub_resources"],
            Promise.Type.EXT_RESOURCE_DIRECT : ["resource", "ext_resources"],
        }

        container = getattr(self.context, _map[self.p_type][0], None)
        if container is None: 
            return

        if (self.p_type is Promise.Type.EXT_RESOURCE):
            container : Project
            self._cached_collection = wref(container.files)
            self._cached_collection_b = wref(container.resources)
            container.files.appended.connect(self._check_appended, weak=True, prepend_source=True)
            container.files.renamed.connect(self._check_renamed, weak=True, prepend_source=True)
            container.resources.appended.connect(self._check_appended, weak=True, prepend_source=True)
            container.resources.renamed.connect(self._check_renamed, weak=True, prepend_source=True)
        else:
            col = getattr(container, _map[self.p_type][1])
            self._cached_collection = wref(col)
            col.appended.connect(self._check_appended, weak=True, prepend_source=True)
            col.renamed.connect(self._check_renamed, weak=True, prepend_source=True)

    def _check_renamed(self, col, o_key, n_key, obj):
        self._check_appended(col,n_key, obj)

    def _check_appended(self, col, key, obj):
        ''' Non-optimal, but is alright for now '''
        val = getattr(self.obj, self.attr, None)
        if (val is None) or (not isinstance(val, Promise)):
            return DISCONNECT
        if val.o_type is Promise.Type.EXT_RESOURCE:
            result = val.resolve(self.context, default=None)
        elif key == val.key:
            result = obj
        else:
            result = None

        if (result is None):
            return

        setattr(self.obj, self.attr, result)
        getattr(self.obj, self.callback)(result)


# class Dict():
#     context : Context
#     def localise(new_context):... 

# class Array():
#     context : Context
#     def localise(new_context):... 


class Properties(UserDict):
    ''' Overlayable dict, any subresource, subresource promises will be localized at fetch 
    Direct references are rendered to indirect on transformation to text w/a
    Promises can exist in a dict, but are replaced when applicable
    '''
    
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

    def __init__(self, iterable, context:Context=None):
        self.__setup__()
        self.context.set_extends(context)
        super().__init__(iterable)


    ## SET ITEM ## 

    def __setitem__(self, key, item):
        return self.set(key, item)

    def set(self, key:str, item:Any):
        o_item :Any|_UNSET = self.data.get(key, _UNSET)

        if isinstance(item, Promise):
            item = item.resolve(self.context, item)

        if isinstance(item, Promise) and (not isinstance(item, PromiseContextual)):
            item = PromiseContextual(item.key, o_type=item.o_type, context=self.context)
            item.replace.connect(self.replace_value, prepend_source=True)

        if not ((callback:=getattr(item, "reference_callback",None)) is None):
            callback(self, self.context)
            ## Let the object sort out any reference BS

        super().__setitem__(key, item)

        if o_item is _UNSET:
            self.added(key, item)
        else:
            self.updated(key, o_item, item)


    ## GET ITEM ## 

    def __getitem__(self, key):
        return self.get(key)

    def get[D:Any](self, key:str, /, default:D=_UNSET, use_overlay:bool=True, localize:bool=True)->Any|D:
        result = self.data.get(key, _UNSET)

        if not (result is _UNSET):
            return result
        elif not use_overlay:
            return default

        sources = [(o.context, o.data) for o in self.overlay_chain()] 
        result = _UNSET
        for (o_context, data) in sources:
            result = data.get(key, _UNSET)
            if not (result is _UNSET):
                if localize:
                    return self.localize(o_context, result)
                return result
        return default

    ## DEL ITEM ##

    def __delitem__(self,key):
        self.delitem(key)

    def delitem(self, key):
        o_item = self._get(key, default=_UNSET, unset_ok=True)
        super().__delitem__(key)
        self.deleted(key, o_item)    


    ### OVERALY 
    
    def overlay_chain(self, ):
        if not (self.overlay is None): 
            yield from self.overlay.overlay_chain()
        yield self.overlay

    def set_overlay(self, overlay:Properties|None, supress_diff:bool=False)->tuple[list,list,list]:
        if self.overlay is overlay: 
            return 
        o_items = dict(self.items(localize=True, use_overlay=True))
        
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

        n_items = dict(self.items(localize=True, use_overlay=True))

        added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
        removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
        updated = {k:(o_items[k],v) for k,v in n_items.items() if (k not in added.keys()) and (o_items[k] != n_items[k])}

        for k,v in added.items():
            self.added(k, v)
        for k,v in removed.items():
            self.removed(k, v)
        for k,(v0,v) in updated.items():
            self.updated(k,v0, v)
        
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


    ## GENERATORS

    def keys(self, use_overlay:bool=True):
        yielded : list[str] = []

        if not use_overlay:
            yield from self.data.keys()
            return

        for k in self.data.keys():
            yielded.append(k)
            yield k

        for _p in (self, *self.overlay_chain()):
            for k in _p.data.keys():
                if k in yielded: 
                    continue
                yielded.append(k)
                yield k

    def values(self, localize:bool=True, use_overlay:bool=True):
        for k in self.keys(use_overlay=use_overlay):
            yield self._get(k, localize=localize, use_overlay=use_overlay)
        
    def items(self, localize:bool=True, use_overlay:bool=True):
        for k in self.keys(use_overlay=use_overlay):
            yield (k, self._get(k, localize=localize, use_overlay=use_overlay))
        
    def localize[V:Any](self, original_context, value:V)->V:
        if isinstance(value, Promise):
            return value.resolve(self.context, default=value)
        elif isinstance(value, Resource) and (not isinstance(value,Node)):
            if self.context.resource:
                return self.context.resource.sub_resources.get(value.name, default=value)
        elif getattr(value, "localize"):
            ## Array / Dict copy
            return value.localize(self.context)
        return value
        
    def replace_value(self, o_value, n_value):
        for k,v in dict(self.data):
            if (v is o_value):
                self[k] = n_value

class Project():
    context : Context

    fs : AbstractFileSystem

    resources : Collection[str, Resource]
    files : Collection[str, File]
    # resource_types : Collection[str, GdType] #DEFER

    def __init__(self, fs:AbstractFileSystem, files:Iterable[Resource]=tuple(), resources:Iterable[Resource]=tuple()):
        self.__setup__()
        raise NotImplementedError()

    def __setup__(self):
        self.resources = Collection(key_attr="_name")
        self.file = Collection(key_attr="_path")

class File():
    context : Context

    _path : CollectionKey[str]
    path = CollectionKeyProperty(str, "_path", callack="path_set")
    path_set : Signal[str|None]

    _resource : Promise[Resource]|Resource|None = None
    resource : PromiseProperty[str, Resource]
    resource_set : Signal[str|None]

    importer : FileIO|None = None

    def __init__(self, filetype:str|FileIO, resource:Resource|None=None):
        self.__setup__()
        raise NotImplementedError()

    def __setup__(self):
        self.context = Context(file=self)

        self.path_set = Signal(self)
        self.resource_set = Signal(self)

        self.resource = PromiseProperty(self, "_resource", self.context, "resource_set", Promise.Type.RESOURCE)


## IMPORT AND SETTINGS ##

class Settings:
    ''' Simple file contents object '''
    categories : Collection[str, Category]
    properties : Properties

    def __init__(self, categories:Iterable[Category]=tuple(), properties:Iterable=tuple()):
        self.__setup__()
        self.categories.extend(categories)
        self.properties.update(properties)

    def __setup__(self):
        self.categories = Collection(key_attr = "name")
        self.properties = Properties(context=self.context)

class Category:
    context : Context
    name : CollectionKey[str]
    properties : Properties

    def __init__(self, name, properties):
        self.__setup__()
        self.name.key = name
        self.properties.update(properties)

    def __setup__(self):
        self.context = Context(subresouce=self)
        self.name = CollectionKey(self)
        self.properties = Properties(context=self.context)s

class FileIO[ResourceType:Resource](Settings):
    ## TODO Matched globally via file type, somehow.
    
    def create_resource()->ResourceType:
        ''' Create a from-scratch resource matching specified type '''

    def file_import()->ResourceType:
        pass

    def file_export()->tuple[tuple[str],bytes]:
        ''' return file extension(s) and disc-byte rep '''
        pass

## RESOURCE STRUCTURE ##

class Resource():
    ## ALL INSTANCES ##
    context : Context

    _name : CollectionKey[str]
    name = CollectionKeyProperty(str, "_name", callback = "name_set")
    nane_set : Signal[str|Node|None]

    _instance : Promise[Self]|Self|None = None # Specifically ExtResource promise
    instance : PromiseProperty[Self]
    instance_set : Signal[str|Self|None]
    instance_editable : bool = False

    properties : dict[str, Any|Generic[Promise[Promise.Object]|Promise.Object]]


    ## SCENE/FILE ONLY ##
    constructed: bool|None = None

    uid_set : Signal[str|None]
    file_set : Signal[str|File|None]

    _uid : CollectionKey[str]|None = None
    uid = CollectionKeyProperty(str, "_uid", callback = "uid_set")

    _file : Promise[File]|File|None = None
    file : PromiseProperty[File]

    sub_resources : Collection[str, Resource] 
        ## Inclusionary, 
            # only "cleaned" for unreferenced if tree is constructed/loaded fully
            # At write also remove instances converted to external files. 
        ## references to subresources should append to this subresource
        ## Promises draw from this "pool" 

    def __init__(self, id:str|None=None, uid:str|None=None, file:str|File|None=None, properties:Iterable=tuple(), subresources:Iterable[Subresource]=tuple()):
        self.__setup__()

        if id is None:
            self._name.generate()
        else:
            self.name = id 

        self.sub_resources.extend(subresources)
        self.properties.update(properties)

    def __setup__(self):
        self.context = Context(subresource=self)

        self.uid_set = Signal(src = self) 
        self.file_set = Signal(src = self) 
        self.name_set = Signal(src = self) 
        self.instance_set = Signal(src = self) 

        self.sub_resources = Collection(key = "name")
        self.properties = Properties(context=self.context)

        self.file = PromiseProperty(self, "_file", self.context, "file_set", Promise.Type.FILE)
        self.instance = PromiseProperty(self, "_instance", self.context, "instance_set", Promise.Type.EXT_RESOURCE)

        self.file_set.connect(self._on_file_set)



    ## STD BEHAVIOR:

    def _on_file_set(self):
        ''' Generate UID if one doesn't already exist'''
        if (self.file is None) or (not (self.uid is None)): 
            return
        self.uid = self._uid.generate(self.context)

    ## STD TOOLS:

    def construct_and_load(self):
        ''' construct tree, loading everything. Multipass in-place transformer. Load dependencies as well. '''
        if self.uid is None: 
            raise TypeError()
        raise NotImplimentedError()


class NodePath(str):...

class Node(Resource):
    ## UNIVERSAL:
    unique_id : int ## Generate at instanciation if not provided

    ## TEMP/CACHED ONLY ##
    # Node only
    _parent : None|str = None

    # Scene only - Pre Construction
    unclaimed_nodes : None | dict[str, Node] = None
    unclaimed_edits : None | dict[str, NodePath] = None

    def __init__(self, name:str=None, unique_id:str=None,  uid = None, file = None, properties = tuple(), subresources = tuple(), unclaimed_nodes:Iterable=tuple(), unclaimed_edits:Iterable=tuple):
        super().__init__(name, uid, file, properties, subresources)

        if not (unique_id is None):
            self.unique_id = unique_id
        else:
            self.unique_id = randint(100000, 1000000)

        if unclaimed_edits: self.unclaimed_edits.extend(unclaimed_edits)
        if unclaimed_nodes: self.unclaimed_nodes.extend(unclaimed_nodes)

    def __setup__(self):
        self.children = Collection(key = "_name")
        super().__setup__()

    def resolve_nodepath(self, path:str|NodePath):
        pass