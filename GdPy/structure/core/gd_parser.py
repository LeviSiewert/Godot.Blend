from typing import Type, Callable
from lark.visitors import Transformer #type:ignore
from lark import Lark #type:ignore
from .core import GdType, Context

class GdParser():
    types : list[Type]
    grammer : str
    
    _transformer : Transformer
    
    def __init__(self, grammer:str, types:list[Type]):
        self.grammer = grammer
        self.types = types

    def construct_transformer_function(self,key,func)->Callable:
        def res(*args, **kwargs):
            func(key, *args, **kwargs)
        return res

    def construct_transformer(self):
        class transformer(Transformer):
            pass

        for x in self.types:
            assert(getattr(x,"_lark_key", None))
            assert(getattr(x,"_lark_transformer", None))
            setattr(transformer, x._lark_key, self.construct_transformer_function(x._lark_key, x._lark_transformer))

        self._transformer = transformer

    def parse(self, data:str, context:Context, start:str=None)->GdType|None:
        parser = Lark(self.grammer, maybe_placeholders=True, start=start)
        tree = self._transformer.transform(parser.parse(data))
        return tree