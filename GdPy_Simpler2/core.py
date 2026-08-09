from __future__ import annotations
from typing import Any, Callable, Iterable
from types import LambdaType
from weakref import ReferenceType, ref as _wref
from copy import copy
from inspect import getmembers
from collections import UserDict


import random
from string import ascii_letters, digits

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

    def __contains__(self, obj:int|Callable|_SignalSubscriber):
        if obj is None:
            raise ValueError()
        if isinstance(obj,int):
            return obj in self.subscribers.keys()
        if isinstance(obj, _SignalSubscriber):
            return obj in self.subscribers.values()
        for k,v in self.subscribers.items():
            if v.callback() is obj:
                return True
        return False
        
    def disconnect(self, c:Callable, /, not_exist_ok:bool=False)->None:
        to_remove = []
        found = False
        for k,v in self.subscribers.items():
            if (v.callback() is c) or (hash(c) == hash(v.callback())):
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
    _slots_ : tuple[str] = tuple()
    _default = None
    element_changed : Signal
    default_null = ContextVar("", default=None)
    # verify_structure : Signal[dict] 
    
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
        raise AttributeError(self._slots_,attr, obj=self, name=attr)
        
    def __setattr__(self,attr,value):
        # self.verify_structure({attr:value})
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
    ''' Structural Proxy, for replacing objects in a collection in runtime w/out 
    good article to read fully later:
    https://www.pythontutorials.net/blog/how-to-fake-proxy-a-class-in-python/#ensuring-isinstance-compatibility
    '''
    _proxy_obj : None|T = None
    _proxy_orig_dict : dict

    _proxy_obj_changed : Signal[None|T]

    def __init__(self, obj:Any|None=None):
        self._proxy_obj_changed = Signal(self)
        self._proxy_orig_dict = copy(self.__dict__)
        if not (obj is None):
            self._proxy_set_obj(obj)

    def __getattribute__(self, name:str):
        if name.startswith("_proxy_") or (name == "__class__"):
            return super().__getattribute__(name)
        p = self._proxy_obj
        if not (p is None):
            return getattr(p,name)
        return super().__getattribute__(name)


    # def __getattr__(self, name):
    #     if self._proxy_obj:
    #         return getattr(self._proxy_obj, name)
    #     return super().__getattr__(name)

    # def __setattr__(self, name, value):
    #     if self._proxy_obj:
    #         return setattr(self._proxy_obj, name, value)
    #     return super().__setattr__(name, value)
    
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
            if (attr not in exclude) and attr.startswith("__"):
                setattr(self, attr, make_proxy_func(self._proxy_obj, attr))

        self.__class__ = type("PROXY_"+obj.__class__.__name__, (Proxy, obj.__class__), {})

        self._proxy_obj_changed(obj)

    def __repr__(self):
        return f"Proxy(<{self._proxy_obj}>)"

class _C_Proxy(Proxy):
    __name__ = "Proxy"
    _proxy_owner : Collection
    _proxy_key_updated : Signal
    _proxy_key_attr : str

    def __init__(self, owner:Any|None, key_attr:str, obj = None):
        self._proxy_key_attr = key_attr
        self._proxy_owner = owner
        self._proxy_key_updated = Signal(self) 
        super().__init__(obj)

    def _proxy_set_obj(self, obj):
        if not (obj is None):
            getattr(obj, self._proxy_key_attr).key_updated.connect(self._proxy_key_updated)
        if not (self._proxy_obj is None):
            getattr(obj, self._proxy_key_attr).key_updated.connect(self._proxy_key_updated)
        return super()._proxy_set_obj(obj)

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

