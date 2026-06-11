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
    
    def extend(self, iterable):
        for x in iterable:
            self.append(x)

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
    
    def values(self,):
        return self.values.__iter__()
    
class Context():
    project      : ContextVar[Any]
    load_session : ContextVar[Any]
    file_db      : ContextVar[Any]
    file         : ContextVar[Any]
    resource     : ContextVar[Any]
    subresource  : ContextVar[Any]

    def __init__(self,):
        self.project = ContextVar(str(id(self))+"_project")
        self.load_session = ContextVar(str(id(self))+"_load_session")
        self.file = ContextVar(str(id(self))+"_file")
        self.resource = ContextVar(str(id(self))+"_resource")
        self.subresource = ContextVar(str(id(self))+"_subresource")
        self.file_db = ContextVar(str(id(self))+"_file_db")
    
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
        if is_root: 
            buffer = {}
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
        func = getattr(self.obj, func_name, None)
        if not (func is None):
            func(context, *args, **kwargs)
        for x in self.layer_children.get(layer, tuple()):
            x.call(layer, func_name, context, *args, **kwargs)