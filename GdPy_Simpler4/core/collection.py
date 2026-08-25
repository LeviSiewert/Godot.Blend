from __future__ import annotations

from typing import Any, Iterable, Callable
from collections import UserDict
from string import digits, ascii_letters

import random 

from .signals import Signal
from .context import Context


class _UNSET:...

class CollectionKey[K:str|int]():
    _key : None|K = None
    _src : Any

    key_updated : Signal[Any, K]

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key
        self.key_updated(self.src, key)

    def __setup__(self):
        self.key_updated = Signal(self)

    def __init__(self, /, src, key=None):
        self.__setup__()
        self.src = src
        self._key = key


# class CollectionKeyProperty():
#     attr : str
    
#     def __init__(self, attr):
#         self.attr = attr

#     def __get__(self, instance, owner):
#         promise : None|CollectionKey = getattr(instance, self.attr, None)
#         if promise is None:
#             return None
#         return promise.key

#     def __set__(self, instance, value):
#         promise : None|CollectionKey = getattr(instance, self.attr, None)
#         if promise is None:
#             return setattr(instance, self.attr, CollectionKey(instance, key = value))

from enum import Enum

class Collection[K:str|int,V:Any](UserDict):
    context : Context

    key_attr : str

    data : dict[K,V]

    appended : Signal[K,V]
    removed : Signal[K,V]
    renamed : Signal[K,K,V]
    replaced : Signal[K,V,V]

    key_is_string : bool = True
    key_increment : bool = False
    key_formatter : None|Callable = None 

    def __setup__(self):
        self.data = {}

        self.context = Context()

        self.appended = Signal(self)
        self.removed = Signal(self)
        self.renamed = Signal(self)
        self.replaced = Signal(self)

    def __init__(self, key_attr:str, iterable:Iterable=tuple(), context:Context=None, key_is_string:bool=True, key_resolve_incriment:bool=False, key_formatter:Callable|None=None):
        self.__setup__()

        self.key_is_string = key_is_string
        self.key_increment = key_resolve_incriment
        self.key_formatter = key_formatter

        self.key_attr = key_attr

        if context:
            self.context.set_extends(context)

        if iterable:
            self.extend(iterable)
            
    def append(self, item, /, rename=True, right_key_priority=True):
        if (item in self):
            raise ValueError("Item already in collection!")
        
        key = getattr(item, self.key_attr).key
        if key is None:
            key = self.generate_key(item)
            getattr(item, self.key_attr)._key = key

        if (key in self) and (rename is False):
            raise ValueError("key is already fullfilled in collection!")
        elif (key in self):
            self._resolve_key_collision(key, self[key], item, replace=False, rename=True, right_key_priority=right_key_priority)
            return

        self.data[key] = item
        self._connect(item)
        self.appended(key, item)

    def extend(self, items:Iterable[V], /, rename=True, right_key_priority=True):
        for i in items:
            self.append(i, rename=rename, right_key_priority=right_key_priority)

    def remove(self, key_or_item:V|K):
        if isinstance(key_or_item, (str,int)):
            key = key_or_item
            item = self[key]
        else:
            key = self.find_key(key_or_item)
            item = key_or_item

        self._disconnect(item)
        del self.data[key]
        self.removed(key, item)

    def rename(self, item:V, key:K, /, rename=False, replace=False, right_key_priority=True):
        assert (item in self)

        c_key = self.find_key(item)
        c_val = self.get(key, None)

        if c_val is item:
            return

        if c_val:
            self._resolve_key_collision(key, c_val, item, rename=rename, replace=replace, right_key_priority=right_key_priority)
            return

        del self.data[c_key]
        getattr(item, self.key_attr)._key = key
        self.data[key] = item
        self.renamed(c_key, key, item)

    def find_key[D](self, item:V, default:D=_UNSET)->D|V:
        for k,v in self.data.items():
            if v is item:
                return k
        if default is _UNSET:
            raise ValueError(item)
        return default

    def _resolve_key_collision(self, key:K, l_val:V, r_val:V, /, rename:bool=False, replace:bool=False, right_key_priority=True):
        ## Integrates/Appends
        assert (rename or replace)

        if not right_key_priority:
            ## Switch values, making it true!
            l_val, r_val = r_val, l_val 

        l_key : K = self.find_key(l_val, None)
        r_key : K = self.find_key(r_val, None)

        if (replace):
            if (r_key is key):
                return
            if (l_key):
                del self.data[l_key]
                self._disconnect(l_val)

            self.data[key] = r_val
            getattr(r_val, self.key_attr)._key = key

            if r_key is None: #Meaning isnt already connected!
                self._connect(r_val)

            self.renamed(r_key, key, r_val)
            self.replaced(key, l_val, r_val)
            return

        # if (rename):
        
        if self.key_increment:
            new_l_key = self.incriment_key(l_val, key)
        else:
            new_l_key = self.generate_key(l_val)

        assert new_l_key != key

        self.data[new_l_key] = l_val
        getattr(l_val, self.key_attr)._key = new_l_key

        if l_key is None:
            self._connect(l_val)
            self.appended(l_key, l_val)
        else:
            self.renamed(l_key, new_l_key, l_val)

        self.data[key] = r_val
        getattr(r_val, self.key_attr)._key = key
        if r_key is None:
            self._connect(r_val)
            self.appended(r_key, r_val)
        self.replaced(key, l_val, r_val)


    def _connect(self, item):
        getattr(item, self.key_attr).key_updated.connect(self._on_rename_signal, weak=True)

    def _disconnect(self, item):
        getattr(item, self.key_attr).key_updated.disconnect(self._on_rename_signal)

    def _on_rename_signal(self, item, key):
        self.rename(item, key, rename=True)

    def __contains__(self, key):
        if isinstance(key, (int,str)):
            return (key in self.data.keys())
        return key in self.data.values()

    def incriment_key(self,obj:V,key:K)->K:
        if isinstance(key, int):
            return self.incriment_integer_key(obj,key)
        if isinstance(key, str):
            return self.incriment_string_key(obj,key)
        raise KeyError(key)

    def incriment_integer_key(self, obj:V, key:int):
        keys = tuple(self.keys())
        i = 1
        if not (self.key_formatter is None):
            n_key = self.key_formatter(self, obj, key+i)
        else:
            n_key = key+i
        while n_key in keys:
            if not (self.key_formatter is None):
                n_key = self.key_formatter(self, obj, key+i)
            else:
                n_key = key+i
            i = i+1
        return n_key
    
    def incriment_string_key(self, obj:V, key:str):
        keys = tuple(self.keys())
        i = 1
        if not (self.key_formatter is None):
            n_key = self.key_formatter(self, obj, key.rstrip(digits))
        else:
            n_key = key.rstrip(digits)
        while n_key in keys:
            if not (self.key_formatter is None):
                n_key = self.key_formatter(self, obj, f"{key}{i}")
            else:
                n_key = f"{key}{i}"
            i = i+1
        return n_key

    def _generate_key(self,obj:V)->K:
        if self.key_is_string:
            res = "".join(random.sample(ascii_letters, 9))
        else:
            res = random.randint(100000, 999999)
        if not (self.key_formatter is None):
            return self.key_formatter(self, obj, res)

    def generate_key(self,obj:V)->K:
        keys = self.data.keys()
        k = self._generate_key(obj)
        i = 0
        while k in keys:
            k = self._generate_key(obj)
            i = i+1
            if i > 99:
                raise Exception("")
        return k