from __future__ import annotations
from typing import Any, Callable
from types import LambdaType
from weakref import ReferenceType, ref as _wref
from copy import copy
from inspect import getmembers
from collections import UserDict

class _UNSET():...

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
    ''' Context object, attribute fallback through extends chain. Values set/changed along chain propigate to children. (including removed as None) 
    sub to self.verify_structure w/ any behavior that is disallowed.
    '''
    _extends : Context = None
    _slots_ : tuple[str]
    _default = None
    element_changed : Signal
    default_null = ContextVar("", default=None)
    verify_structure : Signal[dict] 
    
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
        self.verify_structure({attr:value})
        super().__setattr__(attr, value)
        if attr in self._slots_:
            self.element_changed(attr,value)

    def __setitem__(self, key, value):
        self.__setattr__(key,value)
    def __getitem__(self, key):
        return self.__getattr__(key)
    def __delitem__(self, key):
        self.__delattr__(key)

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

def make_proxy_func(_proxy_obj, attr):
    def func (*args,**kwargs): 
        return getattr(_proxy_obj, attr)(*args, **kwargs)
    return func

class Proxy[T:Any]():
    ''' Structural Proxy, for replacing objects in a collection in runtime w/out '''
    _proxy_obj : None|T = None
    _proxy_orig_dict : dict

    _proxy_obj_changed : Signal[None|T]

    def __init__(self, obj:Any|None=None):
        self._proxy_obj_changed = Signal(self)
        self._proxy_orig_dict = copy(self.__dict__)
        if not (obj is None):
            self._proxy_set_obj(obj)

    def __getattr__(self, name):
        if self._proxy_obj:
            return getattr(self._proxy_obj, name)
        raise AttributeError()
    
    def _proxy_set_obj(self, obj:None|T):
        if self._proxy_obj is obj:
            return

        if not (self._proxy_obj is None):
            self.__dict__ = copy(self._proxy_orig_dict) #Reset object state
            self.__class__ = Proxy

        if obj is None:
            self._proxy_obj = obj
            self._proxy_obj_changed(obj)
            return
        
        self._proxy_obj = obj

        exclude = list(set(dir(self)))
        exclude.append("__class__")
        for attr, _ in getmembers(obj, callable):
            if attr not in exclude:
                setattr(self, attr, make_proxy_func(self._proxy_obj, attr))

        self.__class__ = type("PROXY_"+obj.__class__.__name__, (Proxy, obj.__class__), {})

        self._proxy_obj_changed(obj)

class _C_Proxy(Proxy):
    __name__ = "Proxy"
    _proxy_owner : Collection
    def __init__(self, owner:Any|None=None, obj = None):
        self._proxy_owner = owner
        super().__init__(obj)

class CollectionKey():
    value : None|str = None


class Collection[K:str|int,V:object](UserDict):
    ''' Dict wrapper that holds proxies of children objects.  
    Objects set keys in collection 
    '''

    data : dict[K, _C_Proxy[V]]
    _key_attr : str

    def get_pair[D:Any](self, value:V|_C_Proxy[V]|K, default:D)->tuple[K,V]|D:...
    def get_key[D:Any](self, item:V, default:D)->K|D:...

    def append(self, item:V, r_key_priority:bool=True):...
    def remove(self, item:V):...

    def promise(self, key:K):...
    def promises_missing(self)->tuple[K]:...

    def replace(self, key:K, new_item:V|_C_Proxy[V]):...
    def merge(self, key_a:K, key_b:K):...
        # ''' effectivly 'Merge' keys by setting (obj_b._proxy_obj = obj_a), and forwarding the update signal and deleting key_b '''
        ## perhaps instead use replace signal, since most proxy users will be Properties objects 
        

    def resolve_key_collision(self, key:K, l_obj:V|_C_Proxy[V], r_obj:V|_C_Proxy[V]):pass

    def __setitem__(self, key:K, item:V|_C_Proxy[V]):...
    def __delitem__(self, key:K):...
    def __getitem__(self, key:K)->V:... #->_C_Proxy[V]

    def __contains__(self, item:V|_C_Proxy[V]):...

