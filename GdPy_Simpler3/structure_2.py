from __future__ import annotations
from weakref import ReferenceType as WeakReferenceType, ref as wref
from typing import Self, Any, Iterable
from collections import UserDict

from .signal import Signal
from .context import Context


class _UNSET():...

class RefIO:
    replace_promise : Signal[ResourceRef.Type, Self]

    def make_ref(self)->tuple[None|ResourceRef.Type, None|str|int]:
        ## Make Ref within scope or return None!
        ...

class ResourceRef[K:str|int, T:RefIO]:
    ''' Defered structural ref that attaches and updates from context, resolved on get via multiple ways (Properties or @property-like) '''

    class Type:
        DEFERED = None

        File = ("project","files",False)
        RID = ("project","resources",False)

        Resource = ("project", "resources", True) ## Convert to RID or ExtResource on save w/a
        ExtResource = ("resource", "ext_resource", True)
        SubResource = ("resource", "sub_resource", True)    

    ref_type : ResourceRef.Type = None
    sref : None|T = None
    wref : WeakReferenceType[T] = wref(_UNSET())
    key : K = None

    updated : Signal[ResourceRef.Type, K]

    
    def __init__(self, item_or_key:T|K, ref_type:ResourceRef.Type=None, ):
        if isinstance(item_or_key, (str,int) and ref_type is None):
            raise TypeError("a key as an argument must have declared scope!")

        if isinstance(item_or_key, (str,int)):
            self.key = item_or_key
            self.ref_type = ref_type
            return

        if (ref_type is None): 
            rt, key = item_or_key.make_ref() #Ask for any ref within context
            if (rt is None): 
                self.sref = item_or_key
                item_or_key.replace_promise.connect(self._on_replace_promise, once=True) #First relevent scope!
            else:
                self.ref_type = rt
                self.key = key
            return

        else:
            self.sref = item_or_key
            item_or_key.replace_promise.connect(self._on_replace_promise, filter = lambda t, k: (t[1] == ref_type[1]) and ((self is k) or (self.key == k) ), once=True) #First matching scope!
            return

    def _on_replace_promise(self, ref_type:ResourceRef.Type, key:K):
        if not (self.sref is None):
            self.wref = wref(self.sref) 
        self.ref_type = ref_type
        self.key = key
        self.updated(ref_type, key)
    
    def resolve(self, context:Context):
        if self.ref_type is self.Type.DEFERED:
            return self.sref

        scope = getattr(context,self.ref_type[0], _UNSET)
        if scope is _UNSET:
            return self
        col = getattr(scope, self.ref_type[1], _UNSET)
        if col is _UNSET:
            return self
        item = col.get(self.key, _UNSET)
        if item is _UNSET:
            return self
        self.wref = wref(item)
        return item

    def update(self, value:T|None):
        pass

class ResourceRefProperty[K:str|int, T:Any|RefIO]():
    attr : str
    ref_type : ResourceRef.Type

    def __init__(self, attr, ref_type:ResourceRef.Type=None):
        self.ref_type = ref_type
        self.attr = attr

    def __get__(self, instance, owner):
        ref = getattr(instance, self.attr,None) 
        if (ref is None):
            return None
        return ref.resolve(instance.context)

    def __set__(self, instance, value):
        ref = getattr(instance, self.attr,None) 
        if (ref is None):
            ref = ResourceRef(self.ref_type, value)
            setattr(instance, self.attr, ref)
            return
        
        if value is None:
            setattr(instance, self.attr, ref)
            return

        ref.update(value)

from .collection import Collection, CollectionKey

class Project():
    context : Context

    files : Collection[str, File]
    types : Collection[str, GdDefType]
    resources : Collection[str, Resource]

    def __setup__(self):
        self.context = Context(project=self)
        self.resources = Collection(key_attr="_uid", context=self.context)
        self.files = Collection(key_attr="_path", context=self.context)

    def __init__(self):
        self.__setup__()

class GdDefType():
    ...

class StructureError(BaseException):...

