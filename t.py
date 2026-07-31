from __future__ import annotations
from collections import UserDict
from typing import Any, Callable, Generator, Type, Self
from types import LambdaType
from weakref import ReferenceType, ref as _wref
from enum import Enum
from copy import copy
from fsspec import AbstractFileSystem
from string import ascii_letters
import random



class _UNSET():...

class DifAction(Enum):
    DIF = 0 ## Identical local scope, changed children
    SET = 1 ## Replaced child, immutable type.
    ADD = 2 ## New child
    REM = 3 ## Rem child
    RE_KEY = 4 ## Reordered/Rekeyed children. Rekey, append/set new, reorder, finally sub-tree updates.
    # REF_IMPLIED = 5 ## Reference that remains the same, but was implied in changes elsewhere? 

class DifNode[T:Any]():
    ''' Reminder: This will be generated & integrated via tree transformers. '''
    cur : T|None
    new : T|None
    action : DifAction
    children : dict[str,DifNode] | list[DifNode]
    

class DISCONNECT():...

class _SignalSubscriber():
    callback : ReferenceType[Callable]
    _callback : None|Callable
    
    call_filter : LambdaType
    parent_signal : Signal
    prepend_source : bool
    once_only : bool

    def __repr__(self):
        return f"SignalSubscriber({str(id(self.callback()))})"

    def __init__(self, signal:Signal, callable:Callable, once_only:bool=False, prepend_source:bool=False, prepend_signal:bool=False, filter:LambdaType=None, weak=False):
        self.parent_signal = signal
        if not weak:
            self._callback = callable 
        self.callback = _wref(callable)
        self.once_only = once_only
        self.prepend_source = prepend_source
        self.prepend_signal = prepend_signal
        self.call_filter = filter

    def __call__(self, *args, **kwargs):
        func = self.callback()
        if func is None:
            self.disconnect()
            return

        if self.prepend_signal:
            args = (self.parent_signal, *args)

        if self.prepend_source:
            args = (self.parent_signal.source, *args)

        if not (self.call_filter is None):
            if not self.call_filter(*args,**kwargs):
                return

        res = func(*args, **kwargs)
        if (res is DISCONNECT) or self.once_only:
            self.disconnect()

    def disconnect(self):
        self.parent_signal._remove_subscriber(self)


class Signal[T:Any]():
    ''' On call, fwd call to all connected subscribers, disconnect or append arguments based on options'''
    source : Any
    subscribers : dict[int, _SignalSubscriber]

    def __init__(self, source):
        self.source = source
        self.subscribers = {}

    def connect(self, c:Callable, /, once_only=False, prepend_source=False, prepend_signal:bool=False, filter:LambdaType=None, weak=False)->int:
        ''' Returns an optional "token" that can be used if the callable is a lambda. "token" is subscriber object's id '''
        sub = _SignalSubscriber(self, callable=c, once_only=once_only, prepend_source=prepend_source, prepend_signal=prepend_signal, filter=filter, weak=False)
        return self._append_subscriber(sub)
        
    def disconnect(self, c:Callable, /, not_exist_ok:bool=False)->None:
        to_remove = []
        found = False
        for k,v in self.subscribers.items():
            if v.callback() is c:
                to_remove.append(k)
                found = True
            elif v.callback() is None:
                to_remove.append(k)
        s = self.subscribers
        
        if (found is False) and (not not_exist_ok):
            raise KeyError(c)
        for k in to_remove:
            self.t_disconnect(k)

    def t_disconnect(self, t:int)->None:
        del self.subscribers[t]

    def _append_subscriber(self,sub:_SignalSubscriber):
        self.subscribers[id(sub)] = sub
        return id(sub)
    
    def _remove_subscriber(self,sub):
        del self.subscribers[id(sub)]
        
    def __call__(self, *args, **kwargs):
        vs = tuple(self.subscribers.values())
        for v in vs:
            v(*args,**kwargs)

from contextvars import ContextVar

