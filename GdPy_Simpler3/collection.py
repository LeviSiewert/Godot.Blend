from collections import UserDict
from .signal import Signal
from .context import Context

from typing import Any, Self
from weakref import ReferenceType


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
    ''' Dict like that proposes context, allows overlays, and DynamicPromises reference these '''
    context : Context
    _key_attr : str|None = None

    overlay : None|Self = None
    overlay_updated : Signal
    _overlay_memo : dict[K,T] #Objects created from the overlay, but may or may not be saved/converted to local later


    appended : Signal[K,V]
    removed : Signal[K,V]
    renamed : Signal[K,K,V]
    updated : Signal[K,V]

    def __setup__(self):
        self.context = Context()

        self.overlay_updated = Signal(self)

        self.appended = Signal(self)
        self.removed = Signal(self)
        self.renamed = Signal(self)
        self.updated = Signal(self)

    def __init__(self, iterable, /, context:None|Context=None, context_self_as:None|str=None):
        self.__setup__()
        self.context.set_extends(context)
        if not (context_self_as is None):
            self.context.__setattr__(context_self_as, self)
        super().__init__(iterable)

    def set_overlay(self, overlay:None|Self=None, supress_signals:bool=False):
        o_items = dict(self.items())
        if not (self.overlay is None):
            self._disconnect_overlay(self.overlay)
            self._overlay_disintegrate_all(supress_signals=supress_signals)

        self.overlay = overlay

        if not (self.overlay is None):
            self._connect_overlay(self.overlay)
            self._overlay_integrate_all(supress_signals=supress_signals)

        if supress_signals:
            return
        
        self.overlay_updated()
        
        n_items = dict(self.items())

        added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
        removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
        changed = {k:v for k,v in n_items.items() if (not (n_items.get(k,None) is o_items.get(k,None)))}

        for k,v in added.items():
            self._on_overlay_key_appended(k,v)

        for k,v in removed.items():
            self._on_overlay_key_removed(k,v)

        for k,v in changed.items():
            self._on_overlay_key_updated(k,v)

    def _overlay_integrate_all(self, supress_signals:bool=False):
        for k in {*self.overlay.keys(), *self.data.keys()}:
            self._overlay_integrate_item(k, self.overlay.get(k, None), self.data.get(k,None))
        
    def _overlay_disintegrate_all(self, supress_signals:bool=False):
        for k in {*self.overlay.keys(), *self.data.keys()}:
            self._overlay_disintegrate_item(k, self.overlay.get(k, None), self.data.get(k,None))

    def _overlay_integrate_item(self, key:bool, o_item:V|None, l_item:V|None)->V:
        ''' When overlay is set, this is called for every item in both collections matched by K '''
        raise NotImplementedError() 

    def _overlay_disintegrate_item(self, key:bool, o_item:V|None, l_item:V|None)->V:
        ''' when overlay is rem, this is called for every itme in both collections matched by K '''
        raise NotImplementedError() 

    def _connect_overlay(self, overlay:Self):
        self.overlay.appended.connect(self._on_overlay_key_appended, weak=True)
        self.overlay.removed.connect(self._on_overlay_key_removed, weak=True)
        self.overlay.renamed.connect(self._on_overlay_key_renamed, weak=True)
        self.overlay.updated.connect(self._on_overlay_key_updated, weak=True)

    def _disconnect_overlay(self, overlay:Self):
        self.overlay.appended.disconnect(self._on_overlay_key_appended)
        self.overlay.removed.disconnect(self._on_overlay_key_removed)
        self.overlay.renamed.disconnect(self._on_overlay_key_renamed)
        self.overlay.updated.disconnect(self._on_overlay_key_updated)

    def _on_overlay_key_append(self, k:K, v:V): ...
    def _on_overlay_key_remove(self, k:K, v:V): ...
    def _on_overlay_key_rename(self, k0:K, k:K, v:V): ...
    def _on_overlay_key_updated(self, k:K, v0:V|None, v:V): ...

    def embed_overlay(self,):... ## embbedd all values to localize all

    def append(self, item:V, r_key_priority:bool=True):...

    def extend(self, iterable, r_key_priority:bool=True):...


    def get(self, key, resolve_promises:bool=True):...


    def set(self, key, item):...

    def rename(self, item:V, key:K, r_key_priority:bool=True): ...


    def remove(self, item:V|K):...


    def _generate_key(self, obj:None|V=None)->K:...

    def generate_key(self, obj:None|V=None)->K:...

    def resolve_key_collision(self, key:K, l_item:V, r_item:V, r_key_priority:bool=True)->tuple[K,K]:...


    def _connect(self, obj:V):
        ''' Called whenever an object is added to this collection '''

        if ckey := getattr(obj, self._key_attr):
            ckey : CollectionKey
            ckey.key_updated.connect(self.rename, prepend_source=True, weak=True)

        if func:=getattr(obj,"_reference_callback",None):
            func(self, self.context)

    def _disconnect(self, obj:V):
        ''' Called whenever an object is removed from this collection '''

        if ckey := getattr(obj, self._key_attr):
            ckey : CollectionKey
            ckey.key_updated.disconnect(self.rename)

        if hasattr(obj,"_dereference_callback"):
            obj._dereference_callback(self, self.context)


    def _find_key(self, item:V)->None|K: 
        if ckey:=getattr(item, self._key_attr, None):
            return ckey.key        
        for k,v in self.data.items():
            if v is item:
                return k
        return None

    def _set_key(self,  key:K, item:V, r_key_priority:bool=True):
        current_key = self._find_key(item)

        if ckey:=getattr(item, self._key_attr, None):
            ckey._key = key

        current_item = self.data.get(key, None)
        assert (current_item is None)

        if not (current_key is None):
            del self.data[current_key]
            self.data[key] = item
            self.renamed(current_key, key, item)
            return

        self.data[key] = item
        self._connect(item)
        self.appended(key, item)


    def __setitem__(self, key:K, item:V):
        if item in self:
            self.rename(item, key, replace=True)
        else:
            self.set(key, item)

    def __getitem__(self, key:K):
        self.get(key, include_overlays=True)

    def __delitem__(self, key:K):
        return self.remove(key)

    def __contains__(self, key):
        if isinstance(key, (str,int)):
            return key in self.data.keys()
        return (key in self.data.values())