class ExtResource():
    ''' Listen and fullfill, priority match of uid'''
    context : Context

    replace_promise : Signal[ResourceRef.Type, str|Self]

    id : CollectionKey[str]

    _path : ResourceRef[File]
    path = ResourceRefProperty("_path", ResourceRef.Type.File)

    _uid : ResourceRef[Resource]
    uid = ResourceRefProperty("_uid",ResourceRef.Type.RID)

    def __setup__(self):
        self.context = Context(ext_resource = self)
        self.replace_promise = Signal(self)
        self.context.callback("resource", self._on_resource_updated)
        self.id = CollectionKey()

    def __init__(self, id:str|None ):
        self.__setup__()
        self.id.key = id

    def _reference_callback(self, context:Context):
        if (self.context._extends is None):
            self.context.set_extends(context)

    def _dereference_callback(self, context:Context):
        pass

    def _on_resource_updated(self, resource:None|Resource):
        if resource is None:
            return
        if not (self in resource.ext_resources):
            resource.ext_resources.append(self, supress_callback=True)
            self.replace_promise(ResourceRef.Type.ExtResource, self.id.key)


class Properties(UserDict):
    context : Context
    overlay : None|Properties

    data : dict[str,Any|ResourceRef]
    
    def __setup__(self):
        self.context = Context()
        
    def __init__(self, iterable, context:Context|None=None, overlay:None|Properties=None):
        self.__setup__() 
        self.context.set_extends(context)
        self.overlay = overlay
        super().__init__(iterable)

    def overlay_chain(self, depth_first:bool=False, include_self=False):
        if self.overlay is None:
            if include_self: 
                yield self
            return
        
        if depth_first:
            yield from self.overlay.overlay_chain(True)
            if include_self: 
                yield self
            return
        
        if include_self: 
            yield self
        yield from self.overlay.overlay_chain(True)

    def get(self, key, /, default:Any=_UNSET, use_overlay:bool=True, localize:bool=True, resolve:bool=True, resolve_nodepath:bool=True, _unset_ok:bool=False, ):
        res = self.data.get(key, _UNSET)

        if (res is _UNSET) and use_overlay and not (self.overlay is None):
            res = self.overlay.get(use_overlay, localize=localize, resolve=resolve, _unset_ok=True, resolve_nodepath=False)

        if (res is _UNSET):
            if _unset_ok:
                return res
            raise KeyError(key)

        if isinstance(res, NodePath) and resolve_nodepath:
            return self.context.node.get_node(res, default=res)

        if isinstance(res, Resource) and localize and not isinstance(res, Node):
            if res.is_subresource():
                _c_resource = self.context.resource  
                if not (_c_resource is None) and (res.id in _c_resource.sub_resources):
                    return _c_resource.sub_resources[res.id]
                return res
            else:
                _c_project = self.context.project  
                if not (_c_project is None) and (res.id in _c_project.resources):
                    return _c_project.resources[res.id]
                return res
            
        elif isinstance(res, ResourceRef) and resolve:
            return res.resolve(self.context, default=res)

        elif isinstance(res, ExtResource) and resolve:
            _res = res.resource.resolve(self.context)
            if isinstance(_res, Resource):
                return _res
            return res 

        return res

    def set(self, key, value):
        o_val = self.data.get(key, _UNSET)

        if isinstance(value, Node):
            res = self.context.node.get_path(value)

        elif isinstance(value, (Resource, File, ExtResource)):
            value = ResourceRef(value)

        self.data[key] = res
    
        if hasattr(o_val, "_dereference_callback"):
            o_val._dereference_callback(self.context)