class Context():
    ''' Context object, attribute fallback through extends chain. Values set/changed along chain propigate to children. (including removed as None) '''
    _extends : Context = None
    _slots_ : tuple[str]
    _default = None
    element_changed : Signal
    default_null = ContextVar("", default=None)
    
    def __init__(self, **kwargs):
        self.element_changed = Signal(self)
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self,attr):
        ''' Called when attr is missing from local object '''
        if not (self._extends is None):
            return getattr(self._extends, attr, self.default_null.get())
        elif attr in self._slots_:
            return self.default_null.get()
        raise AttributeError(obj=self,name=attr)
        
    def __setattr__(self,attr,value):
        # if not (attr in self._slots_):
        #     raise AttributeError("Context attribute must exist in local slots to be assigned!", obj=self, name=attr)
        super().__setattr__(attr, value)
        if attr in self._slots_:
            self.element_changed(attr,value)

    def __delattr__(self, attr):
        super().__delattr__(attr)
        self.element_changed(attr, getattr(self, attr))

    def _iter_extends(self):
        if self._extends:
            yield from self._extends._iter_extends()
            yield self._extends

    def _get_local_elements(self,)->dict[str,Any]:
        ''' Return a dict that only contains slots fullfilled locally '''
        res = {}
        t = self.default_null.set(_UNSET)
        _dir = dir(self)
        for attr in filter(lambda x: x in _dir, self._slots_):
            res[attr] = getattr(self, attr)
        self.default_null.reset(t)
        return res

    def _get_all_elements(self,)->dict[str,Any]:
        ''' Return a dict that contains all slots fullfilled in extends chain '''
        res = self._get_local_elements()
        t = self.default_null.set(_UNSET)
        for c in reversed(tuple(self._iter_extends())):
            search = filter(lambda x: not (x in res.keys()), c._slots_)
            for attr in search:
                if not (getattr(c, attr) is _UNSET):
                    res[attr] = getattr(self, attr)
        self.default_null.reset(t)
        return res

    def set_extends(self, extends:Context|None, supress_changes:bool=False):
        ''' Set or clear extends, manage signal forwarding, and signal diffed values '''
        old = self._get_all_elements()
        cur = self._get_local_elements()

        if not(extends is None):
            _cur = extends._get_all_elements()
            _cur.update(cur)
            cur = _cur

        if not (self._extends is None):
            self._extends.element_changed.disconnect(self.element_changed)
        self._extends = extends
        if not (self._extends is None):
            self._extends.element_changed.connect(self.element_changed)

        if supress_changes:
            return

        _old_keys = tuple(old.keys())
        _cur_keys = tuple(cur.keys())

        rem = {k:None for k,v in old.items() if not (k in _cur_keys)}
        add = {k:v for k,v in cur.items() if not (k in _old_keys)}
        # set(_old_keys) & set(_cur_keys)
        changed = {k:cur.get(k) for k in (set(_old_keys) & set(_cur_keys)) }
        # changed = {k:v for k,v in cur.items() if (not (v is old.get(k, None)))}

        for k,v in {**rem, **add, **changed}.items():
            self.element_changed(k, v)
        return add, rem, changed

    def callback(self, attribute:str, c:Callable)->None:
        ''' Shortcut to filtered signal '''
        def func(source:Context, attr:str, val:Any):
            if attr != attribute:
                return
            return c(attr, val)
            
        return self.element_changed.connect(func, prepend_source=True)

class _Wrapper[T:Any]():
    def __init__(self, col, key, item, ):
        self._w_dict = self.__dict__
        self._w_replace(item)

    _w_obj : T = None
    _w_dict: Any = None
    _w_filled : Signal[T] = None

    def _w_replace(self, item:Any|None):
        self._w_obj = item
        if item is None:
            self.__class__ = _Wrapper
            self.__dict__ = self._w_dict
            return
        self.__class__ = type(item.__class__.__name__, (_Wrapper, item.__class__), {})
        self.__dict__ = item.__dict__
        self._w_filled(item)

_nullref = _wref(_UNSET())

