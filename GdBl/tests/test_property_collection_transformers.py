import bpy
from typing import Generator

from .utils import BlenderPytestAttr
from ..structure.core.properties import BlPropertyCollection, BlArray, BlDictionary, BlPrimitives, BlVectors
from ..structure.core.primitives.pointer_collection import BlPointerArrayItemWrapper, BlPointerArrayWrapper, BlPointerDictionaryItemWrapper, BlPointerDictionaryWrapper, _Wrapper
from ...GdPy.structure.core.property_collection import PropertyCollection as GdPropertyCollection
from ...GdPy.structure import values as GdPy



from typing import Any

from ..structure.transformers.property_collection import py_to_bl_ruleset, bl_to_py_ruleset
from ...GdPy.structure.core.transformer_v2 import Transformer

from ..structure.transformers.core import BlPyTransformerContext

from contextlib import contextmanager

_bl_to_py_transformer = Transformer((bl_to_py_ruleset,))
_bl_to_py_context = BlPyTransformerContext(_bl_to_py_transformer)

@contextmanager
def _bl_to_py(bl_pc)->Generator[GdPropertyCollection]:
    ''' Yield a new GdPropertyCollection from the BlPropertyCollection object'''
    t = _bl_to_py_context.property_collection.set(bl_pc)
    t1 = _bl_to_py_context.existing_object.set(bl_pc)
    yield _bl_to_py_transformer.transform_tree(_bl_to_py_context,bl_pc)
    _bl_to_py_context.property_collection.set(t)
    _bl_to_py_context.existing_object.reset(t1)
    bl_pc.clear()

_py_to_bl_transformer = Transformer((py_to_bl_ruleset,))
_py_to_bl_context = BlPyTransformerContext(_py_to_bl_transformer)
@contextmanager
def _py_to_bl(bl_pc, gd_pc)->Generator[BlPropertyCollection]:
    ''' Yield a transformed bl_pc (same as input object)'''
    t = _py_to_bl_context.property_collection.set(bl_pc)
    t1 = _py_to_bl_context.existing_object.set(bl_pc)
    yield _py_to_bl_transformer.transform_tree(_py_to_bl_context,gd_pc)
    _py_to_bl_context.property_collection.set(t)
    _py_to_bl_context.existing_object.reset(t1)
    bl_pc.clear()