# class Collection[K:str|int, V:object](UserDict):
#     ''' dict-wrapper that replaces items with proxies to those items 
#     - Keys must be primitives (not objects)
#     - Items store & declare keys through CollectionKeys under a specific attr
#     - In cases where two _C_Proxy s are "merged" the secondary item becomes a wrapper of the first and is removed from the collection.
#     - _C_Proxys have an owner attr to prevent duplicates and circular references
#     '''

#     data : dict[K, _C_Proxy[V]]
#     _key_attr : str
#     _random_key : bool = True

#     appended : Signal[K, _C_Proxy[V]]
#     removed : Signal[K, _C_Proxy[V]]
#     renamed : Signal[K, K, _C_Proxy[V]]
#     merged : Signal[K,K,_C_Proxy]

#     def __init__(self, key_attr:str, items:Iterable=tuple()):
#         self.appended = Signal(self)
#         self.removed = Signal(self)
#         self.renamed = Signal(self)
#         self.merged = Signal(self)
#         self._key_attr = key_attr
#         super().__init__( items)

#     def _connect(self, item:_C_Proxy):
#         item._proxy_key_updated.connect(self.rename, weak=True, prepend_source=True)

#     def _disconnect(self, item:_C_Proxy):
#         # assert len(item._proxy_key_updated.subscribers) == 1
#         # raise Exception(tuple(item._proxy_key_updated.subscribers.values())[0].callback())
#         item._proxy_key_updated.disconnect(self.rename)

#     def rename(self, item:V|_C_Proxy[V]|K, new_key:K, r_key_priority:bool=True):
#         c_key, item = self.resolve_pair(item, (None,None))
#         e_key, e_item = self.resolve_pair(new_key, (None,None))


#         if item is None:
#             raise ValueError("Item not in collection!")
#         if c_key == new_key:
#             raise KeyError("Key is already fullfilled!", c_key, item)
#         if e_item is item:
#             raise KeyError("Key is already fullfilled!", c_key, item)

#         if not (e_item is None):
#             if e_item._proxy_obj is None:
#                 e_item._proxy_obj = item
#                 self.renamed(e_key, new_key, item)
#                 return
#             else:
#                 self.resolve_key_collision(new_key, e_item, item, r_key_priority=r_key_priority)
#                 ##TODO: Missing keyattr solution here!
#                 return

#         if not c_key is None:
#             del self.data[c_key]
#         self.data[new_key] = item

#         if ckey:=getattr(item, self._key_attr, None):
#             ckey._key = new_key
#         self.renamed(c_key, new_key, item)

#     def append_promise(self, key:K)->_C_Proxy[None|V]:
#         assert isinstance(key, (str,int))
#         if not ((res:=self.data.get(key,None)) is None):
#             return res
#         return self.append(None, key=key)

#     def append(self, item:V|_C_Proxy[V], nested_ok:bool=False, key:None|K=None, r_key_priority:bool=True, rename_ok:bool=False)->V|_C_Proxy[V]:

