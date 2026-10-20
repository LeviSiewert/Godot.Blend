from .properties import *

from ._test_utils import addon_ensure

class _Base():
    attach = ["test_attr", bpy.types.Scene]
    struct = Properties

    @property
    def value(self)->Properties:
        return getattr(bpy.data.scenes[0], self.attach[0])

    def setup_class(self):
        addon_ensure(True)
        setattr(self.attach[1], self.attach[0], PointerProperty(type=self.struct))

    def teardown_class(self):
        getattr(bpy.data.scenes[0], self.attach[0]).clear()
        delattr(self.attach[1], self.attach[0])
        addon_ensure(False)

from ..GdPy.transformers.gd_to_py.values_test import (
    Test_Options as _T_Options,
    Test_NodePath as _T_NodePath,
    Test_StringName as _T_StringName,
    Test_Object as _T_Object,
    Test_Dictionary as _T_Dictionary,
#   Test_Explicit as _T_Explicit,
#   Test_Implicit as _T_Implicit,
    Test_Array as _T_Array,
#   Test_Explicit as _T_Explicit,
#   Test_Implicit as _T_Implicit,
    Test_Vector2i as _T_Vector2i,
    Test_Vector3i as _T_Vector3i,
    Test_Vector4i as _T_Vector4i,
    Test_Rect2i as _T_Rect2i,
    Test_Vector2 as _T_Vector2,
    Test_Vector3 as _T_Vector3,
    Test_Vector4 as _T_Vector4,
    Test_Rect2 as _T_Rect2,
    Test_Plane as _T_Plane,
    Test_Color as _T_Color,
    Test_AABB as _T_AABB,
    Test_Quaternion as _T_Quaternion,
    Test_Transform2D as _T_Transform2D,
    Test_Transform3D as _T_Transform3D,
    Test_Basis as _T_Basis,
    Test_PackedInt32Array as _T_PackedInt32Array,
    Test_PackedInt64Array as _T_PackedInt64Array,
    Test_PackedFloat32Array as _T_PackedFloat32Array,
    Test_PackedFloat64Array as _T_PackedFloat64Array,
    Test_PackedStringArray as _T_PackedStringArray,
    Test_PackedVector2Array as _T_PackedVector2Array,
    Test_PackedVector3Array as _T_PackedVector3Array,
    Test_PackedVector4Array as _T_PackedVector4Array,
    Test_PackedColorArray as _T_PackedColorArray,
    Test_PackedByteArray as _T_PackedByteArray,
)

