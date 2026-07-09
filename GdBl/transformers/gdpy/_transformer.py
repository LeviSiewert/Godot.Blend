from ....GdPy.core.transformer import Transformer, TransformerRuleset, TransformerModule, Context

from contextvars import ContextVar

class PyToBlContext(Context):
    def __init__(self):
        super().__init__()
        self.existing_object = ContextVar("existing_object", default=None)


PyToBlTransformer = Transformer

PyToBlRuleset = TransformerRuleset

PyToBlModule = TransformerModule


BlToPyContext = Context

BlToPyTransformer = Transformer

BlToPyRuleset = TransformerRuleset

BlToPyModule = TransformerModule