class CollectionKey[K:str|int]():
    _key : K|None = None
    _col : ReferenceType[Collection]|None = _nullref
    _src : Any

    key_changed : Signal[K|None]
    col_changed : Signal[Collection|None]

    def __setup__(self):
        self.key_changed = Signal(self)
        self.col_changed = Signal(self)

    def __init__(self, src, key:K|None):
        self.__setup__()
        self._src = src
        self.key = key

    @property
    def key(self):
        return self._key
    @key.setter
    def key(self,val):
        if not (self.col is None):
            self.col.rename(self._src, val)
            self.key_changed(self._key)
            return
        self._key = val
        self.key_changed(val)

    @property
    def col(self)->Collection|None:
        ''' Reactionary property, collections will fullfill this when the object is appended to them'''
        return self._col()
    @col.setter
    def col(self, col:Collection|None):
        if (not (self.col() is None)) and (not (col is None)):
            ##Avoiding implicit behavior. Dont want to just swap structure bc I accidently didnt copy an object.
            raise Exception("Collection already set with this key!")
        if col is None:
            self._col = _nullref
            self.col_changed(col)
            return
        self.col = _wref(col)
        self.col_changed(col)

class Collection[K:str|int,T:Any](UserDict):
    context : None|Context = None
    context_filter : None|Callable = None

    data : dict[K,_Wrapper[T]]
    _inverse : dict[_Wrapper[T], K]

    appended : Signal[K,_Wrapper[T]]
    removed : Signal[K,_Wrapper[T]]
    swapped : Signal[K,_Wrapper[T],_Wrapper[T]]
    renamed : Signal[K,K,_Wrapper[T]]

    def __setup__(self, context:bool):
        self._inverse = {}

        self.appended = Signal(self)
        self.removed = Signal(self)
        self.swapped = Signal(self)
        self.renamed = Signal(self)
        
        if context:
            self.context = Context(self)

    def __init__(self, key_attr:str, context:None|Context=None, context_apply_filter:None|Callable=None):
        self.__setup__(not (context is None))
        self._key_attr = key_attr
        if context:
            self.context_filter = context_apply_filter
            self.context.set_extends(context)
            self.apply_context = True

    def _add_context(self, item):
        if (self.context is None) or (not hasattr(item, "context")): return
        if not self.context_filter(item): return
        item.context.set_extends(self.context)

    def _rem_context(self, item):
        if (self.context is None) or (not hasattr(item, "context")): return
        if item.context._extends is self.context:
            item.context.set_extends(None)

    def _set_key_collection(self, item):
        getattr(item,self._key_attr).col = self

    def _rem_key_collection(self, item):
        getattr(item,self._key_attr).col = None

    def find[D:Any](self, target:K|T|_Wrapper[T], default:D=_UNSET)->T|_Wrapper[T]|K: 
        if isinstance(target, (str,int)):
            res = self.data.get(target, _UNSET)
        elif isinstance(target,_Wrapper):
            res = self._inverse.get(target, _UNSET)
        else:
            res = _UNSET
            for v in self.data.values():
                if v._w_obj is target:
                    res = target
                    break

        if (res is _UNSET):
            if default is _UNSET:
                raise KeyError()
            return default
        return res

    def _resolve_find(self, item:K|T|_Wrapper[T])->tuple[K,_Wrapper[T]]|tuple[None,None]:
        ''' Internal Utility, resolving a generic to known (key,wrapped(item)) or (None,None)'''
        key = self.find(item, None)
        if (key is None):
            return None,None
        if isinstance(key,_Wrapper):
            item,key = key,item
        return key,item

    def append(self, item:T|_Wrapper[T], key:None|K=None, key_priority:bool=False, resolve_collisions:bool=True)->tuple[K,_Wrapper[T]]:
        if not(self.find(item) is None):
            raise Exception("cannot append one item multiple times!")

        if (key is None):
            key = getattr(item,self._key_attr).key
        if (key is None):
            key = self.generate_key()

        if not (existing := self.find(key)) is None:
            if existing._w_obj is None:
                #'Promise' fullfilment
                existing._w_replace(item)
                return
            if not resolve_collisions:
                raise KeyError()
            
            self.resolve_collision(key, existing, item, right_key_priority = key_priority)
            key = getattr(item,self._key_attr).key

        getattr(item,self._key_attr)._key = key
        self._set_key_collection(item)
        self._add_context(item)

        if not isinstance(item,_Wrapper):
            item = _Wrapper(item)

        self.data[key] = item
        self._inverse[item] = key

        self.appended(key,item)

        return key, item
        

    def remove(self, item:T|_Wrapper[T]|K, missing_is_ok:bool=False):
        key,item = self._resolve_find(item)

        if (key is None):
            if missing_is_ok: 
                return
            raise KeyError()

        del self.data[key]
        del self._inverse[item]

        self._rem_context(item)
        self._rem_key_collection(item)
        self.removed(key,item)

    def rename(self, target:K|T|_Wrapper[T], target_key:K, key_priority:bool=True, resolve_collision:bool=False): 
        c_key, c_item = self._resolve_find(target) 
        _, e_item = self._resolve_find(target_key)

        if c_key is None:
            raise Exception("item doesnt exist in collection yet!") 

        if not (e_item is None):
            # assert (e_key == target_key)
            if (e_item is c_item):
                return
            if not resolve_collision:
                raise KeyError()
            self.resolve_collision(target_key, e_item, c_item, key_priority) 
            return

        getattr(c_item, self._key_attr)._key = target_key

        del self.data[c_key]
        self._inverse[c_item] = target_key
        self.data[target_key] = c_item

        self.renamed(c_key, target_key, c_item)

    def generate_key(self, item:Any|None=None, old_key:str|None=None)->K: 
        return "".join(random.sample(ascii_letters, 9))

    def _generate_unique_key(self, *args,**kwargs):
        ks = tuple(self.data.keys())
        k = self.generate_key(*args, **kwargs)
        while k in ks:
            k = self.generate_key(*args,**kwargs)
        return k

    def resolve_collision(self, key:K, left:T|_Wrapper[T], right:T|_Wrapper[T], right_key_priority:bool)->tuple[K,K]: 
        l_k = getattr(left,self._key_attr)
        r_k = getattr(right,self._key_attr)

        if right_key_priority:
            l_k.key = self._generate_unique_key(item=left, old_key=key)
            ## Warning:: Will call back through rename to resolve!
        else:
            r_k.key = self._generate_unique_key(item=right, old_key=key)
            ## Warning:: Will call back through rename to resolve!

        assert l_k.key != r_k.key

    def valid(self,)->bool:
        for k,v in self.data.items():
            if v._w_obj is None:
                return False
        return True

