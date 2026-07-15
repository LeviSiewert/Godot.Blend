from __future__ import annotations
from .context import StructContext
from typing import Any

from collections import UserDict

from .signals import Signal

class GdValue():
    ''' Base class for all writeable atomic values, prim for isinstance checking '''

class _ResourceFlag:...
class _FileFlag:...

class DelayedReference[T:Any]():
    ''' Delayed load of this type '''
    replace: Signal[T]
    def __init__(self):
        self.replace = Signal(self,)

class _SetContextMixin():
    def _set_item_context(self, key, value):

        if isinstance(value,_ResourceFlag):
            l_res = self.context.resource
            v_res = value.context.resource

            if not value.is_file:
                value.context.set_extends(self.context)
                
            elif not(l_res is None) and not (v_res is None):
                assert (l_res is v_res)

        elif isinstance(value,_FileFlag):
            pass

        elif hasattr(value, "context"):
            value.context.set_extends(self.context)

        elif isinstance(value, DelayedReference):
            value.replace.connect(lambda x: self.__setitem__(key,x), once=True)
    

class PropertyCollection(UserDict, _SetContextMixin):
    context : StructContext
    overlay : PropertyCollection|None = None
    pinned : list[str]

    def __init__(self, iterable=tuple(), /, context:StructContext=None,):
        self.context = StructContext(extends=context)
        super().__init__(iterable)

    def __missing__(self, key)->Any:
        if not (self.overlay is None):
            return self.overlay[key]
        raise KeyError(key)
    
    def __setitem__(self, key, value):

        if not isinstance(key, str):
            raise TypeError("Property Collection Key must be str!")

        if (not isinstance(value, GdValue)) and isinstance(value, (dict, list)):
            raise TypeError("This object cannot intake base dicts or lists due to context object support. Use values.Dictionary or values.Array instead")

        self._set_item_context(key, value)

        return super().__setitem__(key, value)
        
    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("{}")})"
    
    def set_overlay(self, overlay:PropertyCollection|None):
        self.overlay = overlay