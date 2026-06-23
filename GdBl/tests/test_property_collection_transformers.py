import bpy
from typing import Generator

from .utils import BlenderPytestAttr
from ..structure.core.properties import BlPropertyCollection, BlPropertyItem, BlPropertyItemWrapper
from ...GdPy.structure.core.property_collection import PropertyCollection as GdPropertyCollection
from ...GdPy.structure import values as V

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


class TestPrimitives(BlenderPytestAttr):
    attr_value = bpy.props.PointerProperty(type = BlPropertyCollection)

    def test_py_to_bl(self,):
        tests = (
            ("A", V.GdValueStringName("Value"), "Value"),
            ("A", "Value", "Value"),
            ("A", 41, 41),
            ("A", 0.005, 0.005),
            ("A", False, False),
            ("A", True, True),
            ("A", None, None),
        )
        for k,v,eq in tests:
            self.base_py_to_bl(k,v,eq)

    def base_py_to_bl(self, k, v, eq):
        gd_pc = GdPropertyCollection({k:v}.items())

        with _py_to_bl(self.get_attr(), gd_pc) as bl_pc:
            assert(len(bl_pc.properties) == 1)
            assert(len(bl_pc.bin_primitives) == 1)
            assert(bl_pc.properties[k])
            assert(bl_pc.properties[k].ptr == bl_pc.bin_primitives[0].name)
            assert(bl_pc[k] == bl_pc.bin_primitives[0])
            assert(isinstance(bl_pc.get(k, return_ptr=True, _wrap_complex=True), BlPropertyItemWrapper))

            if v is None:
                assert(bl_pc[k].gdtype == "None")
            else:
                assert(bl_pc[k].gdtype == v.__class__.__name__)

            if isinstance(eq, float):
                assert(abs(bl_pc[k].get_value()-eq)<.0001)
            else:
                assert(bl_pc[k].get_value() == eq)


    def base_bl_to_py(self, gdtype, name, bl_value, eq_gdvalue):
        bl_pc = self.get_attr()
        bl_pc.new(gdtype, name, bl_value)
        
        with _bl_to_py(bl_pc) as gd_pc:
            if isinstance(gd_pc[name], float):
                assert(abs(gd_pc[name]-eq_gdvalue)<.0001)
            else:
                assert(gd_pc[name] == eq_gdvalue)

    def test_bl_to_py(self,):
        tests = [
            ("GdValueStringName", "A", "Value", V.GdValueStringName("Value")),
            ("str", "A", "Value", "Value"),
            ("int", "A", 1, 1),
            ("float", "A", 0.1, 0.1),
            ("None", "A", None, None),
            ("bool", "A", False, False),
            ("bool", "A", True, True),
        ] 

        for (gtype, name, bl_value, eq_gd) in tests:
            self.base_bl_to_py(gtype, name, bl_value, eq_gd)
    
class TestArray():
    pass

class TestDictionary():
    pass

class TestFloatVector():
    pass

class TestIntVector():
    pass