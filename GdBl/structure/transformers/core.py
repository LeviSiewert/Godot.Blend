from __future__ import annotations

from ....GdPy.structure.core import GdType
from ....GdPy.structure.core.transformer_v2 import TransformerRuleset, TransformerModule
from ....GdPy.structure.core.lark_transformer import BasePyStructureRuleset

class PyToBlRuleset(BasePyStructureRuleset):
    ''' Shallow inheritance for iterating over all py objects and extracting keys '''

class PyToBl(TransformerModule):
    ''' Shallow Inheritance for traversing and calling transform on all Blender Objects '''


class BlToPyRuleset(TransformerRuleset):
    ''' Base for iterating over all Blender objects and extracting keys '''

class BlToPy(TransformerModule):
    ''' Base for traversing and calling transform on all Blender Objects '''
