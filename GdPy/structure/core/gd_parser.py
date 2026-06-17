from typing import Any, Type, Iterable

from .core.core import GdType, Context
from .core.primitives import CacheTreeNode
from .core.transformer_v2 import Transformer, TransformerRuleset
from lark import Lark #type:ignore


class GdParser():
    def __init__(self, grammer, rulesets:Iterable[TransformerRuleset]):
        self.grammer = grammer
        self._parser = Lark(self.grammer, maybe_placeholders=True)
        self._transformer = Transformer(rulesets)
    
    def parse(self, context:Context, data:str, cache_tree:CacheTreeNode=None, start:str=None)->GdType|Any:
        tree = self._parser.parse(data, start = start) 
        result = self.transformer.transform_tree(None, tree, context)
        # if isinstance(result, GdType) and cache_tree:
        #     with cache_tree.traverse(True):
        #         self.build_cache_tree(result)
        return result
    
# from ..resources import grammer
# from .values_transformer import gd_to_py_ruleset as values_ruleset
# from .sub_resources_transformer import gd_to_py_ruleset as subres_ruleset

# gdparser = 