from __future__ import annotations
from typing import Any, Callable
from .signals import Signal

class StructContext(object):
    _extends : StructContext = None
    _slots_ : tuple[str] = tuple()

    signal_value_updated : Signal[str,Any]
    signal_parent_value_updated : Signal[str,Any]

    def __init_subclass__(cls):
        cls.__slots__ = tuple( set(cls._slots_) | set(("_extends","signal_value_updated",))) 

    def __setup__(self):
        self.signal_value_updated = Signal(owner=self)

    def __init__(self, extends:StructContext=None, **kwargs):
        self.__setup__()
        if extends:
            self.set_extends(extends)
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __getattr__(self, attr):
        if attr in self._slots_:
            return getattr(self._extends, attr, None)
        raise None
    
    def __setattr__(self, attr, value):
        if attr in self._slots_:
            res = super().__setattr__(attr, value)
            self.signal_value_updated(attr, value)
            return res
        return super().__setattr__(attr, value)

    def set_extends(self, extends:StructContext|None):
        if self._extends:
            self._extends.signal_value_updated.disconnect(self.signal_value_updated)
        self._extends = extends
        if extends:
            extends.signal_value_updated.connect(self.signal_value_updated)

    def callback(self, key:str, callback:Callable, once:bool=False, local_only=False):
        def func(origin, attr, val):
            if (not (origin is self)) and local_only:
                return
            if attr != key:
                return
            res = callback(val)
            if once:
                return Signal.REMOVE
            return res
        
        self.signal_value_updated.connect(func, include_owner=True)