class Collection[K:str|int, V:object](UserDict):
    ''' dict-wrapper that replaces items with proxies to those items 
    - Keys must be primitives (not objects)
    - Items store & declare keys through CollectionKeys under a specific attr
    - In cases where two _C_Proxy s are "merged" the secondary item becomes a wrapper of the first and is removed from the collection.
    - _C_Proxys have an owner attr to prevent duplicates and circular references
    '''

    data : dict[K, _C_Proxy[V]]
    _key_attr : str
    _random_key : bool = True

    appended : Signal[K, _C_Proxy[V]]
    removed : Signal[K, _C_Proxy[V]]
    renamed : Signal[K, K, _C_Proxy[V]]
    merged : Signal[K,K,_C_Proxy]

    def __init__(self, key_attr:str, items:Iterable=tuple()):
        self.appended = Signal(self)
        self.removed = Signal(self)
        self.renamed = Signal(self)
        self.merged = Signal(self)
        self._key_attr = key_attr
        super().__init__( items)

    def _connect(self, item:_C_Proxy):
        item._proxy_key_updated.connect(self.rename, weak=True, prepend_source=True)

    def _disconnect(self, item:_C_Proxy):
        # assert len(item._proxy_key_updated.subscribers) == 1
        # raise Exception(tuple(item._proxy_key_updated.subscribers.values())[0].callback())
        item._proxy_key_updated.disconnect(self.rename)

    def rename(self, item:V|_C_Proxy[V]|K, new_key:K, r_key_priority:bool=True):
        ''' Rename, merge if target namespace is a promise. '''
        c_k,c_v = self.resolve_pair(item, (None,None))
        n_k,n_v = self.resolve_pair(new_key, (None, None))

        if c_v is None:
            raise KeyError()

        if not (n_v is None):
            if not (n_v._proxy_obj is None):
                self.handle_key_collision(new_key, n_v, item, r_key_priority)
                return
            else:
                n_v._proxy_set_obj(c_v)
                getattr(item, self._key_attr)._key = new_key 
                return

        if not (c_k is None):
            del self.data[c_k]

        self.data[new_key] = item

        ckey = getattr(item, self._key_attr)
        if ckey.key != new_key:
            ckey.key = new_key 

        self.renamed(c_k, new_key, item)

    def append_promise(self, key:K)->_C_Proxy[None|V]:
        assert isinstance(key, (str,int))
        if not ((res:=self.data.get(key,None)) is None):
            return res
        return self.append(None, key=key)

    def append(self, item:V|_C_Proxy[V], nested_ok:bool=False, key:None|K=None, r_key_priority:bool=True):

        if item in self:
            raise ValueError("Item Already exists in collection!", item)

        if key is None:
            key = getattr(item, self._key_attr).key

        if key is None:
            key = self.generate_key(item)

        if not ((obj:=self.data.get(key,None)) is None) and (obj._proxy_obj is None):
            if isinstance(item,_C_Proxy):
                if item._proxy_owner is self:
                    obj._proxy_set_obj(item._proxy_obj)
                elif not nested_ok:
                    obj._proxy_set_obj(item._proxy_obj)
                elif nested_ok:
                    obj._proxy_set_obj(item)
            else:
                obj._proxy_set_obj(item)
            self.appended(key, obj)
            return obj
        
        if isinstance(item,_C_Proxy):
            if item._proxy_owner is self:
                item = item
            elif not nested_ok:
                item = _C_Proxy(self, self._key_attr, item._proxy_obj)
            elif nested_ok:
                item = _C_Proxy(self, self._key_attr, item)
        else:
            item = _C_Proxy(self, self._key_attr, item)

        if not ((obj:=self.data.get(key,None)) is None):
            self.resolve_key_collision(key,obj,item,r_key_priority)
            key = getattr(item, self._key_attr).key

        assert not (key is None)

        self._connect(item)
        self.data[key] = item

        if not (item._proxy_obj is None):
            self.appended(key, item)

        return item

    def __contains__(self, key:K|V|_C_Proxy[V]):
        if isinstance(key, (str,int)):
            return (key in self.data.keys())
        for v in self.data.values():
            if (key is v) or (key is v._proxy_obj):
                return True
        return False

    def _generate_key(self, obj:V|_C_Proxy[V])->str:
        return "".join(random.sample(ascii_letters,9))
    
    def generate_key(self,obj:V|_C_Proxy[V])->str:
        keys = tuple(self.keys())
        n_key = self._generate_key(obj)
        while n_key in keys:
            n_key = self._generate_key(obj)
        return n_key
    
    def index_key(self, key:str):
        keys = tuple(self.keys())
        n_key = key.rstrip(digits)
        i = 1
        while n_key in keys:
            n_key = f"{key}{i}"
            i = i+1
        return n_key

    def resolve_key_collision(self, key:str, l_item:V|_C_Proxy[V], r_item:V|_C_Proxy[V], r_key_priority:bool=True):
        
        if not r_key_priority:
            if self._random_key:
                n_key = self.generate_key(r_item)
            else: 
                n_key = self.index_key(key)
            getattr(r_item,self._key_attr).key = n_key
        else: 
            if self._random_key:
                n_key = self.generate_key(l_item)
            else: 
                n_key = self.index_key(key)
            getattr(l_item,self._key_attr).key = n_key
        

    def __getitem__(self, key:K|V|_C_Proxy[V])->V|_C_Proxy[V]|K:
        if key is None:
            raise KeyError(key)
        if isinstance(key, (str,int)):
            return self.data[key]
        for k,v in self.data.items():
            if (v is key) or (v._proxy_obj is v):
                return k
        raise KeyError(key)
        
    def remove(self, key:K|V|_C_Proxy[V]):
        k,v = self.resolve_pair(key)
        if k is None:
            raise KeyError(key)
        self._disconnect(v)
        del self.data[k]
        self.removed(k,v)

    def resolve_pair[D:Any](self, key:K|V|_C_Proxy[V], default:D=(None,None))->tuple[K,_C_Proxy[V]]|D:
        if not isinstance(key, (str,int)):
            value = key
            key = self.get(key, None)
            if key is None:
                return default
        else:
            value = self.get(key, None)
            if value is None:
                return default
        return key,value

    def __delitem__(self, key):
        return self.remove(key)

        

