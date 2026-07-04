from __future__ import annotations
from typing import Any
from .signals import Signal

class StructContext():
    _extends : StructContext
    __slots__ : tuple[str] = tuple()

    signal_value_updated : Signal[str,Any]
    
    def __new__(cls):
        self = super().__new__(cls)
        self.signal_value_updated = Signal(owner=self)
        return self

    def __init__(self, extends:StructContext=None, **kwargs):
        if extends:
            self.set_extends(extends)
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __getattr__(self, attr):
        if attr in self.__slots__:
            if res:=getattr(self, attr):
                return res
            return getattr(self._extends, attr)
        return super().__getattr__(attr)
    
    def __setattr__(self, attr, value):
        if attr in self.__slots__:
            res = setattr(self,attr,value)
            self.signal_value_updated(attr, value)
            return res        
        return super().__setattr__(attr, value)

    def set_extends(self, extends:StructContext|None):
        if self._extends:
            self._extends.signal_value_updated.disconnect(self.signal_value_updated)
        self._extends = extends
        if extends:
            extends.signal_value_updated.forward(self.signal_value_updated)

