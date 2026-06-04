from typing import Self, Callable, Any
from inspect import get_annotations

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

    def __call__(self, *args, **kwds):
        to_rem = []
        for x in self.subscribers:
            res = x(*args, **kwds)
            if res is self.REMOVE:
                to_rem.append(res)
        for x in to_rem:
            self.subscribers.remove(res)

    def connect(self, func, include_owner=False):
        if include_owner:
            self.subcribers.append(SignalSubscriber(func))
        else:
            self.subcribers.append(SignalSubscriber(func, self.owner))

    def disconnect(self, func):
        to_rem = []
        for x in self.subscribers:
            if x.func == func:
                to_rem.append(x)
        for x in to_rem:
            self.subscribers.remove(x)
        
class SignalContainer: 
    def __init__(self):
        
        for k,v in get_annotations(self.__class__):
            if isinstance(v,dict):
                continue
            if v is Signal:
                setattr(self,k,Signal())

        super().__init__()


class Collection():
    ''' Dict with multiple keys & signals for changing keys '''
    ## TODO