class Resource():
    ## All :
    context : Context
    replace_promise : Signal[ResourceRef.Type, str|Self]

    ## Resource Only :
    _file : None|ResourceRef[str, File] = None
    file = ResourceRefProperty("_file", ResourceRef.Type.File)
    uid : None|CollectionKey[str] = None

    sub_resources : Collection[str,Resource]
    ext_resources : Collection[str,ExtResource]

    ## Subresource & Resource :

    id : CollectionKey[str]
    properties : Properties

    @classmethod    
    def construct(cls, id:str|None=None, uid:str|None=None, file:str|None=None, nodes:Iterable[Node]=tuple(), sub_resources:Iterable[Resource]=tuple(), properties:Iterable|dict=tuple(), context:Context|None=None):
        inst = cls(id, None, None)

        inst.nodes.extend(nodes)
        inst.sub_resources.extend(sub_resources)
        inst.properties.extend(properties)

        if uid or file:
            inst.__setup_file__(uid, file)

        if not (context is None):
            inst._reference_callback(context)

        return inst


    def __setup__(self):
        self.context = Context(subresource=self)

        self.context.callback("resource", self._on_resource_set, weak=True)
        self.context.callback("project", self._on_project_set, weak=True)

        self.properties = Properties(context=self.context)

        self.replace_promise = Signal(self)
        self.id = CollectionKey()

    def __setup_file__(self, uid:str|None=None, file:File|None=None):
        self.uid = CollectionKey(uid)
        self.file = CollectionKey(file)

    def __init__(self, id:str|None=None, uid:str|None=None, file:str|File|None=None):
        self.id.key = id

        if uid or file:
            self.__setup_file__(uid, file)
        
    def _reference_callback(self, context:Context):
        ''' Append self to structure based on scope, emit replace callback when doing so
        Structural assertions happen here w/a 
        '''
        if not (context.project is None):
            self._on_project_set(context.project)
        if not (context.resource is None):
            self._on_resource_set(context.resource)

    def _on_resource_set(self, resource):
        if not self.is_subresource():
            return
        if resource is None:
            return
        
        if self.context.resource == resource:
            return

        if not (self.resource is None):
            raise StructureError("structure cross-populatin not allowed!")
        
        if not (self in resource.sub_resources):
            resource.sub_resources.append(self, supress_callback=True)

        self.context.set_extends(resource.context)
        self.replace_promise(ResourceRef.Type.SubResource, self.id.key)

    def _on_project_set(self, project):
        if self.is_subresource():
            return
        if project is None:
            return

        if self.context.project == project:
            return
        if not (self.project is None):
            raise StructureError("structure cross-populatin not allowed!")
        
        if not (self in project.resources):
            project.append(self, supress_callback=True)

        self.context.set_extends(project.context)
        self.replace_promise(ResourceRef.Type.Resource, self.uid.key)

    def _dereference_callback(self, context:Context):
        pass

    def is_subresource(self)->bool:
        return (self.uid is None) or (self.uid.key is None)

class File():
    context : Context

    _resource : None|ResourceRef[str, Resource] = None
    resource = ResourceRefProperty("_resource", ResourceRef.Type.RID)

    promise_callback : Signal[ResourceRef.Type, str|Self]

    def __setup__(self):
        self.context = Context()

    def _reference_callback(self, context:Context):
        if not (context.project is None):
            self._on_project_fullfilled(context.project)
        else:
            context.callback("project", self._on_project_fullfilled,  once=True, weak=True)

    def _on_project_fullfilled(self, project:None|Project):
        self.context.set_extends(project.context)

class NodePath(str): ...

class Node(Resource):
    overlay : None|Self = None
    
    # All:
    id : CollectionKey[int]
    name : CollectionKey[str]
    children : Collection[str, Node]

    # As Resource:
    nodes : Collection[int, Node]

    @classmethod    
    def construct(cls, id:int|None=None, uid:str|None=None, file:str|None=None, nodes:Iterable[Node]=tuple(), sub_resources:Iterable[Resource]=tuple(), properties:Iterable|dict=tuple(), context:Context|None=None, overlay:None|Self=None):
        inst = cls(id, None, None)

        inst.nodes.extend(nodes)
        inst.sub_resources.extend(sub_resources)
        inst.properties.extend(properties)

        if uid or file:
            inst.__setup_file__(uid, file)

        if not (context is None):
            inst._reference_callback(context)

        if overlay:
            inst.set_overlay(overlay)

        return inst

    def __setup__(self):
        super().__setup__()
        self.nodes = Collection(key_attr="name", context=self.context)

    def __setup_file__(self, uid = None, file = None):
        self.nodes = Collection(key_attr="id", context=self.context)
        super().__setup_file__(uid, file)

    def _on_child_appended(self, child:Node):
        assert child.context.parent in (None, self)
        child.context.set_extends(self.context)
        child.context.parent = self

    def _on_child_removed(self, child:Node):
        child.context.parent = None