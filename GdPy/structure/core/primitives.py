from __future__ import annotations
from typing import Self, Callable, Any, Iterable
from inspect import get_annotations
from abc import ABC, abstractmethod
from contextvars import ContextVar
from contextlib import contextmanager

class SignalSubscriber():
    func : Callable
    pre_args : list

    def __init__(self,func, *pre_args):
        self.func = func
        self.pre_args = pre_args
        
    def __call__(self,*args,**kwargs):
        return self.func(*self.pre_args, *args, **kwargs)

class Signal():
    class REMOVE: pass
    subscribers : list[SignalSubscriber]
    owner : Any

    def __init__(self,owner):
        self.owner = owner
        self.subscribers = []

    def __call__(self, *args, **kwds):
        to_rem = []
        for x in self.subscribers:
            res = x(*args, **kwds)
            if res is self.REMOVE:
                to_rem.append(res)
        for x in to_rem:
            self.subscribers.remove(res)
    
    def forward(self, *args, **kwargs):
        self(self.owner, *args, **kwargs)

    def connect(self, func, include_owner=False):
        if include_owner:
            self.subscribers.append(SignalSubscriber(func))
        else:
            self.subscribers.append(SignalSubscriber(func, self.owner))

    def disconnect(self, func):
        to_rem = []
        for x in self.subscribers:
            if x.func == func:
                to_rem.append(x)
        for x in to_rem:
            self.subscribers.remove(x)
        
class SignalContainer: 
    def __init__(self):
        classes_limited = []
        for x in self.__class__.__mro__:
            if x is SignalContainer:
                break
            classes_limited.append(x)
        for clss in classes_limited:
            for k,v in get_annotations(clss).items():
                if not isinstance(v,str):
                    continue
                if v.startswith("Signal"):
                    setattr(self,k,Signal(self))

        super().__init__()


class Collection[T](ABC, SignalContainer):
    items : list[T]
    item_appended : Signal
    item_removed : Signal
    
    def __init__(self):
        items = []
        self.item_appended = Signal(self) 
        self.item_removed = Signal(self)
        super().__init__()
    
    def append(self, item:T):
        self._integrate(item)
        self.item_appended(item)

    def remove(self, item:T):
        self._disintegrate(item)
        self.item_removed(item)
    
    def extend(self, iterable):
        for x in iterable:
            self.append(x)

    @abstractmethod
    def _integrate(item:T):
        pass
    
    @abstractmethod
    def _disintegrate(item:T):
        pass

    @abstractmethod
    def __getitem__(self, key)->T:
        return None
    
    def get(self, key, default=None):
        res = self[key]
        if res is None:
            return default
        return res
    
    def values(self,):
        return self.items.__iter__()
    
class Context():
    project      : ContextVar[Any]
    load_session : ContextVar[Any]
    file_db      : ContextVar[Any]
    file         : ContextVar[Any]
    resource     : ContextVar[Any]
    subresource  : ContextVar[Any]

    def __init__(self,):
        self.project = ContextVar(str(id(self))+"_project")
        self.load_session = ContextVar(str(id(self))+"_load_session")
        self.file = ContextVar(str(id(self))+"_file")
        self.resource = ContextVar(str(id(self))+"_resource")
        self.subresource = ContextVar(str(id(self))+"_subresource")
        self.file_db = ContextVar(str(id(self))+"_file_db")
    
    @contextmanager
    def w(self, key:str,val:Any):
        if var := getattr(self,key):
            token=var.set(val)
            yield
            var.reset(token)


# buffer : ContextVar[dict[str,ContextVar[list]]]
buffer : dict[str, ContextVar[list]] = {}
class CacheTreeNode():
    obj : Any
    trailing : dict[str, list]
    layer_keys : tuple[str]
    layer_children : dict[str,list]
    
    def __init__(self, obj, layer_keys:tuple[str]):
        self.obj = obj
        self.layer_keys = layer_keys
        self.layer_children = {}

    @contextmanager
    def traverse(self, is_root:bool=False):
        if is_root: 
            buffer = {}
        tokens = self.enter()
        yield
        self.exit(tokens)
        if is_root:
            self.claim_buffer()
    
    def claim_buffer(self,):
        self.trailing = {}
        for k,v in buffer.items():
            value = v.get()
            if not isinstance(value,list):
                continue
            self.trailing[k] = value
        buffer.clear()

    def enter(self,)->dict[str,str]:
        tokens = {}
        for k in self.layer_keys:
            if not (k in buffer):
                buffer[k] = ContextVar(k+str(id(self)))
                buffer[k].set([]) ## Left in buffer as w/out claimant, claimed by root in claim_buffer
            buffer[k].get().append(self)
        for k in self.layer_keys:
            tokens[k] = buffer[k].set([]) #my Children
        return tokens
    
    def exit(self, tokens:dict[str,str]):
        for k in self.layer_keys:
            lst = buffer[k].get()
            self.layer_children[k] = lst #Attach my children
            buffer[k].reset(tokens[k])   #pass back up towards siblings.

    def __eq__(self, value)->bool:
        if (value is self) or (self.obj == value):
            return True
        if isinstance(value, CacheTreeNode):
            return value.obj == self.obj
        return False
    
    def call(self, layer:str, func_name:str, context:Context, *args, **kwargs):
        ctx_key = getattr(self.obj, "context_key", None)
        if ctx_key:
            with context.w(ctx_key,self.obj):
                self._call(layer,func_name,context,*args,**kwargs)
        else:
            self._call(layer,func_name,context,*args,**kwargs)

    def _call(self, layer:str, func_name:str, context:Context, *args, **kwargs):
        func = getattr(self.obj, func_name, None)
        if not (func is None):
            func(context, *args, **kwargs)
        for x in self.layer_children.get(layer, tuple()):
            x.call(layer, func_name, context, *args, **kwargs)


