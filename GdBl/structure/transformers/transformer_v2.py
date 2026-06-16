from __future__ import annotations
from typing import Any, Iterable, Generator, Callable
from contextvars import ContextVar, Token
from inspect import isgeneratorfunction

class TERMINAL: pass
class IGNORE: pass

class TransformerContext():
    transformer : ContextVar
    ## Current transformer

    current_rulesets : ContextVar[tuple[TransformerRuleset]]
    ## Current rulsets the transformer evaluates in order

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
    def __init__():
        pass

    def transform_tree(self, node, c:TransformerContext|None, *args, **kwargs)->IGNORE|None:
        module, ruleset, key = self.matcher(node)
        
        t0 = c.ruleset.set(ruleset)
        t1 = c.key.set(key)
        
        res = module.transform_tree()
        
        c.key.reset(t1)
        c.ruleset.reset(t0)
        
        return res
    
    def matcher()->tuple[TransformerModule, TransformerRuleset, Any]:
        pass

class TransformerRuleset():
    def __default__(self,):
        pass

class TransformerModule():
    _transform_depth_first : True

    @classmethod
    def get_keys(cls)->tuple[str|Any]:
        ''' Returns keys for the matcher '''
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
            
    def transform_tree(self, c:TransformerContext, key:str|Any, node:Any, *args, **kwargs)->IGNORE|Any:
        # TODO: Determine if I can just make it so that the entire grouping of contextvars is reset after calling children 

        kt : dict[str,Token] = {
            "chain" : c.chain_incoming.set(*c.chain.get(tuple()), node),
            "children" : c.children.set(None),
            "children_map" : c.children_map.set(None),
        }
        _kt : dict[str,Token]|None = None

        res : IGNORE|Any 

        func : Generator|Callable = self.transform
        if not isgeneratorfunction(self.transform): ## Ensuring uniform interface
            if self._transform_depth_first:
                def func(node, c, *args, **kwargs):
                    yield self._get_children_default(node)
                    yield self.transform(node, c, *args, **kwargs)
            else:
                def func(node, c, *args, **kwargs):
                    res = self.transform(node, c, *args, **kwargs)
                    yield self._get_children_default(node)
                    yield res

        generator = func(node, c, *args, **kwargs)
        children : None|TERMINAL|Iterable = next(generator)

        if (children is None):
            children = self._get_children_default(node)
            if not ((children is None) or (children is TERMINAL)):
                _kt = self._transform_children_default(children) #-> SIDE EFFECT: context.?
                
        elif not (children is TERMINAL):
            _kt = self._transform_children_yielded(children)  #-> SIDE EFFECT: context.?

        res = next(generator)

        if _kt:
            kt = _kt | kt   ## oldest key priority

        for k,t in kt.items():
            getattr(c,k).reset(t)

        return res

    def transform(self, node, c:TransformerContext, *args, **kwargs):
        ''' Transform this node
        If Generator:
            - Yield children first to transform them or TERMINAL to not set any children
            - transformed children are then set in c.children and c.children_map
                - set by function (_transform_children_default | _transform_children_yielded | _transform_children)
            - Yield result after to return the transformed value
            - before first yield, timing is eq to root first
            - after second yield timing is eq to depth first
        If Not Generator:
            - default timing is eq to depth first, all children should be transformed.
            - Root first timing;
                - set inherited flag (class._transform_depth_first = False)
                - Usefull when children attach themselves to the parent, or are otherwise distributed. 
                - in this case, c.children and c.children_map will *always* be None
        '''
        yield TERMINAL #None|TERMINAL|Iterable[MyChildren]
        yield IGNORE