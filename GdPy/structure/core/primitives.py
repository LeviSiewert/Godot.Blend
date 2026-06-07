from __future__ import annotations
from typing import Self, Callable, Any
from inspect import get_annotations
from abc import ABC, abstractmethod
from contextvars import ContextVar
from contextlib import contextmanager

class SignalSubscriber():
    func : Callable
    pre_args : list

    def __init__(self,func, *pre_args):
        self.func = func
        self.pre_args = pre_args
        
    def __call__(self,*args,**kwargs):
        return self.func(*self.pre_args, *args, **kwargs)

class Signal():
    class REMOVE: pass
    subscribers : list[SignalSubscriber]
    owner : Any

    def __init__(self,owner):
        self.owner = owner
        self.subscribers = []

    def __call__(self, *args, **kwds):
        to_rem = []
        for x in self.subscribers:
            res = x(*args, **kwds)
            if res is self.REMOVE:
                to_rem.append(res)
        for x in to_rem:
            self.subscribers.remove(res)
    
    def forward(self, *args, **kwargs):
        self(self.owner, *args, **kwargs)

    def connect(self, func, include_owner=False):
        if include_owner:
            self.subscribers.append(SignalSubscriber(func))
        else:
            self.subscribers.append(SignalSubscriber(func, self.owner))

    def disconnect(self, func):
        to_rem = []
        for x in self.subscribers:
            if x.func == func:
                to_rem.append(x)
        for x in to_rem:
            self.subscribers.remove(x)
        
class SignalContainer: 
    def __init__(self):
        classes_limited = []
        for x in self.__class__.__mro__:
            if x is SignalContainer:
                break
            classes_limited.append(x)
        for clss in classes_limited:
            for k,v in get_annotations(clss).items():
                if not isinstance(v,str):
                    continue
                if v.startswith("Signal"):
                    setattr(self,k,Signal(self))

        super().__init__()


class Collection[T](ABC, SignalContainer):
    items : list[T]
    item_appended : Signal
    item_removed : Signal
    
    def __init__(self):
        items = []
        self.item_appended = Signal(self) 
        self.item_removed = Signal(self)
        super().__init__()
    
    def append(self, item:T):
        self._integrate(item)
        self.item_appended.emit(item)

    def remove(self, item:T):
        self._disintegrate(item)
        self.item_removed.emit(item)
    
    @abstractmethod
    def _integrate(item:T):
        pass
    
    @abstractmethod
    def _disintegrate(item:T):
        pass

    @abstractmethod
    def __getitem__(self, key)->T:
        return None
    
    def get(self, key, default):
        res = self[key]
        if res is None:
            return default
        return res
    
class Context():
    project      : ContextVar[Any]
    load_session : ContextVar[Any]
    file         : ContextVar[Any]
    resource     : ContextVar[Any]
    subresource  : ContextVar[Any]

    def __init__(self,):
        self.project = ContextVar(str(id(self))+"_project")
        self.load_session = ContextVar(str(id(self))+"_load_session")
        self.file = ContextVar(str(id(self))+"_file")
        self.resource = ContextVar(str(id(self))+"_resource")
        self.subresource = ContextVar(str(id(self))+"_subresource")
    
    @contextmanager
    def w(self, key:str,val:Any):
        if var := getattr(self,key):
            token=var.set(val)
            yield
            var.reset(token)


