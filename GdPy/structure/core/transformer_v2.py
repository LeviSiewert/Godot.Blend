from __future__ import annotations
from typing import Any, Iterable, Generator, Callable, Type
from contextvars import ContextVar, Token
from inspect import isgeneratorfunction, isclass

class TERMINAL: pass
class IGNORE: pass
class DEFAULT: pass

class TransformerContext():
    def __init__(self, transformer:Transformer, rulesets:Iterable[TransformerRuleset]=None):
        self.transformer = ContextVar(str(id(self))+"transformer", default = transformer)
        if rulesets is None:
            self.current_rulesets = ContextVar(str(id(self))+"current_rulesets", default = transformer.rulesets)
        else:
            self.current_rulesets = ContextVar(str(id(self))+"current_rulesets", default = tuple(rulesets))
        self.ruleset = ContextVar(str(id(self))+"ruleset")
        self.key = ContextVar(str(id(self))+"key")
        self.chain = ContextVar(str(id(self))+"chain", default = tuple())
        self.children = ContextVar(str(id(self))+"children", default=tuple())
        self.children_map = ContextVar(str(id(self))+"children_map")
        self.node = ContextVar(str(id(self))+"node")
        self.existing_object = ContextVar(str(id(self))+"existing_object")

    node: ContextVar[Any]
    ## Current node that is being transformed!

    existing_object: ContextVar[Any]
    ## Object that may or may not already exist and needs to be altered, passed from the parent

    transformer : ContextVar[Transformer]
    ## Current transformer

    current_rulesets : ContextVar[tuple[TransformerRuleset]]
    ## Current rulsets the transformer evaluates in order
    ## This should never be a mutable iterable for transformation safety

    ruleset : ContextVar[TransformerRuleset]                    
    ## Currently utilized ruleset

    key : ContextVar[str|Any]
    ## Key used to determine current transformer
    
    chain : ContextVar[tuple[Any]]
    ## Chain of parents of original type

    children : ContextVar[tuple[Any]|Any]
    ## Converted Children, side-variable via context. Set via _transform_children

    children_map : ContextVar[dict[Any,Any]|Any]
    ## Converted Children mapped from prev->post, side-variable via context. Set via _transform_children
    
class Transformer():
    ''' A ModularTransformer Header class, where rulesets are in inverse priority. IE last is evaluted first
    It should be noted that once called with a specific context, the original rulsets are ignored.
    '''

    rulesets : list[TransformerRuleset] 
    ## "Seed" rulesets, runtime uses c.rulesets for evalutation (as subsets of trees may need different rules)
    ## These are in inverse priority. First to catch a key is returned. If none return a KeyError is raised

    def __init__(self, rulesets:Iterable[TransformerRuleset]=tuple()):
        self.rulesets = []
        self.rulesets.extend(rulesets)

    def make_context(self)->TransformerContext:
        c = TransformerContext(self, self.rulesets)
        return c 
    
    def transform_tree(self, c:TransformerContext|None, node,  *args, **kwargs)->IGNORE|None:
        if c is None:
            c = self.make_context()
        
        ruleset, module, key = self.matcher(c, node)
        
        t0 = c.ruleset.set(ruleset)
        t1 = c.key.set(key)
        
        res = module.transform_tree(c,node, *args, **kwargs)
        
        c.key.reset(t1)
        c.ruleset.reset(t0)
        
        return res
    
    def matcher(self, c:TransformerContext, node)->tuple[TransformerRuleset, TransformerModule, str|Any|Type]:
        if c is None:
            c = self.make_context()
        rulsets = c.current_rulesets.get(self.rulesets)
        for r in reversed(rulsets):
            res = r.matcher(node)
            if res:
                return (r,*res)
        raise KeyError("Could not determine match node within current ruleset!", node, c.current_rulesets.get())

class TransformerRuleset():
    ''' This class contains transformer modules, and should be treated as immutable for transformation safety
    if behavior desires a same index ruleset change, replace in context.
    '''
    identifier : str
    modules : tuple[TransformerModule]
    data : dict[str|Any|Type,TransformerModule]

    def __init__(self, identifier:str, modules:Iterable[TransformerModule], _reverse=True, _key_safety=True):
        ''' 
        _key_safety asserts that each key in a ruleset is unique, default is true
        _reverse inverts the order of the module, when true and key_safety is off, "key-priority" is effectivly first in modules
        '''

        self.identifier = identifier
        self.modules = tuple(modules)
        if _reverse:
            self.modules = reversed(self.modules)

        self.data = {}

        for m in self.modules:
            if isclass(m):
                m = m()
            for k in m.get_keys():
                if _key_safety and (k in self.data.keys()):
                    raise KeyError("k already registered in ruleset", self, k, m, self.data[k])
                self.data[k] = m

    def matcher(self, key:str|Any|Type)->None|tuple[TransformerModule,str|Any|Type]:
        ''' Return TransformerModule and key.
        if DEFAULT is present, always return matched item
        to customize key extraction, override _key_extractor
        '''
        
        for k in self._key_extractor(key):
            if res:=self.data.get(k,None):
                return (res,k)

        if res:=self.data.get(DEFAULT,None):
            # raise VisitorException("res", key)
            return (res, DEFAULT)
        return None
    
    def _key_extractor(self,key)->tuple[str|Any|Type]:
        return (key,key.__class__)

    def __iter__(self):
        return self.data.__iter__()
    
    def __repr__(self):
        return f"<{self.__class__.__name__} :: {self.identifier}>"

