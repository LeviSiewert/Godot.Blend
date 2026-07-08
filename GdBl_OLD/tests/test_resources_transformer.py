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
from ...GdPy.tests.references_test import (
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
            bl_val : GdResourceTres = col.add()
            bl_val.gd_type =gd_val.type
            bl_val.uid = gd_val.uid

            t = py_to_bl_context.property_collection.set(bl_val.properties)
            PyToBlTransformer(gd_val.properties)
            py_to_bl_context.property_collection.reset(t)

            t = py_to_bl_context.property_collection.set(bl_val.ext_resources)
            PyToBlTransformer(gd_val.ext_resources)
            py_to_bl_context.property_collection.reset(t)

            t = py_to_bl_context.property_collection.set(bl_val.sub_resources)
            PyToBlTransformer(gd_val.sub_resources)
            py_to_bl_context.property_collection.reset(t)

            return bl_val

        for _,gd_value in GdTestResourceTres().data():
            yield conv(gd_value), gd_value
            col.clear()

    def test_py_to_bl(self,):
        def compare(a:BlResourceTres, b:BlResourceTres):
            assert (a.gd_type == b.gd_type)
            assert (a.format == b.format)
            assert (a.uid == b.uid)
            assert (BlToPyTransformer.transform_tree(bl_to_py_context,a.properties) == BlToPyTransformer.transform_tree(bl_to_py_context,b.properties))
            assert (BlToPyTransformer.transform_tree(bl_to_py_context,a.ext_resources) == BlToPyTransformer.transform_tree(bl_to_py_context,b.ext_resources))
            assert (BlToPyTransformer.transform_tree(bl_to_py_context,a.sub_resources) == BlToPyTransformer.transform_tree(bl_to_py_context,b.sub_resources))

        for bl_value, gd_value in self.data():
            res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
            compare(res, bl_value)

    def test_bl_to_py(self,):
        for bl_value, gd_value in self.data():
            res = BlToPyTransformer.transform_tree(bl_to_py_context, bl_value)
            assert(res == gd_value)
            
@pytest.mark.dependency()
class TestResourceImport(BlenderPytestAttr):
    attr_value = bpy.props.CollectionProperty(type = BlResourceImport)

    def data(self)->Generator[tuple[BlResourceImport,GdResourceImport]]:
        col : bpy.types.CollectionProperty = self.get_attr()
        py_to_bl_context.property_collection.set(col)
        bl_to_py_context.property_collection.set(col)

        def conv(gd_val:GdResourceImport):
            bl_val : GdResourceImport = col.add()
            bl_val.gd_type =gd_val.type
            bl_val.uid = gd_val.uid

            t = py_to_bl_context.property_collection.set(bl_val.cat_resources)
            PyToBlTransformer(gd_val.cat_resources)
            py_to_bl_context.property_collection.reset(t)

            return bl_val

        for _,gd_value in GdTestResourceImport().data():
            yield conv(gd_value), gd_value
            col.clear()

    def test_py_to_bl(self,):
        def compare(a:BlResourceImport, b:BlResourceImport):
            assert (a.gd_type == b.gd_type)
            assert (a.uid == b.uid)
            assert (BlToPyTransformer.transform_tree(bl_to_py_context,a.cat_resources) == BlToPyTransformer.transform_tree(bl_to_py_context,b.cat_resources))

        for bl_value, gd_value in self.data():
            res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
            compare(res, bl_value)

    def test_bl_to_py(self,):
        for bl_value, gd_value in self.data():
            res = BlToPyTransformer.transform_tree(bl_to_py_context, bl_value)
            assert(res == gd_value)

# class TestResourceScene(BlenderPytestAttr):
#     ''' Complex behavior is in a SEPERATE FILE for the most part! Behavior is complex enough to require '''