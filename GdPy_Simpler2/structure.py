from __future__ import annotations

from collections import UserDict, UserList
from typing import Any, Self
from types import MappingProxyType 

from .core import Signal, Context as _Context, CollectionKey, Collection, _C_Proxy, ViewStruct

class Context(_Context):
    project : Project
    resource : Resource
    sub_resource : Resource
    properties : Properties
    _slots_ = ("project", "resource", "sub_resource")

class _UNSET:...

class Properties(UserDict):
    overlay : None|Properties = None
    overlay_updated : Signal[None|Properties]

    context : Context

    # data : dict[str,Any]

    local_value_updated : Signal[str, Any]
    local_value_removed : Signal[str, Any]
    local_value_added : Signal[str, Any]

    overlay_value_updated : Signal[str, Any]
    overlay_value_removed : Signal[str, Any]
    overlay_value_added : Signal[str, Any]

    def __setup__(self):
        self.context = Context(properties = self)
        self.overlay_updated = Signal(self)

        self.local_value_updated = Signal(self)
        self.local_value_removed = Signal(self)
        self.local_value_added = Signal(self)

        self.overlay_value_updated = Signal(self)
        self.overlay_value_removed = Signal(self)
        self.overlay_value_added = Signal(self)

    def set_overlay(self, overlay:None|Properties, supress_dif:bool=False):
        o_items = dict(self.items(include_overlay=True))

        if not (self.overlay is None):
            self.overlay.local_value_added.disconnect(self.overlay_value_added)
            self.overlay.local_value_removed.disconnect(self.overlay_value_removed)
            self.overlay.local_value_updated.disconnect(self.overlay_value_updated)

            self.overlay.overlay_value_added.disconnect(self.overlay_value_added)
            self.overlay.overlay_value_removed.disconnect(self.overlay_value_removed)
            self.overlay.overlay_value_updated.disconnect(self.overlay_value_updated)

        self.overlay = overlay

        n_items = dict(self.items(include_overlay=True))

        if not (self.overlay is None):
            self.overlay.local_value_added.connect(self.overlay_value_added, filter=lambda k,v: not (k in self.data.keys()))
            self.overlay.local_value_removed.connect(self.overlay_value_removed, filter=lambda k,v: not (k in self.data.keys()))
            self.overlay.local_value_updated.connect(self.overlay_value_updated, filter=lambda k,v: not (k in self.data.keys()))

            self.overlay.overlay_value_added.connect(self.overlay_value_added, filter=lambda k,v: not (k in self.data.keys()))
            self.overlay.overlay_value_removed.connect(self.overlay_value_removed, filter=lambda k,v: not (k in self.data.keys()))
            self.overlay.overlay_value_updated.connect(self.overlay_value_updated, filter=lambda k,v: not (k in self.data.keys()))

        self.overlay_updated(overlay)

        if supress_dif:
            return

        added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
        removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
        changed = {k:v for k,v in n_items.items() if (k not in added.keys()) and (o_items[k] != n_items[k])}

        for k,v in added.items():
            self.overlay_value_added(k, v)
        for k,v in removed.items():
            self.overlay_value_removed(k, v)
        for k,v in changed.items():
            self.overlay_value_updated(k, v)

    def items(self, include_overlay:bool=True):
        l_keys = tuple(self.data.keys())
        if include_overlay and not (self.overlay is None):
            for k,v in self.overlay.items(include_overlay=include_overlay):
                if k in l_keys:
                    continue
                yield k,v 
        for k in l_keys:
            yield k, self.get(k)

    def keys(self, include_overlay:bool=True):
        l_keys = tuple(self.data.keys())
        if include_overlay and not (self.overlay is None):
            for k in self.overlay.keys(include_overlay=True):
                if k in l_keys:
                    continue
                yield k
        yield from l_keys

    def values(self, include_overlay:bool=True):
        for k,_ in self.items(include_overlay=include_overlay):
            yield k

    def __init__(self, context:Context=None, iterable=tuple(), overlay:Properties|None=None):
        self.__setup__()
        if not (context is None):
            self.context.set_extends(context)
        super().__init__(iterable)
        if not (overlay is None):
            self.set_overlay(overlay)

    def __setitem__(self, key, item):
        if (key in self.data.keys()):
            self.data[key] = item
            self.local_value_updated(key, item)
        else:
            self.data[key] = item
            self.local_value_added(key, item)
        if hasattr(item, "_promise_replace"):
            if not (self._replace_promise in item._promise_replace):
                item._promise_replace.connect(self._replace_promise, prepend_source=True, weak=True, once=True)
        if hasattr(item, "_referenced_callback"):
            item._referenced_callback(self.context)
        return

    def __delitem__(self, key):
        v = self.get(key, default=_UNSET, include_overlays=False, _unset_ok=True)
        super().__delitem__(key)
        self.local_value_removed(key, v)

    def __getitem__(self, key):
        return self.get(key, include_overlays=True)

    def get[D](self, key:str, default:D=_UNSET, include_overlays:bool=True, _unset_ok:bool=False, _bypass_viewstruct:bool=False)->Any|ViewStruct[list|dict]:
        res = self.data.get(key, _UNSET)

        if (res is _UNSET) and (not (self.overlay is None)) and include_overlays:
            res = self.overlay.get(key, default = _UNSET, include_overlays = True, _unset_ok=True, _bypass_viewstruct=True)

            if isinstance(res, Resource) and (res.is_sub_resource()):
                return self.context.resource.sub_resources.append_promise(res.id)

            elif isinstance(res, (list,dict)) and (not _bypass_viewstruct):
                return ViewStruct(res, self.context)
        
        if (res is _UNSET) and (default is _UNSET):
            if (not _unset_ok):
                raise KeyError(key)
            return _UNSET

        elif (res is _UNSET):
            return default

        return res

    def _replace_promise(self, item, new_item):
        for k,v in self.items():
            if (v is item) or (hash(v) == hash(item)):
                self[k] = new_item
    