class MultiKeyCollection[PK:str, SK:Any, T:Any](SignalContainer):
    item_appended : Signal[T]
    item_removed : Signal[T]
    # key_changed : Signal[T,PK,SK]

    _keys : tuple[PK] = tuple()
    ## Keys that return a tuple of items matching
    _unique_keys : tuple[PK] = tuple()
    ## Keys that require a single return per key
    _required_keys : tuple[PK] = tuple()
    ## Keys that are generated and assigned if missing
    _ignore_no_key = False
    ## Ignore if a specific key cannot be generated
    _get_default_key : PK = None

    _items : list[T]
    _shared_dicts : dict[PK,dict[SK, list[T]]]
    _unique_dicts : dict[PK,dict[SK, T]]
    _cache : dict[T,tuple[PK,SK]]

    def __init__(self):
        self._items = []
        self._shared_dicts = {}
        self._unique_dicts = {}
        self._cache = {}
        for k in self._unique_keys:
            self._unique_dicts[k] = {}
        for k in self._keys:
            self._shared_dicts[k] = []
        super().__init__()

    def append(self,item:T):
        keys = self._key_extractor(item)
        self._append_item(item,keys)
        self.item_appended(item)

    def extend(self,items:Iterable[T]):
        for x in items:
            self.append(x)

    def remove(self,item:T):
        self._remove_item(item)
        self.item_removed(item)

    def _key_extractor(self, item:T)->dict:
        res = {}
        for k in (*self._keys, *self._unique_keys):
            s_key = getattr(item, k, None)
            if (s_key is None):
                s_key = self._generate_missing_secondary_key(k,item)
                self._assign_unique_key(k, s_key, item)
            if (s_key is None) and (self._ignore_no_key):
                continue
            elif s_key is None:
                raise KeyError(f"Could not extract or generate key;{item}.{k}",)
            res[k] = s_key
        return res
    
    def _append_item(self, item:T, keys:dict)->None:
        self._items.append(item)
        self._cache[item] = []
        for pk, sk in keys.items():
            if pk in self._keys:
                self._append_item_shared(pk,sk,item)
            elif pk in self._unique_keys:
                self._append_item_unique(pk,sk,item)
            else:
                raise KeyError("Primary key not defined:", pk)
            self._cache[item].append((pk,sk))

    def _remove_item(self, item:T)->None:
        self._items.remove(item)
        for pk, sk in self._cache[item]:
            if pk in self._keys:
                self._remove_item_shared(pk,sk,item)
            elif pk in self._unique_keys:
                self._remove_item_unique(pk,sk,item)
            else:
                raise KeyError("Primary key not defined:", pk)
        del self._cache[item]
            
    def _append_item_unique(self, p_key:PK, s_key:SK, item:T)->None:
        pd = self._unique_dicts[p_key]
        if s_key in pd.keys():
            s_key = self._generate_unique_key(pd,p_key,s_key,item)
            self._assign_unique_key(pd,s_key,item)
        pd[s_key] = item

    def _remove_item_unique(self, p_key:PK, s_key:SK, item:T)->None:
        pd = self._unique_dicts[p_key]
        assert(pd[s_key] is item)
        del pd[s_key]

    def _append_item_shared(self, p_key:PK, s_key:SK, item:T)->None:
        pd = self._unique_dicts[p_key]
        pd[s_key].append(item)

    def _remove_item_shared(self, p_key:PK, s_key:SK, item:T)->None:
        pd = self._unique_dicts[p_key]
        pd[s_key].remove(item)

    def _generate_missing_secondary_key(self, p_key:PK, item:T)->SK:
        return None

    def _generate_unique_key(self, di:dict, p_key:PK, s_key:SK, item:T)->SK:
        raise NotImplementedError("Undefined behavior! Override Class to fullfill as req")

    def _assign_unique_key(self, p_key:PK, s_key:SK, item:T)->None:
        raise NotImplementedError("Undefined behavior! Override Class to fullfill as req")

    def get(self, pk, sk, default:Any=None)->T|list[T]:
        if pk in self._keys:
            pd = self._shared_dicts.get(pk, None)
            if pd is None: return default
            return pd.get(sk,default)
        elif pk in self._unique_keys:
            pd = self._unique_dicts.get(pk, None)
            if pd is None: return default
            return pd.get(sk,default)
        else:
            raise KeyError()
        
    def get_itemkeys(self, item:T)->dict[tuple[PK,SK]]:
        return self._cache[item]
        
    def _key_matcher(self, key)->tuple[PK,SK]|None:
        """ Iterface to determine PK, SK by input key, if key not tuple & not matching primary keys """
        if self._get_default_key:
            return (self._get_default_key, key)
        # raise KeyError("Could not match key to (primary, secondary) key pair!")

    def __getitem__(self, key:tuple[PK,SK]|SK|PK):
        if (key in self._keys):
            return self._shared_dicts[key]
        if (key in self._unique_keys):
            return self._unique_dicts[key]
        
        if isinstance(key, tuple):
            pk,sk = key
        else:
            keys = self._key_matcher(key)
            if keys is None:
                raise KeyError("Could not match key to (primary, secondary) key pair!")
            pk,sk = keys
                
        if (pk in self._keys):
            return self._shared_dicts[pk][sk]        
        if (pk in self._unique_keys):
            return self._unique_dicts[pk][sk]
        
        raise KeyError("(Primary,Secondary) key set not found", pk, sk)
        