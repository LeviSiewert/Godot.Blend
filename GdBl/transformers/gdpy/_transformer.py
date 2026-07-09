from ....GdPy.core.transformer import Transformer, TransformerRuleset, TransformerModule, Context

from contextvars import ContextVar

class PyToBlContext(Context):
    def __init__(self):
        super().__init__()
        self.existing_object = ContextVar("existing_object", default=None)
        self.property_collection = ContextVar("property_collection", default=None)


PyToBlTransformer = Transformer

PyToBlRuleset = TransformerRuleset

PyToBlModule = TransformerModule


class BlToPyContext(Context):
    def __init__(self):
        super().__init__()
        self.existing_object = ContextVar("existing_object", default=None)
        self.property_collection = ContextVar("property_collection", default=None)

BlToPyTransformer = Transformer

BlToPyRuleset = TransformerRuleset

BlToPyModule = TransformerModule
