from typing import Any, Type, Iterable

from .core import GdType, Context
from .primitives import CacheTreeNode
from .transformer_v2 import Transformer, TransformerRuleset
from lark import Lark #type:ignore


class GdParser():
    ''' TODO: This class's purpose will be superceded by a contextual-project module approach *eventually* '''
    def __init__(self, grammer, parser_rulesets:Iterable[TransformerRuleset], render_rulesets:Iterable[TransformerRuleset], start:str="start"):
        self.grammer = grammer
        self._parser = Lark(self.grammer, maybe_placeholders=True, start = start)
        self._parser_transformer = Transformer(parser_rulesets)
        self._render_transformer = Transformer(render_rulesets)
        self._start_default = start
    
    def parse(self, context:Context, data:str, cache_tree:CacheTreeNode=None, start:str=None)->GdType|Any:
        _parser = self._parser
        if start and (start != self._start_default):
            _parser = Lark(self.grammer, maybe_placeholders=True, start=start)
        tree = _parser.parse(data) 
        result = self._parser_transformer.transform_tree(None, tree, context)
        # if isinstance(result, GdType) and cache_tree:
        #     with cache_tree.traverse(True):
        #         self.build_cache_tree(result)
        return result
    
    def render(self, context:Context, data:GdType)->str:
        ''' Render data back to strings '''
        return self._render_transformer.transform_tree(None, data, context)