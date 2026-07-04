''' localization, centralizing planned future behavior changes ''' 

from ...core.transformer import Transformer, TransformerRuleset, TransformerModule, Context
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )

from contextvars import ContextVar

class RenderingOptions():
    float_as_int_ok : ContextVar[bool]
    float_percision : ContextVar[int]
    float_tail_req_len : ContextVar[int]

    def render_float(self, f:float)->str:
        if self.float_as_int_ok.get() and f.is_integer():
            return str(int(f))
        return f'{f:g}'

    def __new__(cls):
        self = super().__new__(cls)        
        self.float_as_int_ok = ContextVar("float_as_int_ok", default = False)
        self.float_percision = ContextVar("float_percision", default = 10)
        self.float_tail_req_len = ContextVar("float_tail_req_len", default = 1)
        return self

class PyToGdContext(Context):
    rendering : RenderingOptions
    def __new__(cls):
        self = super().__new__(cls)
        self.rendering = RenderingOptions()
        return self


PyToGdTransformer = Transformer

PyToGdRuleset = TransformerRuleset

class PyToGdModule(TransformerModule):
    def transform(self, c, node):
        raise NotImplementedError(f"{self}.transform")

GdToPyContext = Context

GdToPyTransformer = Transformer

class GdToPyRuleset(TransformerRuleset):
    ''' Extraction of keys from a lark-tree to Python object tree '''

    def _extract_keys(self, node):
            
        if isinstance(node, LarkToken):
            return (str(node.type),)

        if isinstance(node, LarkTree):
            return (str(node.data),) 
        
        return super()._extract_keys(node)

class GdToPyModule(TransformerModule):
    def transform(self, c, node):
        raise NotImplementedError(f"{self}.transform")