class _Promise():
    replace : Signal[Any]
    def __setup__(self,):
        self.replace = Signal(self)

class _ConstructionPromise(_Promise):
    context : Context 
    _scope : str # "project"
    _scope_attr : str # "files"
    address : str|int

    def __setup__(self):
        super().__setup__()
        self.context = Context()
        self.context.element_changed.connect(self._on_context_fullfilled, once_only=True, weak=True, filter=lambda x,y: (x == self._scope) and (not (y is None)))

    def _on_context_fullfilled(self, scope):
        self.replace(getattr(scope, self._scope_attr).append_promise(self.address))

    def __init__(self, scope, scope_attr, address):
        self.__setup__()
        self._scope = scope
        self._scope_attr
        self.address = address

def FileRef(addr)->_ConstructionPromise:
    return _ConstructionPromise("project", "files", addr)

def Rid(addr):
    return _ConstructionPromise("project", "resources", addr)

def SubResource(addr):
    return _ConstructionPromise("project", "sub_resources", addr)
    
def ExtResource(addr):
    return _ConstructionPromise("resource", "ext_resources", addr)


class Properties[K:str, V:Any](UserDict):
    ''' Dict w/ the ability to overlay, replace promises, remove subresources as a reaction w/a, localize wrappers
    Wrappers are non-local when context doesnt match, and onyl applied to swap context scope w/a 
    '''
    overlay : None|Properties = None
    definitions : ... 

    context : None|Context = None
    context_filter : None|Callable = None

    data : dict[K,V]
    _inverse : dict[V, K]

    appended : Signal[K,V]
    removed : Signal[K,V]
    swapped : Signal[K,V,V]
    renamed : Signal[K,K,V]
    element_changed : Signal[K,V]

    def __setup__(self, context:bool):
        self.appended = Signal(self)
        self.removed = Signal(self)
        self.swapped = Signal(self)
        self.renamed = Signal(self)

        self.element_changed = Signal(self)
        ## Forward local changes:
        self.appended.connect(lambda k,v: self.element_changed(k,v))
        self.removed.connect(lambda k,v: self.element_changed(k,v))
        self.swapped.connect(lambda k,v0,v: self.element_changed(k,v))
        self.renamed.connect(lambda k0,k,v: self.element_changed(k,v))

        if context:
            self.context = Context(self)

    def __init__(self, key_attr:str, context:None|Context=None, context_apply_filter:None|Callable=None):
        self.__setup__(not (context is None))
        self._key_attr = key_attr
        if context:
            self.context_filter = context_apply_filter
            self.context.set_extends(context)
            self.apply_context = True

    def _add_context(self, item):
        if (self.context is None) or (not hasattr(item, "context")): return
        if not self.context_filter(item): return
        item.context.set_extends(self.context)

    def _rem_context(self, item):
        if (self.context is None) or (not hasattr(item, "context")): return
        if item.context._extends is self.context:
            item.context.set_extends(None)

    _replace_callbacks : list[LambdaType]

    def __setitem__(self, key, item):
        if not (self.definitions is None):
            if not (reason:=self.definitions.valid(key,item)):
                raise ValueError(reason)

        if not (self.data.get(key, _UNSET) is _UNSET):
            del self[key]

        if isinstance(item, _Promise) and (not isinstance(item, _Wrapper)):
            l = lambda x: self.__setitem__(key,x); self._replace_callbacks.remove(l)
            self._replace_callbacks.append(l)
            item.replace.connect(l, weak=True, once_only=True)
        if isinstance(item, Resource):
            raise NotImplementedError("Removal upon scope's object removal, ie Implicit cleanup")
            # l = lambda x: self.__delitem__(key); self._replace_callbacks.remove(l)
            ##FUCK! there has got to be a better way to do this.......
            ## Perhaps item.context.resource update?
            # self.context.resource.sub_resource.removed(filter=lambda k,v: v is item)
            

        res = super().__setitem__(key, item)
        self._add_context(item)

        return res

    def __getitem__(self, key):
        return self.get(key, include_overlays=True)

    def __delitem__(self, key):
        res = self[key]
        self._rem_context(res)
        super().__delitem__(key)

    def _as_local(self, item:_Wrapper)->V:
        if not isinstance(item, Resource):
            return item
        if not item.uid is None:
            return item
        if not (item.context.sub_resource is self.context.sub_resource):
            return self.context.resource.sub_resources.append_promise(item.id)
        return item

    def get[D](self, key:str, default:D=_UNSET, include_overlays:bool=True, include_defaults:bool=False, _ret_unset:bool=False)->Any|D:

        res = self.data.get(key, _UNSET)
        if not (res is _UNSET):
            return self._as_local(res)

        if include_overlays and self.overlay:
            res = self.overlay.get(key, _ret_unset=True, include_defaults=False)
            if not (res is _UNSET):
                return self._as_local(res)
            
        if include_defaults and not (self.definitions is None):
            res = self.definitions.defaults.get(key, _ret_unset=True)
            if not (res is _UNSET):
                return self._as_local(res)

        res = default
        if not (res is _UNSET):
            return self._as_local(res)
        
        if _ret_unset:
            return self._as_local(res)
        raise KeyError(key)

    def set_overlay(self, overlay:Collection|None, supress_changes:bool=False):
        old = dict(self.items(include_overlay=True))
        new = dict(self.items(include_overlay=False))
        if not(overlay is None):
            _new = dict(overlay.items())
            _new.update(new)
            new = _new

        if not (self._overlay is None):
            self._overlay.element_changed.disconnect(self.element_changed)
        self._overlay = overlay
        if not (self._overlay is None):
            self._overlay.element_changed.connect(self.element_changed)

        if supress_changes:
            return

        _old_keys = old.keys()
        _new_keys = new.keys()

        if not(self.definitions is None):
            rem = {k:self.definitions.defaults.get(k,default=None) for k,v in old.items() if k not in _new_keys}
        else:
            rem = {k:None for k,v in old.items() if k not in _new_keys}
        add = {k:v for k,v in new.items() if k not in _old_keys}
        changed = {k:v for k,v in new.items() if (not (v is old.get(k, None)))}

        for k,v in {**rem, **add, **changed}:
            self.element_changed(k, v)

    def _iter_overlays(self):
        if not (self._overlay is None):
            yield from self._overlay._iter_extends()
            yield self._overlay

    def items(self, include_overlay:bool=True, include_defaults:bool=False)->Generator[tuple[K,V]]:
        di = copy(self.data)

        for k,v in di.items():
            yield k,v

        if include_overlay:
            for p in reversed(tuple(self._iter_overlays())):
                for k,v in filter(lambda k,v:  not (k in di.keys()), p.data.items()):
                    di[k] = self._as_local(v)

        if include_defaults:
            for k,v in self.definitions.items():
                if not (k in di.keys()):
                    yield k, self._as_local(v)

    def values(self, include_overlay:bool=True, include_defaults:bool=False)->Generator[V]:
        for k,v in self.items(include_overlay=include_overlay, include_defaults=include_defaults):
            yield v

    def keys(self, include_overlay:bool=True, include_defaults:bool=False)->Generator[K]:
        for k,v in self.items(include_overlay=include_overlay, include_defaults=include_defaults):
            yield k

    def validate(self,)->list[Any]:
        ''' Return list of errors '''
        res = []
        for k,v in self.items(include_overlay=True):
            if not (self.definitions is None):
                if not (reason:=self.definitions.valid(k,v)):
                    res.append(ValueError(reason))
            if isinstance(v, _Wrapper):
                if v._w_obj is None:
                    res.append(ReferenceError(""))
        return res

    def _on_overlay_element_changed(self, k,v):
        if (k in self.data.keys()):
            if self.data.get(k,_UNSET) == v: ## Eqa value, get rid of (local object only stores dif)
                del self.data[k]
                # Direct, bypasses signals
        self.element_changed(k,v)

