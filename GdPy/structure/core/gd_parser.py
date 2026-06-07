from typing import Type, Callable
from lark.visitors import Transformer #type:ignore
from lark import Lark #type:ignore
from .core import GdType, Context
from .core import CacheTree
from contextvars import ContextVar

ctx_cache_tree : ContextVar[CacheTree] = ContextVar("CacheTree")

def standard_cache_tree(self):
    inst = CacheTree([
        "References"
    ])
    return inst

class GdParser():
    types : list[Type]
    grammer : str
    _transformer : Transformer
    
    def __init__(self, grammer:str, types:list[Type]):
        self.grammer = grammer
        self.types = types
        super().__init__()
        self.construct_transformer()

    def construct_transformer_function(self,key,func)->Callable:
        def res(*args, **kwargs):
            return func(key, *args, **kwargs)
        return res

    def construct_transformer(self):
        class transformer(Transformer):
            pass

        for x in self.types:
            if (not hasattr(x,"parse_lark")) or (not hasattr(x,"lark_keys")):
                raise Exception("All supplied types must have parse_lark", x)
            for k in x.lark_keys():
                setattr(transformer, k, self.construct_transformer_function(k, x.parse_lark))

        self._transformer = transformer()

    def parse(self, context:Context, cache_tree:CacheTree, data:str, start:str=None)->tuple[GdType|None, CacheTree]:
        token = ctx_cache_tree.set(cache_tree)
        parser = Lark(self.grammer, maybe_placeholders=True, start=start)
        tree = parser.parse(data) 
        result = self._transformer.transform(tree)
        if isinstance(result, GdType):
            self.populate_ctx_cache_tree(result)
        ctx_cache_tree.reset(token)
        return tree
    
    def populate_ctx_cache_tree(result):
        
        pass