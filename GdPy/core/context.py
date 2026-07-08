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
        if not (self._extends is None):
            return getattr(self._extends, attr, None)
        elif attr in self._slots_:
            return None
        raise AttributeError(obj=self,name=attr)
    
    def __setattr__(self, attr, value):
        if attr in self._slots_:
            res = super().__setattr__(attr, value)
            self.signal_value_updated(attr, value)
            return res
        return super().__setattr__(attr, value)

    def _get_filled_slots(self)->dict:
        res = {}
        for k in self._slots_:
            if hasattr(self,k):
                res[k] = getattr(self,k)
        return res

    def _iter_extends(self,):
        if self._extends:
            yield from self._extends._iter_extends()
            yield self._extends

    def set_extends(self, extends:StructContext|None):
        if self._extends:
            self._extends.signal_value_updated.disconnect(self.signal_value_updated)
        ##TODO: DIF THIS SHIT TO EXTEND!!
        old = {} 
        for e in self._iter_extends():
            old.update(e._get_filled_slots())

        self._extends = extends
        new = {}
        for e in self._iter_extends():
            new.update(e._get_filled_slots())

        _old_keys = old.keys()
        _new_keys = new.keys()

        rem = filter(lambda k: not k in _new_keys, _old_keys)
        add = filter(lambda k: not k in _old_keys, _new_keys)
        change = filter(lambda k: (k in _old_keys) and not (getattr(new,k) is getattr(old,k)), _new_keys)

        for k in (*rem, *add, *change):
            self.signal_value_updated(k, getattr(self,k))

        if extends:
            extends.signal_value_updated.connect(self.signal_value_updated)

    def callback(self, key:str, callback:Callable, once:bool=False, local_only=False):
        # raise Exception(key)
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