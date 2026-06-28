from ...GdPy.structure.core.transformer_v2 import Transformer

from . import property_collection_transformer

BlToPyTransformer = Transformer((
    property_collection_transformer.bl_to_py_ruleset,
))

PyToBlTransformer = Transformer((
    property_collection_transformer.py_to_bl_ruleset,
))