class TestBasics(_Base):
    def test_stringval(self):
        assert len(self.value.data) == 0
        assert len(self.value.bin_string.data) == 0

        self.value.set("a", "value")

        assert len(self.value.data) == 1
        assert len(self.value.bin_string.data) == 1

        assert "value" == self.value.get("a").value

        self.value.clear()

        assert len(self.value.data) == 0
        assert len(self.value.bin_string.data) == 0

    def data_simple(self):
        properties = self.value
        def values(cls, bin, key:str="key"):
            for _, val in cls().data(None):
                yield bin, key, val


        yield properties.bin_string, "key", "value"

        yield properties.bin_int, "key", 0
        yield properties.bin_int, "key", 1

        yield properties.bin_float, "key", 0.5
        yield properties.bin_float, "key", 1.5

        yield from values(_T_NodePath, properties.bin_string)
        yield from values(_T_StringName, properties.bin_string)

    def data_vector(self):
        properties = self.value
        def values(cls, bin, key:str="key"):
            for _, val in cls().data(None):
                yield bin, key, val
        yield from values(_T_Vector2i, properties.bin_vector)
        yield from values(_T_Vector3i, properties.bin_vector)
        yield from values(_T_Vector4i, properties.bin_vector)
        yield from values(_T_Rect2i, properties.bin_vector)
        yield from values(_T_Vector2, properties.bin_vector)
        yield from values(_T_Vector3, properties.bin_vector)
        yield from values(_T_Vector4, properties.bin_vector)
        yield from values(_T_Rect2, properties.bin_vector)
        yield from values(_T_Plane, properties.bin_vector)
        yield from values(_T_Color, properties.bin_vector)
        yield from values(_T_AABB, properties.bin_vector)
        yield from values(_T_Quaternion, properties.bin_vector)
        yield from values(_T_Transform2D, properties.bin_vector)
        yield from values(_T_Transform3D, properties.bin_vector)
        yield from values(_T_Basis, properties.bin_vector)

    def data_packedarray(self):
        properties = self.value
        def values(cls, bin, key:str="key"):
            for _, val in cls().data(None):
                yield bin, key, val
        yield from values(_T_PackedInt32Array, properties.bin_array)
        yield from values(_T_PackedInt64Array, properties.bin_array)
        yield from values(_T_PackedFloat32Array, properties.bin_array)
        yield from values(_T_PackedFloat64Array, properties.bin_array)
        yield from values(_T_PackedStringArray, properties.bin_array)
        yield from values(_T_PackedVector2Array, properties.bin_array)
        yield from values(_T_PackedVector3Array, properties.bin_array)
        yield from values(_T_PackedVector4Array, properties.bin_array)
        yield from values(_T_PackedColorArray, properties.bin_array)

        yield from values(_T_PackedByteArray, properties.bin_binary)

    def data_dict(self):
        properties = self.value
        def values(cls, bin, key:str="key"):
            for _, val in cls().data(None):
                yield bin, key, val

        yield from values(_T_Object, properties.bin_dict)
        yield from values(_T_Dictionary.Test_Explicit, properties.bin_dict)
        yield from values(_T_Dictionary.Test_Implicit, properties.bin_dict)

    def data_array(self):
        properties = self.value
        def values(cls, bin, key:str="key"):
            for _, val in cls().data(None):
                yield bin, key, val
        yield from values(_T_Array.Test_Explicit, properties.bin_array)
        yield from values(_T_Array.Test_Implicit, properties.bin_array)

    def unit(self, _bin, _key, _val):
        properties = self.value
        properties.clear()
        
        assert len(properties.data) == 0
        assert len(_bin.data) == 0

        v = properties.set(_key, _val, wrap=True)

        assert v.name != _key # As is pointer
        assert v.value == _val

        assert properties.get(_key, wrap=False) == v

        # if hasattr(_val,"typing"):
        #     assert (v.typing == _val.typing) #String based typing for now

        assert len(properties.data) >= 1
        assert len(_bin.data) >= 1

        properties.remove(_key)

        assert len(properties.data) == 0
        assert len(_bin.data) == 0

    def test_simple_store_delete(self):
        ''' Extrensics in storage of structure. '''
        for _bin, _key, _val in self.data_simple():
            self.unit(_bin,_key,_val)
    def test_vector_store_delete(self):
        ''' Extrensics in storage of structure. '''
        for _bin, _key, _val in self.data_vector():
            self.unit(_bin,_key,_val)
    def test_packedarray_store_delete(self):
        ''' Extrensics in storage of structure. '''
        for _bin, _key, _val in self.data_packedarray():
            self.unit(_bin,_key,_val)
    def test_dict_store_delete(self):
        ''' Extrensics in storage of structure. '''
        for _bin, _key, _val in self.data_dict():
            self.unit(_bin,_key,_val)
    def test_array_store_delete(self):
        ''' Extrensics in storage of structure. '''
        for _bin, _key, _val in self.data_array():
            self.unit(_bin,_key,_val)
    
    def test_dict_deep(self):
        properties = self.value
        properties.clear()
        
        wrapped = properties.set("dictionary", {"key":"value", "otherkey":"value"}, wrap = True)

        assert wrapped._properties == properties
        
        assert len(properties.bin_dict.data) == 1
        assert len(properties.bin_dict.data[0].data) == 2

        assert len(properties.bin_string.data) == 4
        assert properties.bin_string.data[0].value in ["key","value","otherkey"]
        assert properties.bin_string.data[1].value in ["key","value","otherkey"]
        assert properties.bin_string.data[2].value in ["key","value","otherkey"]
        assert properties.bin_string.data[3].value in ["key","value","otherkey"]
        
        assert wrapped.get("key").value == "value"
        assert wrapped.get("otherkey").value == "value"

        wrapped.set("key", "val2")
        assert len(properties.bin_string.data) == 4

        wrapped.remove("key")
        assert len(properties.bin_string.data) == 2

        wrapped.set("key1", "val2")
        assert len(properties.bin_string.data) == 4

        wrapped.clear()
        assert len(properties.bin_string.data) == 0

        properties.remove("dictionary")

        assert len(properties.bin_string.data) == 0

    def test_array_deep(self):
        properties = self.value
        properties.clear()
        
        wrapped = properties.set("array", ["a","b","a","c"], wrap = True)        
        assert len(properties.bin_array.data) == 1
        assert len(properties.bin_string.data) == 4

        wrapped.append("d")
        assert len(properties.bin_string.data) == 5

        wrapped.remove(-1)
        assert wrapped.get_index(4, default=None) is None
        assert len(properties.bin_string.data) == 4

        wrapped.clear()
        assert len(properties.bin_string.data) == 0