# buffer : ContextVar[dict[str,ContextVar[list]]]
buffer : dict[str, ContextVar[list]] = {}
class CacheTreeNode():
    obj : Any
    trailing : dict[str, list]
    layer_keys : tuple[str]
    layer_children : dict[str,list]
    
    def __init__(self, obj, layer_keys:tuple[str]):
        self.obj = obj
        self.layer_keys = layer_keys
        self.layer_children = {}

    @contextmanager
    def traverse(self, is_root:bool=False):
        tokens = self.enter()
        yield
        self.exit(tokens)
        if is_root:
            self.claim_buffer()
    
    def claim_buffer(self,):
        self.trailing = {}
        for k,v in buffer.items():
            value = v.get()
            if not isinstance(value,list):
                continue
            self.trailing[k] = value
        buffer.clear()

    def enter(self,)->dict[str,str]:
        tokens = {}
        for k in self.layer_keys:
            buffer[k].get().append(self)
        for k in self.layer_keys:
            tokens[k] = buffer[k].set([]) #my Children
        return tokens
    
    def exit(self, tokens:dict[str,str]):
        for k in self.layer_keys:
            lst = buffer[k].get()
            self.layer_children[k] = lst #Attach my children
            buffer[k].reset(tokens[k])   #pass back up towards siblings.

    def __eq__(self, value)->bool:
        if (value is self) or (self.obj == value):
            return True
        if isinstance(value, CacheTreeNode):
            return value.obj == self.obj
        return False
    
    def call(self, layer:str, func_name:str, context:Context, *args, **kwargs):
        ctx_key = getattr(self.obj, "context_key", None)
        if ctx_key:
            with context.w(ctx_key,self.obj):
                self._call(layer,func_name,context,*args,**kwargs)
        else:
            self._call(layer,func_name,context,*args,**kwargs)

    def _call(self, layer:str, func_name:str, context:Context, *args, **kwargs):
        getattr(self.obj, func_name)(context, *args, **kwargs)
        for x in self.layers.get(layer, tuple()):
            x.call(layer, func_name, context, *args, **kwargs)


# class CacheTree():
#     ''' Secondary Layered Tree for optimizing tree calls in arbitrary data structures 
#     Planned usage is with parsing & secondary/defered calls to the tree.
#     IE: 
#         - Defered loading 
#         - Attaching References in a load pipeline
#         - Constructing a NodeTree
#     TODO:
#         - Consider integrated layers, instead of categorical
#         - Consider methods for tree joining
#         - Consider use of tree maintnance
#     '''
#     layers : dict[str, CacheTreeLayer]

#     def __init__(self, layers:list[str]):
#         self.layers = {}
#         for k in layers:
#             self.layers[k] = CacheTreeLayer()

#     def __getitem__(self, key):
#         return self.layers[key]
#     def __setitem__(self, key, val):
#         self.layers[key] = val

#     def append(self, obj, *args, **kwargs):
#         layers = self.get_layers(obj)
#         for k in layers:
#             self[k].append(obj, *args,**kwargs)
#     def remove(self, obj, *args, **kwargs):
#         layers = self.get_layers(obj)
#         for k in layers:
#             self[k].remove(obj, *args,**kwargs)
#     def buffer_append(self, obj, *args, **kwargs):
#         layers = self.get_layers(obj)
#         for k in layers:
#             self[k].buffer_append(obj, *args,**kwargs)
#     def buffer_remove(self, obj, *args, **kwargs):
#         layers = self.get_layers(obj)
#         for k in layers:
#             self[k].buffer_remove(obj, *args,**kwargs)
#     def buffer_claim(self, obj, *args, **kwargs):
#         layers = self.get_layers(obj)
#         for k in layers:
#             self[k].buffer_claim(obj, *args,**kwargs)

#     def get_layers(self,obj):
#         res = getattr(obj,"_cache_layers",tuple())
#         if "*" in res:
#             return self.layers.keys()
#         return res

# class CacheTreeLayer():
#     # TODO: Find nested objects for pruning & joining

#     buffer : list[CacheTreeNode]
#     root_nodes : list[CacheTreeNode]

#     def __init__(self):
#         self.buffer = []
#         self.root_nodes = []

#     def append(self, node:CacheTreeNode):
#         self.root_nodes.append(node)

#     def remove(self, node:CacheTreeNode):
#         self.root_nodes.remove(node)

#     def buffer_append(self, obj:CacheTreeNode|Any):
#         if obj in self.buffer:
#             return
#         if isinstance(obj, CacheTreeNode):
#             self.buffer.append(object)
#         else:
#             self.buffer.append(CacheTreeNode(obj))