# class Collection[K:str|int,V:object](UserDict):
#     ''' Dict wrapper that holds proxies of children objects.  
#     Objects set keys in collection 
#     '''

#     data : dict[K, _C_Proxy[V]]
#     _key_attr : str
#     _random_key : bool
#     _allow_nested_proxies : bool

#     def __init__(self, iterable, key_attr:str, allow_nested_proxies:bool=False, random_key:bool=True ):
#         self._random_key = random_key
#         self._key_attr = key_attr
#         self._allow_nested_proxies = allow_nested_proxies
#         super().__init__(iterable)

#     def get_pair[D:Any](self, value:V|_C_Proxy[V]|K, default:D)->tuple[K,V]|D:
#         ''' Get pair if present locally, with local _C_Proxy wrapper '''
#         if isinstance(value, object):
#             item = value
#             key = self.get_key(value, None)
#             if key is None:
#                 return default
#             if (not isinstance(item, _C_Proxy)):
#                 return key, self[key]
#             elif (not (item._proxy_owner is self)):
#                 return key, self[key]
#             return key, item
        
#         key = item
#         item = self.get(key, None)
#         if item is None:
#             return default
#         return key, item

#     def get_key[D:Any](self, item:V|_C_Proxy[V], default:D)->K|D:
#         if isinstance(_C_Proxy):
#             if item._proxy_owner is self:
#                 return (item in self.values())
#             match = (item, item._proxy_obj)
#         else:
#             match = (item,)

#         for k,v in self.items():
#             v:_C_Proxy[V]
#             if (v in match):
#                 return k
#             elif (v._proxy_obj in match):
#                 return k

#         return default
        
#     def _connect(self, item:_C_Proxy):
#         item._proxy_key_updated.connect(self.rename, weak=True, prepend_source=True)

#     def append(self, item:V|_C_Proxy[V], r_key_priority:bool=True, exist_ok:bool=True)->_C_Proxy[V]:
#         if kv := self.get_pair(item,None):
#             if not exist_ok:
#                 raise ValueError()
#             return kv[1]
            
#         ckey = getattr(item,self._key_attr)
#         if ckey.key is None:
#             ckey.key = self.generate_key(item)
#         if ckey.key in self.keys():
#             self.resolve_key_collision(key, self[key], item, r_key_priority)
#         key = ckey.key

#         if isinstance(item, _C_Proxy):
#             if (item._proxy_owner is self):
#                 r = item
#                 self._connect(r)
#                 self.data[key] = r
#                 return r
#             elif (self._allow_nested_proxies):
#                 r = _C_Proxy(self, self._key_attr, item)
#                 self._connect(r)
#                 self.data[key] = r 
#                 return r
#             else:
#                 r = _C_Proxy(self, self._key_attr, item._proxy_obj)
#                 self._connect(r)
#                 self.data[key] = r 
#                 return r
            
#         r = _C_Proxy(self, self._key_attr, item)
#         self._connect(r)
#         self.data[key] = r 
#         return r

