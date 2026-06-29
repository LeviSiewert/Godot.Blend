import bpy
from typing import Generator

from ._utils import BlenderPytestAttr, BlenderPytest

from ..structure.property_collection import BlPropertyCollection

from ..structure.sub_resources import (
    SubResource as BlSubResource, 
    SubResourceCategory as BlSubResourceCategory, 
    SubResourceExt as BlSubResourceExt, 
    SubResourceNode as BlSubResourceNode,
)
from ..structure._tranformers import (
    BlToPyTransformer,
    PyToBlTransformer,
)

from ..structure.core.tranformer_base import BlPyTransformerContext

from ...GdPy.structure.sub_resources import (
    SubResource as GdSubResource,
    SubResourceCategory as GdSubResourceCategory, 
    SubResourceExt as GdSubResourceExt, 
    SubResourceNode as GdSubResourceNode,
)
from ...GdPy.tests.sub_resources_test import (
    TestSubResource as GdTestSubResource,
    TestSubResourceCategory as GdTestSubResourceCategory,
    TestSubResourceExt as GdTestSubResourceExt,
    TestSubResourceNode as GdTestSubResourceNode,
)

py_to_bl_context = BlPyTransformerContext(PyToBlTransformer)
bl_to_py_context = BlPyTransformerContext(BlToPyTransformer)

class TestSubResourceExt(BlenderPytestAttr):
    attr_value = bpy.props.CollectionProperty(type = BlSubResourceExt)

    def data(self)->Generator[tuple[BlSubResourceExt,GdSubResourceExt]]:
        col : bpy.types.CollectionProperty = self.get_attr()
        py_to_bl_context.property_collection.set(col)
        bl_to_py_context.property_collection.set(col)

        def conv(gd_val:GdSubResourceExt):
            bl_val : BlSubResourceExt = col.add()
            bl_val.gdtype = gd_val.type
            bl_val.path = gd_val.path
            bl_val.uid = gd_val.uid 
            bl_val.unique_id = gd_val.id
            return bl_val

        for _,gd_value in GdTestSubResourceExt().data():
            yield conv(gd_value), gd_value
            col.clear()

    def test_py_to_bl(self,):
        def compare(a:BlSubResource,b:BlSubResource):
            assert(a.gd_type == a.gd_type)
            assert(a.path == a.path)
            assert(a.uid == a.uid) 
            assert(a.unique_id == a.unique_id)

        for bl_value, gd_value in self.data():
            res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
            compare(res, bl_value)

    def test_bl_to_py(self,):
        for bl_value, gd_value in self.data():
            res = BlToPyTransformer.transform_tree(bl_to_py_context, bl_value)
            assert(res == gd_value)
            

class TestSubResourceCategory(BlenderPytestAttr):
    attr_value = bpy.props.PointerProperty(type = BlSubResourceCategory)

    def data(self)->Generator[tuple[BlSubResourceCategory, GdSubResourceCategory]]:
        col : bpy.types.CollectionProperty = self.get_attr()
        py_to_bl_context.property_collection.set(col)
        bl_to_py_context.property_collection.set(col)

        def conv(gd_val:GdSubResourceCategory):
            bl_val : BlSubResourceCategory = col.add()
            bl_val.name = gd_val.name
            props : BlPropertyCollection = bl_val.properties
            for k,v in gd_value.properties.items.items():
                props.set_property(k,v)
            return bl_val
        
        for _,gd_value in GdTestSubResourceCategory().data():
            yield conv(gd_value), gd_value
            col.clear()

    def test_py_to_bl(self,):
        def compare(a:GdSubResourceCategory,b:GdSubResourceCategory):
            assert(a.name == b.name)
            assert(BlToPyTransformer.transform_tree(bl_to_py_context,a.properties) == BlToPyTransformer.transform_tree(bl_to_py_context,b.properties))

        for bl_value, gd_value in self.data():
            res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
            compare(res, bl_value)

    def test_bl_to_py(self,):
        for bl_value, gd_value in self.data():
            res = BlToPyTransformer.transform_tree(bl_to_py_context, bl_value)
            assert(res == gd_value)
    
class TestSubResource(BlenderPytestAttr):
    attr_value = bpy.props.PointerProperty(type = BlSubResource)

    def data(self)->Generator[tuple[BlSubResource, GdSubResource]]:
        col : bpy.types.CollectionProperty = self.get_attr()
        py_to_bl_context.property_collection.set(col)
        bl_to_py_context.property_collection.set(col)


        def conv(gd_val:GdSubResource):
            bl_val : BlSubResource = col.add()
            bl_val.name = gd_val.name
            bl_val.gd_type = gd_val.type
            bl_val.unqiue_id = gd_val.id
            
            props : BlPropertyCollection = bl_val.properties
            for k,v in gd_value.properties.items.items():
                props.set_property(k,v)
            return bl_val
        
        for _,gd_value in GdTestSubResource().data():
            yield conv(gd_value), gd_value
            col.clear()

    def test_py_to_bl(self,):
        def compare(a:BlSubResource,b:BlSubResource):
            assert(a.name == b.name)
            assert(a.gd_type == b.gd_type)
            assert(a.unqiue_id == b.unqiue_id)
            assert(BlToPyTransformer.transform_tree(bl_to_py_context, a.properties) == BlToPyTransformer.transform_tree(b.properties))

        for bl_value, gd_value in self.data():
            res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
            compare(res, bl_value)

    def test_bl_to_py(self,):
        for bl_value, gd_value in self.data():
            res = BlToPyTransformer.transform_tree(bl_to_py_context, bl_value)
            assert(res == gd_value)

# class TestSubResourceNode(BlenderPytest):
#     ''' Generating and applying attributes onto a new empty, subtype testing is part of modular implemenation 
#     INITIAL: (TreeZip) transformers will be prioritized and supercede this transformer
#     '''

#     @classmethod
#     def setup_class(cls):
#         return super().setup_class()

#     @classmethod
#     def teardown_class(cls):
#         return super().teardown_class()
        

#     def data(self)->Generator[tuple[BlSubResourceNode, GdSubResourceNode]]:
#         col : bpy.types.CollectionProperty = self.get_attr()
        # py_to_bl_context.property_collection.set(col)
        # bl_to_py_context.property_collection.set(col)

#         def conv(gd_val:GdSubResourceNode):
#             bl_val : bpy.types.Object = col.add()

#             bl_val.name = gd_val.name
#             bl_val.gd.name = gd_val.name
#             bl_val.gd.gd_type = gd_val.type
#             bl_val.gd.unqiue_id = gd_val.id
            
#             props : BlPropertyCollection = bl_val.properties
#             for k,v in gd_value.properties.items.items():
#                 props.set_property(k,v)
#             return bl_val
        
#         for _,gd_value in GdTestSubResource().data():
#             yield conv(gd_value), gd_value
#             col.clear()

#     def test_py_to_bl(self,):
#         def compare(a:BlSubResource,b:BlSubResource):
#             assert(a.name == b.name)
#             assert(a.gd_type == b.gd_type)
#             assert(a.unqiue_id == b.unqiue_id)
#             assert(BlToPyTransformer.transform_tree(a.properties) == BlToPyTransformer.transform_tree(b.properties))

#         for bl_value, gd_value in self.data():
#             res = PyToBlTransformer.transform_tree(py_to_bl_context, gd_value)
#             compare(res, bl_value)

#     def test_bl_to_py(self,):
#         for bl_value, gd_value in self.data():
#             res = BlToPyTransformer.transform_tree(bl_value)
#             assert(res == gd_value)