class FileSystemSignals():
    file_created : Signal[str]
    file_removed : Signal[str]
    file_updated : Signal[str]
    file_deleted : Signal[str]
    file_moved : Signal[str,str]

    def __setup__(self):
        self.file_created = Signal(self)
        self.file_removed = Signal(self)
        self.file_updated = Signal(self)
        self.file_deleted = Signal(self)
        self.file_moved = Signal(self)

    def __init__(self):
        self.__setup__()

class Project():
    context : Context
    files : Collection[str|File,File|str]
    resources : Collection[str|Resource,Resource|str]  

    fs : None|AbstractFileSystem
    fs_signals: None|FileSystemSignals

    file_created : Signal[str]
    file_removed : Signal[str]
    file_updated : Signal[str]
    file_deleted : Signal[str]
    file_moved : Signal[str,str]

    def __setup__(self):
        self.context = Context(project=self)
        self.files = Collection(self.context, child_key_attr="path",  child_type=File, set_child_context=True)
        self.resources = Collection(self.context, child_key_attr="uid",  child_type=None, set_child_context=True)

        self.file_created = Signal(self)
        self.file_removed = Signal(self)
        self.file_updated = Signal(self)
        self.file_deleted = Signal(self)
        self.file_moved = Signal(self)

    def __init__(self, fs:None|AbstractFileSystem, fs_signals:None|FileSystemSignals,):
        self.__setup__()
        self.fs = fs
        self.set_fs_signals(fs_signals)

    def set_fs_signals(self, fs_signals:None|FileSystemSignals):
        if not (self.fs_signals is None):
            self.fs_signals.file_created.disconnect(self.file_created)
            self.fs_signals.file_removed.disconnect(self.file_removed)
            self.fs_signals.file_updated.disconnect(self.file_updated)
            self.fs_signals.file_deleted.disconnect(self.file_deleted)
            self.fs_signals.file_moved.disconnect(self.file_moved)
        self.fs_signals = fs_signals
        if not (self.fs_signals is None):
            self.fs_signals.file_created.connect(self.file_created)
            self.fs_signals.file_removed.connect(self.file_removed)
            self.fs_signals.file_updated.connect(self.file_updated)
            self.fs_signals.file_deleted.connect(self.file_deleted)
            self.fs_signals.file_moved.connect(self.file_moved)

