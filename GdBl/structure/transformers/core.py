from __future__ import annotations

from typing import Any
from contextvars import ContextVar

from ....GdPy.structure.core import GdType
from ....GdPy.structure.core.transformer_v2 import TransformerRuleset, TransformerModule, TransformerContext
from ....GdPy.structure.core.lark_transformer import BasePyStructureRuleset

class BlPyTransformerContext(TransformerContext):
    property_collection : ContextVar
    # property_obj_attr : ContextVar[tuple[Any,str]]

    def __init__(self, transformer, rulesets = None):
        self.property_collection = ContextVar(str(id(self))+"property_collection")
        self.property_obj_attr = ContextVar(str(id(self))+"property_obj_attr")
        super().__init__(transformer, rulesets)

class PyToBlRuleset(BasePyStructureRuleset):
    ''' Shallow inheritance for iterating over all py objects and extracting keys '''


class PyToBl(TransformerModule):
    ''' Shallow Inheritance for traversing and calling transform on all Blender Objects '''
    _keys : tuple[Any] = tuple()
    def get_keys(self):
        return self._keys

class BlToPyRuleset(TransformerRuleset):
    ''' Base for iterating over all Blender objects and extracting keys '''
    def _key_extractor(self,key)->tuple:
        if key is None:
            return (key, "None")
        return (key.__class__, key.__class__.__name__)

class BlToPy(TransformerModule):
    ''' Base for traversing and calling transform on all Blender Objects '''
    _keys : tuple[Any] = tuple()
    def get_keys(self):
        return self._keys