import bpy #type:ignore
from typing import Any
from contextlib import contextmanager

from .utils import BlenderPytestAttr

from ..structure.core.properties import BlPropertyCollection, BlProperty, BlPropertyArray, BlPropertyDict, BlPropertyArrayFloat,BlPropertyArrayInt,BlPropertyArrayVector
from ..structure.transformers import BlToPyTransformer, PyToBlTransformer
from ...GdPy.structure.core import GdType
from ...GdPy.structure.values import (
    GdValueStringName,
    GdValueArray,
    GdValueDictionary,
    GdValueVector2,
    GdValueVector3,
    GdValueVector4,
    GdValueVector2i,
    GdValueVector3i,
    GdValueVector4i,
    GdValueRect2,
    GdValueRect2i,
    GdValuePlane,
    GdValueColor,
    GdValueAABB,
    GdValueQuaternion,
    GdValueTransform2D,
    GdValueBasis,
    GdValueTransform3D,
    GdValuePackedByteArray,
    GdValuePackedInt32Array,
    GdValuePackedInt64Array,
    GdValuePackedFloat32Array,
    GdValuePackedFloat64Array,
    GdValuePackedStringArray,
    GdValuePackedVector2Array,
    GdValuePackedVector3Array,
    GdValuePackedVector4Array,
    GdValuePackedColorArray,
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
    attr_value = bpy.props.PointerProperty(type=BlProperty)
    def test_bl_to_py(self,):
        with self.set_prop(type="GdValueStringName", val_str="value") as prop:
            assert(isinstance(bl_to_py_transform(prop), GdValueStringName))
            assert(bl_to_py_transform(prop) == GdValueStringName("value"))

    def test_py_to_bl(self,):
        with self.py_as_prop(GdValueStringName("value")) as prop:
            assert(prop.type == "GdValueStringName")
            assert(prop.value == "value")


class TestGdValueArray_Simple(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyArray)
    def test_bl_to_py(self,):
        raise NotImplementedError()
    def test_py_to_bl(self,):
        raise NotImplementedError()
    
class TestGdValueArray_Complex(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyCollection)
    ## [Variant|Array|Dict] typed arrays requires property collection, which catches recursive elements
    def test_bl_to_py(self,):
        raise NotImplementedError()
    def test_py_to_bl(self,):
        raise NotImplementedError()


class TestGdValueDictionary_Simple(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyDict)
    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueDictionary_Complex(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyCollection)
    ## [Variant|Array|Dict] typed dicts requires property collection, which catches recursive elements
    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class _SimpleArrayBase_Int(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyArrayInt) 
    _py_expected_type : GdType
    _bl_expected_key : str
    BlPropertyArrayInt

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()
    
class _SimpleArrayBase_Float(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyArrayFloat) 
    _py_expected_type : GdType
    _bl_expected_key : str

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class _PackedArrayBase_String(_Base):
    # attr_value = bpy.props.PointerProperty(type=BlPropertyArrayString) 
    _py_expected_type : GdType
    _bl_expected_key : str

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class _PackedArrayBase_Vector(_Base):
    attr_value = bpy.props.PointerProperty(type=BlPropertyArrayVector) 
    _py_expected_type : GdType
    _bl_expected_key : str

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValuePackedByteArray(_Base):

    def test_bl_to_py(self,):
        raise NotImplementedError()

    def test_py_to_bl(self,):
        raise NotImplementedError()

class TestGdValueVector2(_SimpleArrayBase_Float):
    _py_expected_type = GdValueVector2
    _bl_expected_key = "GdValueVector2"

class TestGdValueVector3(_SimpleArrayBase_Float):
    _py_expected_type = GdValueVector3
    _bl_expected_key = "GdValueVector3"

class TestGdValueVector4(_SimpleArrayBase_Float):
    _py_expected_type = GdValueVector4
    _bl_expected_key = "GdValueVector4"

class TestGdValueVector2i(_SimpleArrayBase_Int):
    _py_expected_type = GdValueVector2i
    _bl_expected_key = "GdValueVector2i"

class TestGdValueVector3i(_SimpleArrayBase_Int):
    _py_expected_type = GdValueVector3i
    _bl_expected_key = "GdValueVector3i"

class TestGdValueVector4i(_SimpleArrayBase_Int):
    _py_expected_type = GdValueVector4i
    _bl_expected_key = "GdValueVector4i"

class TestGdValueRect2(_SimpleArrayBase_Float):
    _py_expected_type = GdValueRect2
    _bl_expected_key = "GdValueRect2"

class TestGdValueRect2i(_SimpleArrayBase_Int):
    _py_expected_type = GdValueRect2i
    _bl_expected_key = "GdValueRect2i"

class TestGdValuePlane(_SimpleArrayBase_Float):
    _py_expected_type = GdValuePlane
    _bl_expected_key = "GdValuePlane"

class TestGdValueColor(_SimpleArrayBase_Float):
    _py_expected_type = GdValueColor
    _bl_expected_key = "GdValueColor"

class TestGdValueAABB(_SimpleArrayBase_Float):
    _py_expected_type = GdValueAABB
    _bl_expected_key = "GdValueAABB"

class TestGdValueQuaternion(_SimpleArrayBase_Float):
    _py_expected_type = GdValueQuaternion
    _bl_expected_key = "GdValueQuaternion"

class TestGdValueTransform2D(_SimpleArrayBase_Float):
    _py_expected_type = GdValueTransform2D
    _bl_expected_key = "GdValueTransform2D"

class TestGdValueBasis(_SimpleArrayBase_Float):
    _py_expected_type = GdValueBasis
    _bl_expected_key = "GdValueBasis"

class TestGdValueTransform3D(_SimpleArrayBase_Float):
    _py_expected_type = GdValueTransform3D
    _bl_expected_key = "GdValueTransform3D"

class TestGdValuePackedInt32Array(_SimpleArrayBase_Int):
    _py_expected_type = GdValuePackedInt32Array
    _bl_expected_key = "GdValuePackedInt32Array"

class TestGdValuePackedInt64Array(_SimpleArrayBase_Int):
    _py_expected_type = GdValuePackedInt64Array
    _bl_expected_key = "GdValuePackedInt64Array"

class TestGdValuePackedFloat32Array(_SimpleArrayBase_Float):
    _py_expected_type = GdValuePackedFloat32Array
    _bl_expected_key = "GdValuePackedFloat32Array"

class TestGdValuePackedFloat64Array(_SimpleArrayBase_Float):
    _py_expected_type = GdValuePackedFloat64Array
    _bl_expected_key = "GdValuePackedFloat64Array"

class TestGdValuePackedStringArray(_PackedArrayBase_String):
    _py_expected_type = GdValuePackedStringArray
    _bl_expected_key = "GdValuePackedStringArray"

class TestGdValuePackedVector2Array(_PackedArrayBase_Vector):
    _py_expected_type = GdValuePackedVector2Array
    _bl_expected_key = "GdValuePackedVector2Array"

class TestGdValuePackedVector3Array(_PackedArrayBase_Vector):
    _py_expected_type = GdValuePackedVector3Array
    _bl_expected_key = "GdValuePackedVector3Array"

class TestGdValuePackedVector4Array(_PackedArrayBase_Vector):
    _py_expected_type = GdValuePackedVector4Array
    _bl_expected_key = "GdValuePackedVector4Array"

class TestGdValuePackedColorArray(_PackedArrayBase_Vector):
    _py_expected_type = GdValuePackedColorArray
    _bl_expected_key = "GdValuePackedColorArray"



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


    