class VisitorException(Exception):
    pass

class TransformerModule():
    _transform_depth_first : bool = True

    def get_keys(self)->tuple[str|Any|DEFAULT]:
        ''' Returns keys for the matcher, only called once on addition to a Ruleset. Malbehavior can occur if dependencies & behavior are not uniform '''
        return tuple()
    
    def _get_children_default(self, node:Any)->None|TERMINAL|Iterable:
        return TERMINAL

    def _transform_children_default(self, c:TransformerContext, node, iterable:Iterable, args, kwargs)->dict[str:Token]|None:
        ''' Port of _transform_children for handling Type[iterable] reasons '''
        return self._transform_children(c,node,iterable,args,kwargs)

    def _transform_children_yielded(self, c:TransformerContext, node, iterable:Iterable, args, kwargs)->dict[str:Token]|None:
        ''' Port of _transform_children for handling Type[iterable] reasons '''
        return self._transform_children(c,node,iterable,args,kwargs)
    
    def _transform_children(self,c:TransformerContext, node, iterable:Iterable, args, kwargs):
        ''' Call and populate children from _transform yielded children
        -> SIDE EFFECTS: c.children_map, c.children
        -> RETURN: None OR {key:Token} to reset after parent is transformed. 
        '''
        transformer : Transformer = c.transformer.get()

        children_map = {}
        children = []
        
        for child in iterable:
            res = transformer.transform_tree(c, child, *args, **kwargs)
            if res is IGNORE:
                continue
            children_map[child] = res
            children.append(res)

        return {
            "children" : c.children.set(children),
            "children_map" : c.children_map.set(children_map),
        }        
            
    def transform_tree(self, c:TransformerContext, node:Any, *args, **kwargs)->IGNORE|Any:
        # TODO: Determine if I can just make it so that the entire grouping of contextvars is reset after calling children 

        kt : dict[str,Token] = {
            "node" : c.node.set(node),
            "chain" : c.chain.set((*c.chain.get(tuple()), node)),
            "children" : c.children.set(None),
            "children_map" : c.children_map.set(None),
        }
        _kt : dict[str,Token]|None = None


        func : Generator|Callable = self.transform
        if not isgeneratorfunction(self.transform): ## Ensuring uniform interface
            if self._transform_depth_first:
                def func(node, c, *args, **kwargs):
                    yield self._get_children_default(node)
                    return self.transform(node, c, *args, **kwargs)
            else:
                def func(node, c, *args, **kwargs):
                    res = self.transform(node, c, *args, **kwargs)
                    yield self._get_children_default(node)
                    return res

        # children : None|TERMINAL|Iterable = next(generator) 
        
        generator = func(node, c, *args, **kwargs)
        cv = ContextVar("result")
        def generator_closure(gen:Generator):
            ## `yield from` forwards iterator results, and returns the res value locally
            res = yield from gen
            cv.set(res)

        for children in generator_closure(generator):
            if _kt:
                for k,t in _kt.items():
                    getattr(c,k).reset(t)
                _kt = None

            if (children is None):
                children = self._get_children_default(node)
                if not ((children is None) or (children is TERMINAL)):
                    _kt = self._transform_children_default(c, node, children, args, kwargs) #-> SIDE EFFECT: context.?
                    
            elif isinstance(children,dict):
                _kt = self._transform_children_yielded(c, node, children.values(), args, kwargs)  #-> SIDE EFFECT: context.?
                _m = c.children_map()
                new = {}
                for k,v in children.items():
                    new[k] == _m[v] 
                c.children.set(new)

            elif (children is TERMINAL):
                c.children.set(TERMINAL)
                c.children_map.set(TERMINAL)
            
            else:
                _kt = self._transform_children_yielded(c, node, children, args, kwargs)  #-> SIDE EFFECT: context.?


        if _kt:
            ## NOTE: Have to offset context reset due to `return` happening *after* last yield completes
            for k,t in _kt.items():
                getattr(c,k).reset(t)
            _kt = None


        res : IGNORE|Any = cv.get()

        for k,t in kt.items():
            getattr(c,k).reset(t)

        return res

    def transform(self, node, c:TransformerContext, *args, **kwargs):
        ''' Transform this node
        If Generator:
            - Yield children first to transform them or TERMINAL|None to not set any children
            - transformed children are then set in c.children and c.children_map
                - set by function (_transform_children_default | _transform_children_yielded | _transform_children)
            - Multiple yields are allowed, c.children will be changed for each
            - return after to return the transformed value
            - before first yield, timing is eq to root first
            - directly before final return, timing is eq to depth first
        If Not Generator:
            - default timing is eq to depth first, all children should be transformed.
            - Root first timing;
                - set inherited flag (class._transform_depth_first = False)
                - Usefull when children attach themselves to the parent, or are otherwise distributed. 
                - in this case, c.children and c.children_map will *always* be None
        '''
        yield TERMINAL #None|TERMINAL|Iterable[MyChildren]
        return IGNORE