class Resource(_Promise):
    replace : Signal[_Wrapper[Resource]]

class File():
    ...
#     context : Context
#     path : CollectionKey[str]
#     resource : ResourceRef
    
#     last_updated : int = -0

#     _project : None|Project = None

#     def get_disc_uid()->str|None:...

#     def load():... ## load from disc, apply to project, and dif integration as req
#     def _load()->Resource:...
#     def _generate_dif():...
#     def _integrate_dif():...

#     def dump():... ## create or update as required
#     def _dump()->str|bytes:...

#     def create():...
#     def remove():...
#     def update():...
#     def delete():...
#     def move(self, new_path:str):
#         ...

#     def on_fs_created(self, _:str):...
#     def on_fs_removed(self, _:str):...
#     def on_fs_updated(self, _:str):...
#     def on_fs_deleted(self, _:str):...
#     def on_fs_moved(self, new_path:str):
#         if self.path.key != new_path:
#             self.path.set(new_path)

#     def __setup__(self,):
#         self.context = Context(file=self)
#         self.path = CollectionKey(self)
#         self.resource = ResourceRef(context=self.context)

#         def _on_project_set(self, project:None|Project):
#             if not (self._project is None):
#                 self.project.file_created.disconnect(self.on_file_created)
#                 self.project.file_removed.disconnect(self.on_file_removed)
#                 self.project.file_updated.disconnect(self.on_file_updated)
#                 self.project.file_deleted.disconnect(self.on_file_deleted)
#                 self.project.file_moved.disconnect(self.on_file_moved)
#             self._project = project
#             if not (self._project is None):
#                 self.project.file_created.connect(self.on_file_created, filter=lambda x: x==self.path.key)
#                 self.project.file_removed.connect(self.on_file_removed, filter=lambda x: x==self.path.key)
#                 self.project.file_updated.connect(self.on_file_updated, filter=lambda x: x==self.path.key)
#                 self.project.file_deleted.connect(self.on_file_deleted, filter=lambda x: x==self.path.key)
#                 self.project.file_moved.connect(self.on_file_moved, filter=lambda o,n: o==self.path.key)
#         self.context.callback("project", _on_project_set)