#     def buffer_remove(self, obj:CacheTreeNode|Any):
#         self.buffer.remove(object)

#     def buffer_claim(self, obj:Any):
#         self.root_nodes.append(CacheTreeNode(obj, self.buffer))
#         self.buffer = []
        
#     def call(self, func_name:str, _depth_first:bool=True, _ctx_func_name:str=None, *args, **kwargs):
#         for x in self.root_nodes:
#             x.call(func_name, _depth_first, _ctx_func_name, *args, **kwargs)

# class CacheTreeNode():
#     obj : Any
#     children : list[CacheTreeNode]

#     def __init__(self, obj, children:list[CacheTreeNode]):
#         self.obj = obj
#         self.children = children

#     def _call(self, func_name:str, context:Context, _depth_first:bool=True, *args, **kwargs):
#         if not _depth_first:
#             getattr(self.obj,func_name)(*args, **kwargs)
#         for x in self.children:
#             x.call(func_name, context, _depth_first, *args, **kwargs)
#         if _depth_first:
#             getattr(self.obj,func_name)(*args, **kwargs)

#     def call(self, func_name:str, context:Context, _depth_first:bool=True, *args, **kwargs):
#         ctx = getattr(self.obj, "context_key", None)
#         if not (ctx is None):
#             token = getattr(context,ctx).set(self.obj)
#             self._call(func_name, _depth_first, *args, **kwargs)
#             getattr(context,ctx).reset(token)
#         else:
#             self._call(func_name, _depth_first, *args, **kwargs)
    
#     def __eq__(self, obj):
#         if obj is self: 
#             return True
#         if obj is CacheTreeNode:
#             return obj.obj == self.obj
#         return False
    

# buffer : ContextVar[dict[str, ContextVar[list]]] = ContextVar("CacheTreeNode_buffer")
# trailing : ContextVar[dict[str,list[CacheTreeNode]]] = ContextVar("CacheTreeNode_trailing")

# class CacheTreeNodeV21():
#     obj : Any
#     layer_keys : list[str]
#     layers : dict[str,list]
    
#     def __init__(self, obj:Any, layer_keys:list[str]):
#         self.obj = obj
#         self.layers_keys = layer_keys
#         self.layers = {}

#     @contextmanager
#     def init_traversal(self,):
#         t1 = buffer.set({})
#         t2 = trailing.set({})
#         yield
#         buffer.reset(t1)
#         _trailing = trailing.get()
#         trailing.reset(t2)
#         return _trailing

#     @contextmanager
#     def traverse(self):
#         b = buffer.get()

#         tokens : dict[str, str] = {}
#         for k in self.layers_keys:
#             inst = []
#             if b[k].get() is None:
#                 if not (k in trailing.get().keys()):
#                     trailing.get()[k] = []
#                 trailing.get()[k].append(self) 
#                 ## First instance of layer in this traversal, so there are no acces-root. thus is trailing-root
#             tokens[k] = b[k].set(inst)

#         yield #Population of context via subnodes traversal

#         for k,v in tokens:
#             self.layers[k] = b[k].get()  #incorperate children
#             b[k].reset(v)                #reset buffer per incoperated layer children

#     def call(self, layer:str, func_name:str, context:Context, *args, **kwargs):
#         ctx_key = getattr(self.obj, "context_key", None)
#         if ctx_key:
#             with context.w(ctx_key,self.obj):
#                 self._call(layer,func_name,context,*args,**kwargs)
#         else:
#             self._call(layer,func_name,context,*args,**kwargs)

#     def _call(self, layer:str, func_name:str, context:Context, *args, **kwargs):
#         getattr(self.obj, func_name)(context, *args, **kwargs)
#         for x in self.layers.get(layer, tuple()):
#             x.call(layer:str, func_name:str, context, *args, **kwargs)