class Project():
    context : Context
    resources : Collection[Resource]
    files : Collection[File]

    def __init__(self):
        self.context = Context(project=self)

        self.resources = Collection("uid")
        self.resources.appended.connect(self._on_resource_appended, weak=True)
        self.resources.removed.connect(self._on_resource_removed, weak=True)

        self.files = Collection("path") 
        self.files.appended.connect(self._on_file_appended, weak=True)
        self.files.removed.connect(self._on_file_removed, weak=True)
    
    def _on_resource_appended(self, key:str, resource:Resource):
        resource.context.set_extends(self.context)
    def _on_resource_removed(self, key:str, resource:Resource):
        resource.context.set_extends(None)

    def _on_file_appended(self, key:str, file:File):
        file.context.set_extends(self.context)
    def _on_file_removed(self, key:str, file:File):
        file.context.set_extends(None)

class File():
    context : Context
    path : CollectionKey[str]
    resource : None|Resource

    def __init__(self):
        self.context = Context(self, file = self)

    def _referenced_callback(self, ref_context:Context):
        if ref_context.project is None:
            ref_context.callback("project", self._on_project_set, weak=True, once=True)
        else:
            self._on_project_set("", ref_context.project)

    def _on_project_set(self, _attr:str, project:Project|None):
        if self in project.files:
            return
        if project is None:
            raise NotImplementedError() #Unknown desired behavior, as driven by referencers
        assert (self.context.project is None) or (self.context.project is project)
        project.files.append(self)
        
class Resource():
    context : Context

    properties : Properties
    sub_resources : Collection[str,Resource]

    id : CollectionKey[str]
    uid : CollectionKey[str]
    file : None|File = None

    def __init__(self, /, id:str|None=None, uid:str|None=None, file:File|None=None):
        self.context = Context(sub_resource = self)
        if (not(uid is None) or not(file is None)):
            self.context.resource = self

        self.properties = Properties(context=self.context)

        self.sub_resources = Collection("id")
        self.sub_resources.appended.connect(self._on_subresource_appended, weak=True)        
        self.sub_resources.removed.connect(self._on_subresource_removed, weak=True)        

        self.id = CollectionKey(id)
        self.uid = CollectionKey(uid)
        self.file = file

        if (not (uid is None)) or (not (file is None)):
            self.context.resource = self

        if not (file is None):
            file._referenced_callback(self.context)

    def _on_subresource_appended(self, k, resource:Resource):
        resource.context.set_extends(self.context)
    def _on_subresource_removed(self, k, resource:Resource):
        resource.context.set_extends(None)

    def _referenced_callback(self, ref_context:Context):
        if ref_context.project is None:
            ref_context.callback("project",self._on_project_set, weak=True, once=True)
        else:
            self._on_project_set("", ref_context.project)

        if ref_context.resource is None:
            ref_context.callback("resource",self._on_resource_set, weak=True, once=True)
        else:
            self._on_resource_set("", ref_context.resource)

    def _on_project_set(self, _attr:str, project:Project|None):
        assert (project is None) or (isinstance(project, Project))
        if self.is_sub_resource():
            return
        if self in project.resources:
            return
        if project is None:
            raise NotImplementedError() #Unknown desired behavior, as driven by referencers
        assert (self.context.project is None) or (self.context.project is project)
        project.resources.append(self)
        
    def _on_resource_set(self, _attr:str, resource:Resource|None):
        assert (resource is None) or (isinstance(resource, Resource))
        if not self.is_sub_resource():
            return
        if self in resource.sub_resources:
            return
        if resource is None:
            raise NotImplementedError() #Unknown desired behavior, as driven by referencers
        assert (self.context.resource is None) or (self.context.resource is resource)
        resource.sub_resources.append(self)

    def is_sub_resource(self):
        return (self.uid.key is None)
        
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

    def __setup__(self):
        self._promise_replace = Signal(self)
        self.context = Context()

    def __init__(self, scope, attr, id, default_rep:str):
        self.__setup__() 
        self.scope = scope
        self.attr = attr
        self.id = id
        self.default_rep = default_rep
        self.context.callback(scope, self._test_replace, weak=True)

    def _referenced_callback(self, context:Context):
        self.context.set_extends(context)

    def _test_replace(self, _attr:str, obj:Any|None):
        if obj is None:
            return
        col : Collection = getattr(obj, self.attr)
        val : _C_Proxy = col.append_promise(self.id)
        if (val._proxy_obj is None):
            val._proxy_obj_changed.connect(self._defered_replace, prepend_source=True, weak=True)
            ## Note: Connection here is retained even if the scope has been changed
            ## TODO: change to active scope-promise and sub to appended (which is called when promise is fullfilled)
        else:
            self._promise_replace(val)

    def _defered_replace(self, src, wrapped):
        self._promise_replace(src)

def SubResource(id:str): return _StructuralPromise("Resource", "sub_resources", id, f"SubResource({id})")
def ExtResource(id:str): return _StructuralPromise("Resource", "ext_resources", id, f"ExtResource({id})")
def RID(id:str): return _StructuralPromise("Project", "resources", id, f"RID({id})")
