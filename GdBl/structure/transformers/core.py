from __future__ import annotations

from typing import Any
from contextvars import ContextVar

from ....GdPy.structure.core import GdType
from ....GdPy.structure.core.transformer_v2 import TransformerRuleset, TransformerModule, TransformerContext
from ....GdPy.structure.core.lark_transformer import BasePyStructureRuleset

class PyToBlRuleset(BasePyStructureRuleset):
    ''' Shallow inheritance for iterating over all py objects and extracting keys '''

class PyToBl(TransformerModule):
    ''' Shallow Inheritance for traversing and calling transform on all Blender Objects '''
    _keys : tuple[Any] = tuple()
    def get_keys(self):
        return self._keys

class BlToPyRuleset(TransformerRuleset):
    ''' Base for iterating over all Blender objects and extracting keys '''

class BlToPy(TransformerModule):
    ''' Base for traversing and calling transform on all Blender Objects '''
    _keys : tuple[Any] = tuple()
    def get_keys(self):
        return self._keys

class PyToBlContext(TransformerContext):
    existing_object : ContextVar[tuple[object,str]]
    def __init__(self, transformer, rulesets):
        self.existing_object = ContextVar(str(id(self))+"existing_object")
        super().__init__(transformer, rulesets)