#     @classmethod
#     def __collection_new__(cls, filepath:str)->File:
#         ...

# class ExtResource[F:File,R:Resource]():
#     context : Context

#     file_ref : FileRef[str,F]
#     resource_ref : ResourceRef[str,R]
#     id : CollectionKey[str]

#     match_found : Signal[R]

#     def __setup__(self,):
#         self.context = Context(ext_resource = self)
#         self.id = CollectionKey(self)
#         self.file_ref = FileRef(context=self.context)
#         self.resource_ref = ResourceRef(context=self.context)
#         self.match_found = Signal(self)

#         self.file_ref.match_found.connect(self.match_found)
#         self.resource_ref.match_found.connect(self.match_found)

#         self.context.callback("resource", self._on_resource_set)

#     def __init__(self, file:str, resource:str, id:None|str=None):
#         self.__setup__()

#     def _on_resource_set(self, resource:None|Resource):
#         if self._resource() is resource: 
#             return
        
#         if not (self._resource() is None):
#             self._resource.ext_resources.remove(self)

#         if not (resource is None):
#             self.context.set_extends(resource.context)
#             resource.ext_resources.append(self)
#             self._resource = _wref(resource)
            
#         elif not (self._resource() is None):
#             self._resource = _wref(object())


#     def get(self, load_as_required:bool=True)->R|None:
#         r = self.resource_ref.get(default=None)

#         if not (r is None):
#              return r
#         if not load_as_required:
#             return None
        
#         f = self.file_ref.get(default=None)
#         if (f is None):
#             return None
#         f.load()
#         return f.resource.get()
        
#     @classmethod
#     def __collection_new__(cls, path:str, uid:str, id:str)->ExtResource:
#         ...


# class SignalDef():
#     ...

# class PropertyDef():
#     ...

# class ResourceDef():
#     extends : None|ResourceDef = None
#     properties : dict[str,PropertyDef]
#     signals : dict[str,SignalDef]

# class Resource():
#     context : Context

#     ## File Resource:
#     is_file_resource : bool = False
#     file : None|FileRef = None
#     uid : None|CollectionKey[str] = None
#     sub_resources : None|Collection[str,Resource] = None
#     ext_resources : None|Collection[str,ExtResource] = None

#     ## Base Resource:
#     id : CollectionKey[str]
#     properties : Properties

#     ## File Instance:
#     instance : None|ExtResourceRef
#     overlay : None|Resource
#     def is_shallow()->bool:... #return if this overlay-instance has any changes compared to overlay's source

#     def set_instance(self, file : None|File|ExtResourceRef):...
#     def set_overlay(self, resource : Resource):...

#     def setup_resource_state():... ## Setup FileRef, ect
#     def break_resource_state():... ## Breakdown Filesetate, ect. Requires context for where it's being inserted into.