#         if (c:=(item in self)) and rename_ok:
#             self.rename(item, key)
#             return
#         elif c:
#             raise ValueError("Item Already exists in collection!", item)


#         if key is None:
#             ckey = getattr(item, self._key_attr, None)
#             if not (ckey is None):
#                 key = ckey.key

#         if key is None:
#             key = self.generate_key(item)

#         if not ((obj:=self.data.get(key,None)) is None) and (obj._proxy_obj is None):
#             if isinstance(item,_C_Proxy):
#                 if item._proxy_owner is self:
#                     obj._proxy_set_obj(item._proxy_obj)
#                 elif not nested_ok:
#                     obj._proxy_set_obj(item._proxy_obj)
#                 elif nested_ok:
#                     obj._proxy_set_obj(item)
#             else:
#                 obj._proxy_set_obj(item)
#             self.appended(key, obj)
#             return obj
        
#         if isinstance(item,_C_Proxy):
#             if item._proxy_owner is self:
#                 item = item
#             elif not nested_ok:
#                 item = _C_Proxy(self, self._key_attr, item._proxy_obj)
#             elif nested_ok:
#                 item = _C_Proxy(self, self._key_attr, item)
#         else:
#             item = _C_Proxy(self, self._key_attr, item)

#         if not ((obj:=self.data.get(key,None)) is None):
#             _,r_key = self.resolve_key_collision(key,obj,item,r_key_priority)
#             key = r_key

#         assert not (key is None)

#         self._connect(item)
#         self.data[key] = item

#         if not (item._proxy_obj is None):
#             self.appended(key, item)

#         return item

#     def __contains__(self, key:K|V|_C_Proxy[V]):
#         if isinstance(key, (str,int)):
#             return (key in self.data.keys())
#         for v in self.data.values():
#             if (key is v) or (key is v._proxy_obj):
#                 return True
#         return False

#     def _generate_key(self, obj:V|_C_Proxy[V])->str:
#         return "".join(random.sample(ascii_letters,9))
    
#     def generate_key(self,obj:V|_C_Proxy[V])->str:
#         keys = tuple(self.keys())
#         n_key = self._generate_key(obj)
#         while n_key in keys:
#             n_key = self._generate_key(obj)
#         return n_key
    
#     def index_key(self, key:str):
#         keys = tuple(self.keys())
#         n_key = key.rstrip(digits)
#         i = 1
#         while n_key in keys:
#             n_key = f"{key}{i}"
#             i = i+1
#         return n_key

#     def resolve_key_collision(self, key:str, l_item:V|_C_Proxy[V], r_item:V|_C_Proxy[V], r_key_priority:bool=True)->tuple[str,str]:
        
#         if not r_key_priority:
#             if self._random_key:
#                 n_key = self.generate_key(r_item)
#             else: 
#                 n_key = self.index_key(key)

#             if (ckey := getattr(r_item,self._key_attr,None)):
#                 ckey.key = n_key
#             else:
#                 self.rename(r_item, n_key)

#             return key, n_key

#         else: 
#             if self._random_key:
#                 n_key = self.generate_key(l_item)
#             else: 
#                 n_key = self.index_key(key)
#             if (ckey := getattr(l_item,self._key_attr,None)):
#                 ckey.key = n_key
#             else:
#                 self.rename(l_item, n_key)
#             return n_key, key
        

#     def __getitem__(self, key:K|V|_C_Proxy[V])->V|_C_Proxy[V]|K:
#         if key is None:
#             raise KeyError(key)
#         if isinstance(key, (str,int)):
#             return self.data[key]
#         for k,v in self.data.items():
#             if (v is key) or (v._proxy_obj is v):
#                 return k
#         raise KeyError(key)
        
#     def remove(self, key:K|V|_C_Proxy[V]):
#         k,v = self.resolve_pair(key)
#         if k is None:
#             raise KeyError(key)
#         self._disconnect(v)
#         del self.data[k]
#         self.removed(k,v)

#     def __setitem__(self, key, item):
#         self.append(item, key=key)

#     def resolve_pair[D:Any](self, key:K|V|_C_Proxy[V], default:D=(None,None))->tuple[K,_C_Proxy[V]]|D:
#         if not isinstance(key, (str,int)):
#             value = key
#             key = self.get(key, None)
#             if key is None:
#                 return default
#         else:
#             value = self.get(key, None)
#             if value is None:
#                 return default
#         return key,value

#     def __delitem__(self, key):
#         return self.remove(key)
    
#     def promises_missing(self)->dict[K,_C_Proxy[None]]:
#         res = {}
#         for k,v in self.data.items():
#             if v._proxy_obj is None:
#                 res[k] = v
#         return res