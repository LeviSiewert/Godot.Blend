from .primitives import Context
from .transformer_v2 import Transformer, TransformerModule, TransformerRuleset, TERMINAL, IGNORE, DEFAULT, TransformerContext
from lark.visitors import Tree, Token #type:ignore
from typing import Any, Iterable, Type, Callable
from .property_collection import PropertyCollection
from abc import ABC, abstractmethod

''' Custom transformer for lark types of (Tree|Token) for uniformity of first and second pass transformer implementations, along with parsing flexibility '''

class GdToPyRuleset(TransformerRuleset):
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
            return self._transform(tc.key.get(), tc, c, *args, *tc.children.get(tuple()), **kwargs)
    @abstractmethod
    def _transform(self, key, tc, gdc, *children):
        pass


class PyToGdRuleset(TransformerRuleset):
    pass

class PyToGd(TransformerModule, ABC):
    pass



# class LarkTransformerModule(TransformerModule):
#     ''' Attempting eq behavior to Lark.visitors.Transformer.transform() to a new tree by calling _transform() with expanded children and depth-first '''

#     def get_keys(self):
#         return tuple()
    
#     def _get_children_default(self, node:Tree|Token|None):
#         if isinstance(node, Tree):
#             return node.children
        
#         if isinstance(node, Token):
#             return TERMINAL

#         if node is None:
#             return None
        
#         raise KeyError("Could not determine children of unknown object:", node)
    
#     def transform(self, node:Tree|Token, tc:TransformerContext, gdc:Context, *args, **kwargs):
#         ''' Called on each token, children already exist, are ordered and are nullable '''
#         key = tc.key.get()
#         children = tc.children.get()
#         if children is None:
#             children = tuple()
#         return self._transform(key, tc, gdc, *children)
    
#     def _transform(self, key:str, tc:TransformerContext, gdc:Context, *children)->Any:
#         return IGNORE

# class LarkTransformerModuleCentralized(LarkTransformerModule):
#     ''' A central transformer module for extracting lark_keys and parse_lark.
#     Planned to be depreciated in the future in favor of GdType subclasses OR seperate files. 
#     '''
#     transformers : dict[str, Callable]
#     _get_parse_keys = "lark_keys"
#     _get_parse_func = "parse_lark"

#     def get_keys(self,):
#         return self.transformers.keys()

#     def __init__(self, objects:Iterable[Type]):
#         self.transformers = {}
#         for obj in objects:
#             for k in getattr(obj, self._get_parse_keys)():
#                 v = getattr(obj, self._get_parse_func)
#                 self.transformers[k] = v 
#         super().__init__()

#     # def _transform(self, key:str, c:Context, *args, **kwargs)->Any:
#     def _transform(self, key:str, tc:TransformerContext, gdc:Context, *children)->Any:
#         if isinstance(tc.node.get(), Tree):
#             return self.transformers[key](key, tc, gdc, *children)
#         else:
#             return self.transformers[key](key, tc, gdc, tc.node.get())