#     def convert_to_resource():... ## Convert an object into a resource with it's own file. Optionally return an instance
#     def copy_to_subresource():... ## Embedd a copy of this resource into a sub-resource.

#     def _iter_dependencies():...

#     def duplicate(self, regen_id:bool=True, deep:bool=False, file_depth:int=1, filename_solver:None|LambdaType=None, memo:None|dict=None)->Resource: ... ## Duplicate, copying deep or shallow. Re-generates ID, keeps in parent-resource collection
#     def collapse(self, deep:bool=False, file_depth:int=1, memo:None|dict=None)->Resource:...
#     def sublimate(self, deep:bool=False)->Resource:... ## Copy-clear internal data and set_overlay to Source, return Source. Used for moving subresource to instance.

#     # def clone(self, context:Context, deep:bool=True)->Resource:... ## FUTURE: runtime resource object for emulating behavior?

#     def __setup__(self):
#         self.context = Context(sub_resource = self)

#         self.id = CollectionKey(self)
#         self.properties = Properties(context=self.context)
#         self.instance = ExtResourceRef(context=self.context)
        
#         self.context.callback("project", self._on_project_set_as_file, filter= lambda: getattr(self, "is_file_resource"))
#         self.context.callback("resource", self._on_resource_set, filter=lambda: not getattr(self, "is_file_resource"))

#     _resource : ReferenceType[Resource]
#     _project : ReferenceType[Project]

#     def _on_resource_set(self, resource:None|Resource):
#         if self._resource() is resource: 
#             return
        
#         if not (self._resource() is None):
#             self._resource.sub_resources.remove(self)

#         if not (resource is None):
#             self.context.set_extends(resource.context)
#             resource.sub_resources.append(self)
#             self._resource = _wref(resource)
            
#         elif not (self._resource() is None):
#             self._resource = _wref(object())


#     def _on_project_set_as_file(self, project:None|Project):
#         if self._project() is project: 
#             return
        
#         if not (self._project() is None):
#             self._project.resources.remove(self)

#         if not (project is None):
#             self.context.set_extends(project.context)
#             project.resources.append(self)
#             self._project = _wref(project)
            
#         elif not (self._project() is None):
#             self._project = _wref(object())

#     @classmethod
#     def __collection_new__(cls, subtype:str)->Resource:
#         ...

# class GodotSignal():
#     signal : str
#     fr : Node
#     to : Node
#     method : str
#     unbind : None|int
#     flags : None|list[int]
#     binds : None|list[Any]

# class Node(Resource):
#     node_context : Context 

#     ## As a file:
#     nodes : None|Collection[int,Node] = None
#     signals : None|list[GodotSignal] = None

#     ## as all:
#     name : CollectionKey[str]
#     overlay : None|Node = None
#     children : Collection[str,Node]

#     @classmethod
#     def __collection_new__(cls, subtype:str)->Node:
#         ...

#     def _on_resource_set(self, resource:None|Node):
#         assert isinstance(resource, Node)

#         if self._resource() is resource: 
#             return
        
#         if not (self._resource() is None):
#             self._resource.nodes.remove(self)

#         if not (resource is None):
#             self.context.set_extends(resource.context)
#             resource.nodes.append(self)
#             self._resource = _wref(resource)
            
#         elif not (self._resource() is None):
#             self._resource = _wref(object())

#     ## Alternations to accomidate tree - children:

#     def _iter_dependencies():...

#     def duplicate(self, regen_id:bool=True, deep:bool=False, file_depth:int=1, filename_solver:None|LambdaType=None, memo:None|dict=None)->Resource: ... ## Duplicate, copying deep or shallow. Re-generates ID, keeps in parent-resource collection
#     def collapse(self, deep:bool=False, file_depth:int=1, memo:None|dict=None)->Resource:...
#     def sublimate(self, deep:bool=False)->Resource:... ## Copy-clear internal data and set_overlay to Source, return Source. Used for moving subresource to instance.

#     def setup_resource_state():... ## Alter for nodes & signals
#     def break_resource_state():... ## Alter for nodes & signals

#     # def clone(self, context:Context, deep:bool=True)->Resource:... ## FUTURE: runtime resource object for emulating behavior?
