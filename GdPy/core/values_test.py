from .values import (
    NodePath,
    StringName,
    Object,
    Dictionary,
    Array,
    Vector2i,
    Vector3i,
    Vector4i,
    Rect2i,
    Vector2,
    Vector3,
    Vector4,
    Rect2,
    Plane,
    Color,
    AABB,
    Quaternion,
    Transform2D,
    Transform3D,
    Basis,
    PackedInt32Array,
    PackedInt64Array,
    PackedFloat32Array,
    PackedFloat64Array,
    PackedStringArray,
    PackedVector2Array,
    PackedVector3Array,
    PackedVector4Array,
    PackedColorArray,
    PackedByteArray,
)


class Test_NodePath():
    def test_construction(s):
        r = NodePath(".")


class Test_StringName():
    def test_construction(s):
        assert ""  == StringName("")
        assert "A" == StringName("A")


class Test_Object():
    def test_construction(s):
        Object('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":4194309,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":False,"script":None})
        Object('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":4194310,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":False,"script":None})
        Object('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"location":0,"echo":False,"script":None})
        Object('InputEventJoypadButton',**{"resource_local_to_scene":False,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":False,"script":None})

class Test_Dictionary():
    def test_construction(s):
        assert {} == Dictionary()
        assert {"a":"b", "c":"d"} == Dictionary({"a":"b", "c":"d"})
        assert {"a":"b", "c":"d"} == Dictionary({"a":"b", "c":"d"}, typing=["String","String"])

class Test_Array():
    def test_construction(s):
        assert [] == Array()
        assert ["a","b","c"] == Array("a","b","c", typing="String")

class Test_Vector2i():
    def test_construction(s):
        assert (0,1) == Vector2i(0,1)

class Test_Vector3i():
    def test_construction(s):
        assert (0,1,2) == Vector3i(0,1,2)

class Test_Vector4i():
    def test_construction(s):
        assert (0,1,2,3) == Vector4i(0,1,2,3)

class Test_Rect2i():
    def test_construction(s):
        assert (0,1,2,3) == Rect2i(0,1,2,3)

class Test_Vector2():
    def test_construction(s):
        assert (0,1) == Vector2(0,1)
        assert (0.5,1.5) == Vector2(0.5,1.5)

class Test_Vector3():
    def test_construction(s):
        assert (0,1,2) == Vector3(0,1,2)
        assert (0.5,1.5,2.5) == Vector3(0.5,1.5,2.5)

class Test_Vector4():
    def test_construction(s):
        assert (0,1,2,3) == Vector4(0,1,2,3)
        assert (0.5,1.5,2.5,3.5) == Vector4(0.5,1.5,2.5,3.5)

class Test_Rect2():
    def test_construction(s):
        assert (0,1,2,3) == Rect2(0,1,2,3)
        assert (0.5,1.5,2.5,3.5) == Rect2(0.5,1.5,2.5,3.5)

class Test_Plane():
    def test_construction(s):
        assert (0,1,2,3) == Plane(0,1,2,3)
        assert (0.5,1.5,2.5,3.5) == Plane(0.5,1.5,2.5,3.5)

class Test_Color():
    def test_construction(s):
        assert (0,1,2,3) == Color(0,1,2,3)
        assert (0.5,1.5,2.5,3.5) == Color(0.5,1.5,2.5,3.5)

class Test_AABB():
    def test_construction(s):
        assert (1,2,3,4,5,6) == AABB(1,2,3,4,5,6)
        assert (1.5,2.5,3.5,4.5,5.5,6.5) == AABB(1.5,2.5,3.5,4.5,5.5,6.5)

class Test_Quaternion():
    def test_construction(s):
        assert (0,1,2,3) == Quaternion(0,1,2,3)
        assert (0.5,1.5,2.5,3.5) == Quaternion(0.5,1.5,2.5,3.5)

class Test_Transform2D():
    def test_construction(s):
        assert (0,1,2,3,4,5) == Transform2D(0,1,2,3,4,5)
        assert (0.5,1.5,2.5,3.5,4.5,5.5) == Transform2D(0.5,1.5,2.5,3.5,4.5,5.5)

class Test_Transform3D():
    def test_construction(s):
        assert (0,1,2,3,4,5,6,7,8,9,10,11) == Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)
        assert (0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5) == Transform3D(0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5)

class Test_Basis():
    def test_construction(s):
        assert (0,1,2,3,4,5,6,7,8) == Basis(0,1,2,3,4,5,6,7,8)
        assert (0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5) == Basis(0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5)

class Test_PackedInt32Array():
    def test_construction(s):
        assert tuple() == PackedInt32Array()
        assert (0,1,2,3,4) == PackedInt32Array(0,1,2,3,4)

class Test_PackedInt64Array():
    def test_construction(s):
        assert tuple() == PackedInt64Array()
        assert (0,1,2,3,4)  == PackedInt64Array(0,1,2,3,4) 

class Test_PackedFloat32Array():
    def test_construction(s):
        assert tuple() == PackedFloat32Array()
        assert (0,1,2,3,4) == PackedFloat32Array(0,1,2,3,4)
        assert (0,1.5,2.5,3.5,4.5) == PackedFloat32Array(0,1.5,2.5,3.5,4.5)

class Test_PackedFloat64Array():
    def test_construction(s):
        assert tuple() == PackedFloat64Array()
        assert (0,1,2,3,4) == PackedFloat64Array(0,1,2,3,4)
        assert (0,1.5,2.5,3.5,4.5) == PackedFloat64Array(0,1.5,2.5,3.5,4.5)

class Test_PackedStringArray():
    def test_construction(s):
        assert tuple() == PackedStringArray()
        assert ("a","b") == PackedStringArray("a","b")

class Test_PackedVector2Array():
    def test_construction(s):
        assert tuple() == PackedVector2Array()
        assert ([0,1],) == PackedVector2Array(0,1)
        assert ([0,1],) == PackedVector2Array(Vector2(0,1))
        assert ([0,1],[0,1]) == PackedVector2Array(0,1,0,1)
        assert ([0,1],[0,1]) == PackedVector2Array(Vector2(0,1),Vector2(0,1))
        assert ([0,1],[0,1]) == PackedVector2Array(Vector2(0,1),*(0,1))

class Test_PackedVector3Array():
    def test_construction(s):
        assert tuple() == PackedVector3Array()
        assert ([0,1,2],) == PackedVector3Array(0,1,2)
        assert ([0,1,2],) == PackedVector3Array(Vector3(0,1,2))
        assert ([0,1,2],[0,1,2]) == PackedVector3Array(0,1,2,0,1,2)
        assert ([0,1,2],[0,1,2]) == PackedVector3Array(Vector3(0,1,2),Vector3(0,1,2))
        assert ([0,1,2],[0,1,2]) == PackedVector3Array(Vector3(0,1,2),*(0,1,2))

class Test_PackedVector4Array():
    def test_construction(s):
        assert tuple() == PackedVector4Array()
        assert ([0,1,2,3],) == PackedVector4Array(0,1,2,3)
        assert ([0,1,2,3],) == PackedVector4Array(Vector4(0,1,2,3))
        assert ([0,1,2,3],[0,1,2,3]) == PackedVector4Array(0,1,2,3,0,1,2,3)
        assert ([0,1,2,3],[0,1,2,3]) == PackedVector4Array(Vector4(0,1,2,3),Vector4(0,1,2,3))
        assert ([0,1,2,3],[0,1,2,3]) == PackedVector4Array(Vector4(0,1,2,3),*(0,1,2,3))

class Test_PackedColorArray():
    def test_construction(s):
        assert ([0,1,2,3],) == PackedColorArray(0,1,2,3)
        assert ([0,1,2,3],) == PackedColorArray(Color(0,1,2,3))
        assert ([0,1,2,3],[0,1,2,3]) == PackedColorArray(0,1,2,3,0,1,2,3)
        assert ([0,1,2,3],[0,1,2,3]) == PackedColorArray(Color(0,1,2,3),Color(0,1,2,3))
        assert ([0,1,2,3],[0,1,2,3]) == PackedColorArray(Color(0,1,2,3),*(0,1,2,3))

class Test_PackedByteArray():
    def test_construction(s):
        assert b"" == PackedByteArray(b"")
        assert b"abc123" == PackedByteArray(b"abc123")