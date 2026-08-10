from __future__ import annotations

from collections import UserDict, UserList
from typing import Any, Self

from .core import Signal, Context as _Context, CollectionKey, Collection, _C_Proxy

class Context(_Context):
    project : Project
    resource : Resource
    sub_resource : Resource
    properties : Properties
    _slots_ = ("project", "resource", "sub_resource")

class GdValue:...
class GdValueOverlayable(GdValue):
    overlay : None|Self = None
    overlay_updated : Signal

    def __setup__(self):
        self.overlay_updated = Signal(self)
        self.value_updated = Signal(self)
        self.value_removed = Signal(self)
        self.value_added = Signal(self)

    value_updated : Signal[str|int, Any]
    value_removed : Signal[str|int, Any]
    value_added : Signal[str|int, Any]

    def set_overlay(self, overlay:Self|None, supress_changes:bool=False):

        if not (self.overlay is None): ## Disconnect
            self.overlay.value_updated.disconnect(self._on_overlay_value_updated)
            self.overlay.value_removed.disconnect(self._on_overlay_value_removed)
            self.overlay.value_added.disconnect(self._on_overlay_value_added)

        self.overlay = overlay

        if not (self.overlay is None): ## Connect
            self.overlay.value_updated.connect(self._on_overlay_value_updated)
            self.overlay.value_removed.connect(self._on_overlay_value_removed)
            self.overlay.value_added.connect(self._on_overlay_value_added)

        self.overlay_updated()

        if supress_changes:
            return

        add, rem, changed = self._generate_overlay_dif()

        for k,v in add.items():
            self._on_overlay_value_updated(k,v)
        for k,v in rem.items():
            self._on_overlay_value_removed(k,v)
        for k,v in changed.items():
            self._on_overlay_value_added(k,v)

    def _generate_overlay_dif(self)->tuple[dict, dict, dict]:
        '''Return (add, rem, changed), anything returned will go into `_on_overlay_value_...` functions 
        Generally: Allow any items inside w/ overlay as upstream value to handle themselves.
        Generally: All Arrays/Dicts w/out overlays are local only and should not be updated.            
        '''
        raise NotImplementedError()

    def _on_overlay_value_updated(self, key, value):
        ...
    def _on_overlay_value_removed(self, key, value):
        ...
    def _on_overlay_value_added(self, key, value):
        ... 

class GdArray(UserList, GdValueOverlayable):

    def __init__(self, initlist):
        self.__setup__()
        super().__init__(initlist)

    def set_overlay(self, overlay:Properties|None, supress_changes:bool=False):
        raise NotImplementedError()
    
    ... #TODO #Value change propigation, similar.

class GdDictionary(UserDict, GdValueOverlayable):

    def __init__(self, iterable):
        self.__setup__()
        super().__init__(iterable)

    def set_overlay(self, overlay:Properties|None, supress_changes:bool=False):
        raise NotImplementedError()
    
    ... #TODO #Value change propigation, similar.

class Properties(UserDict, GdValueOverlayable):
    context : Context

    value_updated : Signal[str, Any]
    value_removed : Signal[str, Any]
    value_added : Signal[str, Any]

    def __setup__(self):
        self.context = Context(properties = self)
        return super().__setup__()

    def __init__(self, context:Context=None, iterable=tuple(), overlay:Properties|None=None):
        self.__setup__()
        if not (context is None):
            self.context.set_extends(context)
        if not (overlay is None):
            self.set_overlay(overlay)
        super().__init__(iterable)



        # ''' Set or clear extends, manage signal forwarding, and signal diffed values '''
        # old = self._get_all_elements()
        # cur = self._get_local_elements()

        # if not(extends is None):
        #     _cur = extends._get_all_elements()
        #     _cur.update(cur)
        #     cur = _cur

        # if not (self._extends is None):
        #     self._extends.element_changed.disconnect(self.element_changed)
        # self._extends = extends
        # if not (self._extends is None):
        #     self._extends.element_changed.connect(self.element_changed)

        # if supress_changes:
        #     return

        # _old_keys = tuple(old.keys())
        # _cur_keys = tuple(cur.keys())

        # rem = {k:None for k,v in old.items() if not (k in _cur_keys)}
        # add = {k:v for k,v in cur.items() if not (k in _old_keys)}
        # # set(_old_keys) & set(_cur_keys)
        # changed = {k:cur.get(k) for k in (set(_old_keys) & set(_cur_keys)) }
        # # changed = {k:v for k,v in cur.items() if (not (v is old.get(k, None)))}

        # for k,v in {**rem, **add, **changed}.items():
        #     self.element_changed(k, v)
        # return add, rem, changed

    def __setitem__(self, key, item):
        self.data[key] = item
        # r =  super().__setitem__(key, item)
        if hasattr(item, "_promise_replace"):
            if not (self._replace_promise in item._promise_replace):
                item._promise_replace.connect(self._replace_promise, prepend_source=True, weak=True, once=True)
        if hasattr(item, "_referenced_callback"):
            item._referenced_callback(self.context)
        return

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
