import bpy #type:ignore
from typing import Any
from contextlib import contextmanager

from .utils import BlenderPytestAttr

from ..structure.core.properties import BlPropertyCollection, BlProperty
from ..structure.transformers import BlToPyTransformer, PyToBlTransformer
from ...GdPy.structure.core import GdType
from ...GdPy.structure.values import (
    GdValueStringName,
)

_bl_to_py_context = BlToPyTransformer.make_context()
def bl_to_py_transform(property:BlProperty)->GdType|Any:
    res = BlToPyTransformer.transform_tree(_bl_to_py_context, property)
    return res 

_py_to_bl_context = PyToBlTransformer.make_context()
def py_to_bl_transform(property:BlProperty, gdtype:GdType)->Any:
    ## Due to blender's struct req of properties, have to set existing prop as target.
    t = _py_to_bl_context.existing_object.set(property)
    res = PyToBlTransformer.transform_tree(_py_to_bl_context, gdtype)
    _py_to_bl_context.existing_object.reset(t)
    return res


class _Base(BlenderPytestAttr):
    attr_name = "test"
    attr_value = bpy.props.PointerProperty(type=BlProperty)

    @contextmanager
    def set_prop(self, **kwargs):
        prop = self.get_attr()
        o_values = {}
        for k,v in kwargs.items():
            o_values[k] = getattr(prop,k)
            setattr(prop,k,v)
        yield prop
        for k,v in o_values.items():
            setattr(prop,k,v)
    
    @contextmanager
    def py_as_prop(self, gdtype:GdType):
        yield py_to_bl_transform(self.get_attr(), gdtype)

class TestGdValueStringName(_Base):
    def test_bl_to_py(self,):
        with self.set_prop(type="GdValueStringName", val_str="value") as prop:
            assert(isinstance(bl_to_py_transform(prop), GdValueStringName))
            assert(bl_to_py_transform(prop) == GdValueStringName("value"))

    def test_py_to_bl(self,):
        with self.py_as_prop(GdValueStringName("value")) as prop:
            assert(prop.type == "GdValueStringName")
            assert(prop.value == "value")


class TestGdValueArray(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector2(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector3(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector4(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector2i(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector3i(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector4i(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueRect2(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueRect2i(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePlane(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueColor(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueAABB(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueQuaternion(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueTransform2D(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueBasis(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueTransform3D(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedByteArray(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedInt32Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedInt64Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedFloat32Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedFloat64Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedStringArray(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedVector2Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedVector3Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedVector4Array(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedColorArray(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueDictionary(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

# class TestProperties(BlenderPytestAttr):
#     attr_name = "property_collection" 
#     attr_value = PointerProperty(type=BlPropertyCollection)

#     def test_attr(self):
#         c = BlContext()
#         transformer = Transformer([TrfmProperty])
        
#         vals = {"testa":"1", "testb":"2"}

#         source_data = GdPropertyCollection(vals.items())

#         c.meta_tree.set((self.get_attr_loc()[0],))
#         transformer.to_blender(c, source_data)
        
#         col = self.get_attr()

#         for k,v in vals.items():
#             assert(k in col.items.keys())
#             assert(col[k].value == v)

#         # raise Exception("Not yet implimented")


    