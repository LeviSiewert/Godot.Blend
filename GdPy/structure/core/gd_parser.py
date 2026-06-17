from typing import Any, Type, Iterable

from .core import GdType, Context
from .primitives import CacheTreeNode
from .transformer_v2 import Transformer, TransformerRuleset
from lark import Lark #type:ignore


class GdParser():
    def __init__(self, grammer, rulesets:Iterable[TransformerRuleset], start:str="start"):
        self.grammer = grammer
        self._parser = Lark(self.grammer, maybe_placeholders=True, start = start)
        self._transformer = Transformer(rulesets)
        self._start_default = start
    
    def parse(self, context:Context, data:str, cache_tree:CacheTreeNode=None, start:str=None)->GdType|Any:
        _parser = self._parser
        if start and (start != self._start_default):
            _parser = Lark(self.grammer, maybe_placeholders=True, start=start)
        tree = _parser.parse(data) 
        result = self._transformer.transform_tree(None, tree, context)
        # if isinstance(result, GdType) and cache_tree:
        #     with cache_tree.traverse(True):
        #         self.build_cache_tree(result)
        return result
    
# from ..resources import grammer
# from .values_transformer import gd_to_py_ruleset as values_ruleset
# from .sub_resources_transformer import gd_to_py_ruleset as subres_ruleset

# gdparser = 