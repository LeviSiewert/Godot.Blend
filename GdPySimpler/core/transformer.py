from __future__ import annotations
from contextvars import ContextVar
from typing import Any, Iterable, Generator, Callable
from inspect import isclass, isgeneratorfunction, isgenerator
from copy import deepcopy

class _UNSET():
    pass

class TERMINAL():
    pass

class DEFAULT():
    ''' Catch all transformer module'''

class IGNORE():
    pass

class _TransformerCmd():
    def __init__():
        pass

    def result(self, tranform_func:Callable)->Generator[Generator|tuple]|tuple[Any]:
        pass
    

class TSet(_TransformerCmd):
    ''' Children are expanded and grouped together in results, can stream. Can Cache. Nestable Tstream-like '''
    data : tuple[TSet|Any]
    res_structure : tuple[Any]

    def __init__(self, *args, stream=False):
        self.stream = stream
        self.data = args

    def result(self,)->Generator[Generator|tuple] | tuple[Any]:
        raise NotImplementedError()
    
    
class TStream[I:Any,O:Any](_TransformerCmd):
    ''' Tranform is only called when iterated over, .cache keeps results on this object '''
    source : Iterable[I] 
    result : tuple[O]
    caching : bool = False
    completed : bool = False

    def __init__(self, source:Iterable[I], /, caching=False):
        self.source = source
        self.caching = caching
    
    def iter(self, tranform_func:Callable)->Generator[O]:
        if self.completed and self.caching:
            yield from self.result
            return

        if self.caching:
            self.result = []

        for node in self.source:
            val = tranform_func(node)
            if self.caching:
                self.result.append(val)
            yield val
        
        self.completed = True


class Context():
    def __new__(cls):
        self = super().__new__(cls)
        self.transformer = ContextVar("transformer", default=None)
        self.rulesets = ContextVar("rulesets", default=None)

        self.key = ContextVar("key", default=None)
        self.ruleset = ContextVar("ruleset", default=None)
        self.module = ContextVar("module", default=None)

        self.children = ContextVar("children", default=None)
        return self

    transformer : ContextVar
    rulesets : ContextVar
    
    ruleset : ContextVar
    module : ContextVar

    children : ContextVar[Iterable[Any]]

    def __deepcopy__(self,):
        ##TODO: Double check IO
        res = self.__class__()
        for k,v in self.__dict__():
            if isinstance(v, ContextVar):
                getattr(res,k).set(v.get())
        return res

class TransformerModule[IN:Any, CHILDREN:Any|TERMINAL, OUT:Any|IGNORE]():
    def __repr__(self,):
        return f"Module({self.__class__.__name__})"
    
    _keys = tuple()
    def get_keys(self,)->tuple[Any]:
        return self._keys
    
    def transform(self, c:Context, node:IN)->Generator[CHILDREN,OUT]:
        yield TERMINAL
        return IGNORE

class TransformerRuleset():
    modules : dict[Any, TransformerModule]
    
    def __init__(self, identifier, modules:Iterable[TransformerModule]):
        self.identifier = identifier
        self.modules = {}

        for m in modules:
            if isclass(m):
                m = m()
            keys = m.get_keys()
            mod_keys = self.modules.keys()
            for k in keys:
                if k in mod_keys:
                    raise KeyError(f"Key {k} already exists!", m, self, self.modules[k])
                self.modules[k] = m

    def __repr__(self,):
        return f"Ruleset({self.identifier})"

    def _extract_keys(self, node:Any)->tuple[Any]:
        if node is None:
            return (None,)
        if isclass(node):
            return (node, node.__name__) 
        return (node.__class__, node.__class__.__name__)

    def _match_module(self, keys:tuple[Any], default=_UNSET)->None|TransformerModule:
        # raise Exception(keys, (*self.modules.keys(),))
        for k in keys:
            if res:=self.modules.get(k,None):
                return res, k
        if res:=self.modules.get(DEFAULT,None):
            return res, DEFAULT
        if default is _UNSET:
            raise KeyError(self, keys)
        return default, DEFAULT
    
    def get(self, key:Any, default:Any=_UNSET):
        keys = self._extract_keys(key)
        return self._match_module(keys, default)


class Transformer():
    rulesets : tuple[TransformerRuleset]
    def __init__(self, *args:tuple[TransformerRuleset], identifier:str ):
        self.rulesets = args
        self.identifier = identifier

    def __repr__(self)->str:
        return f"{self.__class__.__name__}({self.identifier} :: {self.rulesets})"
        
    def transform_tree(self, c:Context, node:Any)->None:
        if c.rulesets.get() is None:
            c.rulesets.set(self.rulesets)
        return self._transform_tree(c, node)
        
    def _transform_tree(self, c:Context, node:Any)->None:
        t = c.transformer.set(self)

        mod = None
        for r in c.rulesets.get():
            mod,key = r.get(node, None)
            if mod:
                t0 = c.module.set(mod)
                t1 = c.ruleset.set(r)
                t3 = c.transformer.set(self)
                t4 = c.key.set(key)
                break
        if (mod is None):
            raise KeyError(self, node)

        transform_func = mod.transform

        if not isgeneratorfunction(transform_func):
            def _func(c:Context, node:Any,*args,**kwargs):
                ## TODO: Consider default get-children functions asc w/ local?
                yield TERMINAL
                return mod.transform(c,node,*args,**kwargs)
            transform_func = _func

        escape_result = ContextVar("escape_result")
        def caller():
            _res = yield from transform_func(c,node)
            escape_result.set(_res)

        t5 = c.children.set(TERMINAL)
        
        _t = None
        for child_set in caller():
            
            if _t:
                c.children.reset(_t)
                _t = None
            
            if child_set is TERMINAL:
                _t = c.children.set(TERMINAL)

            elif child_set is IGNORE:
                _t = c.children.set(IGNORE)
                        
            elif isgenerator(child_set):
                # _c = deepcopy(c)
                def _call_transform(val):
                    return c.transformer.get().transform_tree(c,val)
                _t = c.children.set(TStream(child_set, caching=True).iter(_call_transform))

            elif isinstance(child_set, _TransformerCmd):
                # _c = deepcopy(c)
                def _call_transform(val):
                    return c.transformer.get().transform_tree(c,val)
                _t = c.children.set(child_set.iter(_call_transform))
            
            elif isinstance(child_set, dict):
                res = {}
                for k,v in child_set.items():
                    res[k] = c.transformer.get().transform_tree(c,v)
                _t = c.children.set(res)

            elif hasattr(child_set, "__iter__"):
                res = []
                for v in child_set:
                    res.append(c.transformer.get().transform_tree(c,v))
                _t = c.children.set(res)

            else:
                raise Exception(f" Yielded children cannot be interpretted! ", child_set.__class__, child_set)
            
            ## Code runs until next yield / func completion
            ## res should now be populated

        c.children.reset(t5)
        c.key.reset(t4)
        c.transformer.reset(t3)
        c.ruleset.reset(t1)
        c.module.reset(t0)
        c.transformer.reset(t)

        return escape_result.get() 
