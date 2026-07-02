''' localization, centralizing planned future behavior changes ''' 

from ...core.transformer import Transformer, TransformerRuleset, TransformerModule, Context
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )

PyToGdContext = Context

PyToGdTransformer = Transformer

PyToGdRuleset = TransformerRuleset

class PyToGdModule(TransformerModule):
    def transform(self, c, node):
        raise NotImplementedError()

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
        raise NotImplementedError()


