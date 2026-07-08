from __future__ import annotations
from typing import Callable, Any
from inspect import get_annotations

class SignalSubscriber():
    func : Callable
    owner : Any = None

    def __init__(self, func, owner=None):
        self.func = func
        self.owner = owner
        
    def __call__(self,*args,**kwargs):
        if self.owner:
            return self.func(self.owner, *args, **kwargs)
        
        return self.func(*args, **kwargs)

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
                to_rem.append(x)
        for x in to_rem:
            self.subscribers.remove(x)

    def connect(self, func, include_owner=False):
        if include_owner:
            self.subscribers.append(SignalSubscriber(func, self.owner))
        else:
            self.subscribers.append(SignalSubscriber(func, None))

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