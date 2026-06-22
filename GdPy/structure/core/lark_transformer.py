from .primitives import Context
from .transformer_v2 import Transformer, TransformerModule, TransformerRuleset, TERMINAL, IGNORE, DEFAULT, TransformerContext
from lark.visitors import Tree, Token #type:ignore
from typing import Any, Iterable, Type, Callable
from .property_collection import PropertyCollection
from abc import ABC, abstractmethod
from .core import GdType

''' Custom transformer for lark types of (Tree|Token) for uniformity of first and second pass transformer implementations, along with parsing flexibility '''

class GdToPyRuleset(TransformerRuleset):
    ''' Ruleset for iterating over Lark Tree|Token trees '''
    def _key_extractor(self, key:Tree|Token|None):
        if isinstance(key, Tree):
            return (str(key.data),)
            # return key.data
        
        if isinstance(key, Token):
            return (str(key.type),)
        
        return super()._key_extractor(key)


class GdToPy(TransformerModule, ABC):
    def _get_children_default(self, node:Tree|Token|None):
        if isinstance(node, Tree):
            return node.children
        
        if isinstance(node, Token):
            return TERMINAL

        if node is None:
            return TERMINAL
        
        raise KeyError("Could not determine children of unknown object:", node)

    _keys : tuple = tuple()
    def get_keys(self):
        return self._keys
    def transform(self, node:Any, tc:TransformerContext, c:Context, *args, **kwargs):
        if tc.children.get() is TERMINAL:
            return self._transform(tc.key.get(), tc, c)
        else:
            children = tc.children.get()
            if children is None:
                children = tuple()
            return self._transform(tc.key.get(), tc, c, *args, *children, **kwargs)
    
    def _transform(self, key, tc, gdc, *children):
        pass


class BasePyStructureRuleset(TransformerRuleset):
    ''' Ruleset structure for iterating over GdPy Objects, Inherit here as future key rules will extract project level information '''
    def _key_extractor(self,key)->tuple[str|Any|Type]:
        if key is None:
            return (key, "None")
        return (key.__class__, key.__class__.__name__)
    
    def _get_children_default(self, node:GdType):
        if hasattr(node, "get_struct_children"):
            return node.get_struct_children()
        return TERMINAL
    
class PyToGdRuleset(BasePyStructureRuleset):
    pass

class PyToGd(TransformerModule, ABC):
    _keys : tuple = tuple()
    def get_keys(self):
        return self._keys

    def transform(self, node:Any, tc:TransformerContext, c:Context, *args, **kwargs):
        if tc.children.get() is TERMINAL:
            return self._transform(tc.key.get(), tc, c, tc.node.get())
        else:
            return self._transform(tc.key.get(), tc, c, tc.node.get(), *args, *tc.children.get(tuple()), **kwargs)
    
    # @abstractmethod
    def _transform(self, key, tc, gdc, node, *children):
        pass
