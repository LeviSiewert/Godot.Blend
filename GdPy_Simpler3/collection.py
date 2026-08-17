from __future__ import annotations

from collections import UserDict
from .signal import Signal
from .context import Context

from typing import Any, Self, Iterable
from weakref import ReferenceType

class _UNSET:...

class CollectionKey[K:str|int]():
    _key : None|K = None
    key_updated : Signal[K]

    def __init__(self, key:None|K=None):
        self.key_updated = Signal(self)
        self._key = key

    def __repr__(self):
        return f"CollectionKey('{self.key}')"

    @property
    def key(self):
        return self._key
    @key.setter
    def key(self,val):
        o_val = self._key
        try:
            self._key = val
            self.key_updated(val)
        except:
            self._key = o_val
            self.key_updated(o_val)
            raise

class _ItemIO():
    overlay : None|Self = None
    overlay_updated : Signal[Self]

    key : CollectionKey[str]

    def set_overlay(self, src:None|Self):...
    

class Collection[K:str|int,V:object](UserDict):
    context : Context
    _key_attr : str

    # overlay : None|Self = None
    # overlay_updated : Signal[Self]

    appended : Signal[K,V]
    removed : Signal[K,V]
    renamed : Signal[K,K,V]
    updated : Signal[K,V,V]

    def __init__(self, iterable:Iterable=None, /, key_attr:str=None, context:Context=None):
        self._key_attr = key_attr
        self.__setup__()
        self.context.set_extends(context)

        if not (iterable is None):
            self.extend(iterable)

    def __setup__(self):
        self.context = Context()

        self.overlay_updated = Signal(self)

        self.appended = Signal(self)
        self.removed = Signal(self)
        self.renamed = Signal(self)
        self.updated = Signal(self)

    def append(self, item:V, replace=False, rename=False, right_priority=True, supress_callback:bool=False):
        if (item in self):
            raise KeyError("Item is already in collection!")

        key = self._get_key(item, generate=True)
        c_item = self.get(key, None)

        if (c_item is item): 
            return

        if (c_item is None):
            self.data[key] = item
            self._connect(item, supress_callback=supress_callback)
            self.appended(key, item)
        else:
            self.resolve_key_colision(key, l_item=c_item, r_item=item, replace=replace, rename=rename, right_priority=right_priority, ensure_appended=True, supress_callback=supress_callback)

    def rename(self, item:V, key:K, replace=False, rename=False, right_priority=True):
        if not (item in self):
            raise KeyError("Item isnt in collection!")

        c_key = self._get_key(item)
        c_item = self.get(key, None)

        if (c_item is item): 
            return

        if c_item is None:
            del self.data[c_key]
            self.data[key] = item
            self.renamed(c_key, key, item)
        else:
            self.resolve_key_colision(key, l_item=c_item, r_item=item, replace=replace, rename=rename, right_priority=right_priority)

    def remove(self, item:V, supress_callback:bool=False):
        if not (item in self):
            raise KeyError("Item isnt in collection!")

        key = self._get_key(item)

        del self.data[key]
        self._disconnect(item, supress_callback=supress_callback)
        self.removed(key, item)

    def replace(self, key:K, item:V, supress_reference_callback:bool=False, supress_dereference_callback:bool=False):
        if not (key in self.data.keys()):
            raise KeyError(key)
        l_item = self.data[key]
        if l_item is item: 
            return
        self._disconnect(l_item, supress_callback=supress_dereference_callback)
        self._set_key(key, item, supress_callback=supress_reference_callback)
        self.updated(key, l_item, item)

    def __setitem__(self, key, item):
        self._set_key(key, item, append=True)

    def __delitem__(self, key):
        item = self.get(key)
        del self.data[key]
        self.removed(key, item)

    def resolve_key_colision(self,key, l_item, r_item, replace=False, rename=False, right_priority=True, ensure_appended=False, supress_callback:bool=False)->tuple[K,K]:
        ## Ensure both local, set keys on each. resolve. replace has priority over rename. error if both true?

        if replace:
            assert not rename
            del self[key]
            self._set_key(r_item, append=ensure_appended, supress_callback=supress_callback)
            return None, key

        if right_priority:
            r_key = self.generate_key(r_item)
            self._set_key(l_item, key, append=ensure_appended, supress_callback=supress_callback)
            self._set_key(r_item, r_key, append=ensure_appended, supress_callback=supress_callback)
            return key, r_key
        else:
            l_key = self.generate_key(r_item)
            self._set_key(r_item, key, append=ensure_appended, supress_callback=supress_callback)
            self._set_key(l_item, self.generate_key(), append=ensure_appended, supress_callback=supress_callback)
            return l_key, key

    def _get_key(self, item:V, generate:bool=False)->K:
        ckey = getattr(item, self._key_attr, None)

        if (ckey is None):
            for k,v in self.data.items():
                if v is item:
                    return k
            if generate:
                return self.generate_key()
            return None
        return ckey.key

    def _set_key(self, item:V, key:K, append:bool=True, supress_callback:bool=False):
        ''' Set key, prereq that key is not already fullfilled! '''

        c_item = self.data.get(key, None)
        if (c_item is item):
            return
        elif not (c_item is None):
            raise KeyError(key, "key is alreaady fillfilled!, use rename or similar!")

        ckey = getattr(item, self._key_attr, None)
        l_key = self._get_key(item, generate=False)

        if not (ckey is None):
            ckey._key = key

        if not (l_key is None):
            del self.data[l_key]
            self.data[key] = item
            self.renamed(l_key, key, item)
        else:
            if not append:
                raise ValueError("item must already be part of collection if append is false!") 
            self.data[key] = item
            self._connect(item, supress_callback=supress_callback)
            self.appended(key, item)

    def _connect(self, item:V, supress_callback:bool=False):
        if not ((ckey := getattr(item, self._key_attr,None)) is None):
            ckey : CollectionKey
            ckey.key_updated.connect(self.rename)
        if (not supress_callback) and (func:=getattr("_reference_callback", None)):
            func(self.context)

    def _disconnect(self, item:V, supress_callback:bool=False):
        if not ((ckey := getattr(item, self._key_attr,None)) is None):
            ckey : CollectionKey
            ckey.key_updated.connect(self.rename)
        if (not supress_callback) and (func:=getattr("_dereference_callback", None)):
            func(self.context)

class _CollectionOverlayable(Collection):
    ''' Collection where overlayed collections actions are propogated upwards and items are integrated '''

    overlay : Self|None=None
    overlay_updated : Signal

    def __setup__(self):
        super().__setup__()
        self.overlay_updated = Signal(self)

    def __init__(self, iterable = None, /, context = None, overlay:None|Self = None):
        super().__init__(iterable, context)
        self.set_overlay(overlay)

    def set_overlay(self, overlay:None|Self):
        raise NotImplementedError()