#     def _disconnect(self, item:_C_Proxy):
#         item._proxy_key_updated.disconnect(self.rename,not_exist_ok=True)

#     def remove(self, item:V|_C_Proxy[V]|K, remove_empty_proxy:bool, not_exist_ok:bool=False): 
#         key,val = self.get_pair(item)

#         if key is None:
#             if not_exist_ok:
#                 return
#             raise KeyError(item)

#         if (val._proxy_obj is None): 
#             if (remove_empty_proxy):
#                 self._disconnect(val)
#                 del self.data[key]
#                 return
#             raise KeyError(key)

#         self._disconnect(val)
#         del self.data[key]
#         return
        
#     def promise(self, key:K)->_C_Proxy[None]:
#         if res:=self.data.get(key):
#             return res
#         res = _C_Proxy(self, self._key_attr, None)
#         self[key] = res
#         return res
        
#     def promises_missing(self)->dict[K,_C_Proxy[None]]:
#         res = {}
#         for k,v in self.data.items():
#             if v._proxy_obj is None:
#                 res[k] = v
#         return res

#     def replace(self, key:K, new_item:V|_C_Proxy[V]):
#         assert not (new_item in self)
#         if not (key in self):
#             self[key] = new_item

#         if isinstance(new_item, _C_Proxy) and (new_item._proxy_owner is self):
#             new_item = new_item._proxy_obj
#         elif isinstance(new_item, _C_Proxy) and self._allow_nested_proxies:
#             pass
#         else:
#             new_item = new_item._proxy_obj

#         self[key]._proxy_obj = new_item

#     def rename(self, item:V|_C_Proxy[V], new_key:str):
#         k,v = self.get_pair(item)
#         if v is None:
#             raise KeyError(item)
#         del self.data[k]
#         self.data[new_key] = v

#     def merge(self, key_a:K, key_b:K):
#         raise NotImplementedError()
#         # ''' effectivly 'Merge' keys by setting (obj_b._proxy_obj = obj_a), and forwarding the update signal and deleting key_b '''
#         ## perhaps instead use replace signal, since most proxy users will be Properties objects 
        
#     # def generate_key(self, obj:V|_C_Proxy[V])->K:
#     #     return "".join(random.sample(ascii))
        
#     # def resolve_key_collision(self, key:K, l_obj:V|_C_Proxy[V], r_obj:V|_C_Proxy[V]):pass


#     def _generate_key(self,)->str:
#         return "".join(random.sample(ascii_letters,9))
    
#     def generate_key(self)->str:
#         keys = tuple(self.keys())
#         n_key = self._generate_key()
#         while n_key in keys:
#             n_key = self._generate_key()
#         return n_key
    
#     def index_key(self, key:str):
#         keys = tuple(self.keys())
#         n_key = key.rstrip(digits)
#         i = 1
#         while n_key in keys:
#             n_key = f"{key}{i}"
#             i = i+1
#         return n_key

#     def resolve_key_collision(self, key:str, l_item:V|_C_Proxy[V], r_item:V|_C_Proxy[V], r_key_priority:bool=True):
        
#         if self._random_key:
#             n_key = self.generate_key()
#         else: 
#             n_key = self.index_key(key)
        
#         if not r_key_priority:
#             getattr(r_item,self.key_attr).key = n_key
#         else: 
#             getattr(l_item,self.key_attr).key = n_key


#     def __setitem__(self, key:K, item:V|_C_Proxy[V]):
#         ## Fullfill proxy if empty, replace proxy contents if present
#         ckey = getattr(item, self._key_attr)
#         if ckey != key:
#             ckey.key = key
#         self.append(item)

#     def __delitem__(self, val:K|V):
#         k,v = self.get_pair(val)
#         self.remove(v)

#     def __getitem__(self, key:K)->V: #actually ->_C_Proxy[V]
#         return self.super().__getitem__(key)

#     def __contains__(self, item:V|_C_Proxy[V]|K)->bool:
#         ''' Return false if item/key is an empty Proxy (a promise) '''
#         if isinstance(item, object):
#             for k,v in self.items():
#                 if (v is item) or (v is item._proxy_obj):
#                     return True
#         for k,v in self.items():
#             if (k == item) and not (v._proxy_obj is None):
#                 return True
#         return False
