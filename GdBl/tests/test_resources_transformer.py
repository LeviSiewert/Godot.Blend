import bpy
import pytest
from typing import Generator

from ._utils import BlenderPytestAttr, BlenderPytest

from ..structure.property_collection import BlPropertyCollection

from ..structure._tranformers import (
    BlToPyTransformer,
    PyToBlTransformer,
)

from ..structure.resources import (
    ResourceTres as BlResourceTres, 
    ResourceScene as BlResourceScene, 
    ResourceImport as BlResourceImport, 
)
from ...GdPy.structure.resources import (
    ResourceTres as GdResourceTres, 
    ResourceScene as GdResourceScene, 
    ResourceImport as GdResourceImport, 
)
from ...GdPy.tests.resources_test import (
    TestResourceTres as GdTestResourceTres,
    TestResourceScene as GdTestResourceScene,
    TestResourceImport as GdTestResourceImport,
)

from ..structure.core.tranformer_base import BlPyTransformerContext
py_to_bl_context = BlPyTransformerContext(PyToBlTransformer)
bl_to_py_context = BlPyTransformerContext(BlToPyTransformer)

@pytest.mark.dependency()
class TestResourceTres(BlenderPytestAttr):
    attr_value = bpy.props.CollectionProperty(type = BlResourceTres)

    def data(self)->Generator[tuple[BlResourceTres,GdResourceTres]]:
        col : bpy.types.CollectionProperty = self.get_attr()
        py_to_bl_context.property_collection.set(col)
        bl_to_py_context.property_collection.set(col)

        def conv(gd_val:GdResourceTres):
            bl_val : BlResourceTres = col.add()
            # bl_val.gdtype = gd_val.type
            return bl_val

        for _,gd_value in GdTestResourceTres().data():
            yield conv(gd_value), gd_value
            col.clear()

    def test_py_to_bl(self,):
        def compare(a:BlResourceTres, b:BlResourceTres):
            # assert(a.gd_type == a.gd_type)
            pass

        for bl_value, gd_value in self.data():
            res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
            compare(res, bl_value)

    def test_bl_to_py(self,):
        for bl_value, gd_value in self.data():
            res = BlToPyTransformer.transform_tree(bl_to_py_context, bl_value)
            assert(res == gd_value)
            