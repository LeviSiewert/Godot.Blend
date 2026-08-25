
from ...core.values import (
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

from ._test_utils import _StructureTest

class Test_NodePath(_StructureTest):
    _type = NodePath
    _parser_key = "value"
    def data(self,):
        yield 'NodePath(".")', NodePath(".")

class Test_StringName(_StructureTest):
    _type = StringName
    _parser_key = "value"
    def data(self,):
        yield '&""', StringName("")
        yield '&"A"', StringName("A")

class Test_Object(_StructureTest):
    _type = Object
    _parser_key = "value"
    def data(self):
        txt = ''' Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194309,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null) '''
        res = Object('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":4194309,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":False,"script":None})
        yield (txt, res)

        txt = ''' Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194310,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null) '''
        res = Object('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":4194310,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":False,"script":None})
        yield (txt, res)

        txt = ''' Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"location":0,"echo":false,"script":null) '''
        res = Object('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"location":0,"echo":False,"script":None})
        yield (txt, res)

        txt = ''' Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":false,"script":null) '''
        res = Object('InputEventJoypadButton',**{"resource_local_to_scene":False,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":False,"script":None})
        yield (txt, res)

class Test_Dictionary(_StructureTest):
    _type = Dictionary
    _parser_key = "value"
    def data(self,):
        yield '{}', Dictionary()
        yield 'Dictionary()', Dictionary()
        yield 'Dictionary[Variant,Variant]()', Dictionary()
        yield 'Dictionary({})', Dictionary()
        yield 'Dictionary[Variant,Variant]({})', Dictionary()
        yield 'Dictionary({"a":"b", "c":"d"})', Dictionary({"a":"b", "c":"d"})
        yield 'Dictionary[Variant,Variant]({"a":"b", "c":"d"})', Dictionary({"a":"b", "c":"d"})
        yield 'Dictionary[String,String]({"a":"b", "c":"d"})', Dictionary({"a":"b", "c":"d"}, typing=["String","String"])

class Test_Array(_StructureTest):
    _type = Array
    _parser_key = "value"
    def data(self,):
        yield '[]', Array()
        # yield 'Array()', Array()
        # yield 'Array[Variant]()', Array()
        # yield 'Array([])', Array()
        # yield 'Array[Variant]([])', Array()
        # yield 'Array(["a","b","c"])', Array("a","b","c")
        # yield 'Array[Variant](["a","b","c"])', Array("a","b","c")
        yield 'Array[String](["a","b","c"])', Array("a","b","c", typing="String")
    
class Test_Vector2i(_StructureTest):
    _type = Vector2i
    _parser_key = "value"
    def data(self,):
        # yield "Vector2i()", Vector2i()
        yield "Vector2i(0,1)", Vector2i(0,1)
class Test_Vector3i(_StructureTest):
    _type = Vector3i
    _parser_key = "value"
    def data(self,):
        # yield "Vector3i()", Vector3i()
        yield "Vector3i(0,1,2)", Vector3i(0,1,2)
class Test_Vector4i(_StructureTest):
    _type = Vector4i
    _parser_key = "value"
    def data(self,):
        # yield "Vector4i()", Vector4i()
        yield "Vector4i(0,1,2,3)", Vector4i(0,1,2,3)
class Test_Rect2i(_StructureTest):
    _type = Rect2i
    _parser_key = "value"
    def data(self,):
        # yield "Rect2i()", Rect2i()
        yield "Rect2i(0,1,2,3)", Rect2i(0,1,2,3)

class Test_Vector2(_StructureTest):
    _type = Vector2
    _parser_key = "value"
    def data(self,):
        # yield "Vector2()", Vector2()
        yield "Vector2(0,1)", Vector2(0,1)
        yield "Vector2(0.5,1.5)", Vector2(0.5,1.5)
class Test_Vector3(_StructureTest):
    _type = Vector3
    _parser_key = "value"
    def data(self,):
        # yield "Vector3()", Vector3()
        yield "Vector3(0,1,2)", Vector3(0,1,2)
        yield "Vector3(0.5,1.5,2.5)", Vector3(0.5,1.5,2.5)
class Test_Vector4(_StructureTest):
    _type = Vector4
    _parser_key = "value"
    def data(self,):
        # yield "Vector4()", Vector4()
        yield "Vector4(0,1,2,3)", Vector4(0,1,2,3)
        yield "Vector4(0.5,1.5,2.5,3.5)", Vector4(0.5,1.5,2.5,3.5)
class Test_Rect2(_StructureTest):
    _type = Rect2
    _parser_key = "value"
    def data(self,):
        # yield "Rect2()", Rect2()
        yield "Rect2(0,1,2,3)", Rect2(0,1,2,3)
        yield "Rect2(0.5,1.5,2.5,3.5)", Rect2(0.5,1.5,2.5,3.5)
class Test_Plane(_StructureTest):
    _type = Plane
    _parser_key = "value"
    def data(self,):
        # yield "Plane()", Plane()
        yield "Plane(0,1,2,3)", Plane(0,1,2,3)
        yield "Plane(0.5,1.5,2.5,3.5)", Plane(0.5,1.5,2.5,3.5)
class Test_Color(_StructureTest):
    _type = Color
    _parser_key = "value"
    def data(self,):
        # yield "Color()", Color()
        yield "Color(0,1,2,3)", Color(0,1,2,3)
        yield "Color(0.5,1.5,2.5,3.5)", Color(0.5,1.5,2.5,3.5)
class Test_AABB(_StructureTest):
    _type = AABB
    _parser_key = "value"
    def data(self,):
        # yield "AABB()", AABB()
        yield "AABB(1,2,3,4,5,6)", AABB(1,2,3,4,5,6)
        yield "AABB(1.5,2.5,3.5,4.5,5.5,6.5)", AABB(1.5,2.5,3.5,4.5,5.5,6.5)
        # yield "AABB(1.0,2.0,3.0,4.0,5.0,6.0)", AABB(1.0,2.0,3.0,4.0,5.0,6.0)
class Test_Quaternion(_StructureTest):
    _type = Quaternion
    _parser_key = "value"
    def data(self,):
        # yield "Quaternion()", Quaternion()
        yield "Quaternion(0,1,2,3)", Quaternion(0,1,2,3)
        yield "Quaternion(0.5,1.5,2.5,3.5)", Quaternion(0.5,1.5,2.5,3.5)
        # yield "Quaternion(0.0,1.0,2.0,3.0)", Quaternion(0.0,1.0,2.0,3.0)
class Test_Transform2D(_StructureTest):
    _type = Transform2D
    _parser_key = "value"
    def data(self,):
        # yield "Transform2D()", Transform2D()
        yield "Transform2D(0,1,2,3,4,5)", Transform2D(0,1,2,3,4,5)
        yield "Transform2D(0.5,1.5,2.5,3.5,4.5,5.5)", Transform2D(0.5,1.5,2.5,3.5,4.5,5.5)
        # yield "Transform2D(0.0,1.0,2.0,3.0,4.0,5.0)", Transform2D(0.0,1.0,2.0,3.0,4.0,5.0)
class Test_Transform3D(_StructureTest):
    _type = Transform3D
    _parser_key = "value"
    def data(self,):
        # yield "Transform3D()", Transform3D()
        yield "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)", Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)
        yield "Transform3D(0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5)", Transform3D(0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5)
        # yield "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0)", Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0)
class Test_Basis(_StructureTest):
    _type = Basis
    _parser_key = "value"
    def data(self,):
        # yield "Basis()", Basis()
        yield "Basis(0,1,2,3,4,5,6,7,8)", Basis(0,1,2,3,4,5,6,7,8)
        yield "Basis(0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5)", Basis(0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5)
        # yield "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0)", Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0)

class Test_PackedInt32Array(_StructureTest):
    _type = PackedInt32Array
    _parser_key = "value"
    def data(self,):
        yield "PackedInt32Array()", PackedInt32Array()
        yield "PackedInt32Array(0,1,2,3,4)", PackedInt32Array(0,1,2,3,4)
class Test_PackedInt64Array(_StructureTest):
    _type = PackedInt64Array
    _parser_key = "value"
    def data(self,):
        yield "PackedInt64Array()", PackedInt64Array()
        yield "PackedInt64Array(0,1,2,3,4)", PackedInt64Array(0,1,2,3,4) 
    
class Test_PackedFloat32Array(_StructureTest):
    _type = PackedFloat32Array
    _parser_key = "value"
    def data(self,):
        yield "PackedFloat32Array()",PackedFloat32Array()
        yield "PackedFloat32Array(0,1,2,3,4)",PackedFloat32Array(0,1,2,3,4)
        yield "PackedFloat32Array(0,1.5,2.5,3.5,4.5)",PackedFloat32Array(0,1.5,2.5,3.5,4.5)
class Test_PackedFloat64Array(_StructureTest):
    _type = PackedFloat64Array
    _parser_key = "value"
    def data(self,):
        yield "PackedFloat64Array()", PackedFloat64Array()
        yield "PackedFloat64Array(0,1,2,3,4)", PackedFloat64Array(0,1,2,3,4)
        yield "PackedFloat64Array(0,1.5,2.5,3.5,4.5)", PackedFloat64Array(0,1.5,2.5,3.5,4.5)
    
class Test_PackedStringArray(_StructureTest):
    _type = PackedStringArray
    _parser_key = "value"
    def data(self,):
        yield 'PackedStringArray()', PackedStringArray()
        yield 'PackedStringArray("a","b")', PackedStringArray("a","b")

class Test_PackedVector2Array(_StructureTest):
    _type = PackedVector2Array
    _parser_key = "value"
    def data(self,):
         yield "PackedVector2Array(0,1)", PackedVector2Array(0,1)
         yield "PackedVector2Array(0,1)", PackedVector2Array(Vector2(0,1))
         yield "PackedVector2Array(0,1,0,1)", PackedVector2Array(0,1,0,1)
         yield "PackedVector2Array(0,1,0,1)", PackedVector2Array(Vector2(0,1),Vector2(0,1))
         yield "PackedVector2Array(0,1,0,1)", PackedVector2Array(Vector2(0,1),*(0,1))
class Test_PackedVector3Array(_StructureTest):
    _type = PackedVector3Array
    _parser_key = "value"
    def data(self,):
        yield "PackedVector3Array(0,1,2)", PackedVector3Array(0,1,2)
        yield "PackedVector3Array(0,1,2)", PackedVector3Array(Vector3(0,1,2))
        yield "PackedVector3Array(0,1,2,0,1,2)", PackedVector3Array(0,1,2,0,1,2)
        yield "PackedVector3Array(0,1,2,0,1,2)", PackedVector3Array(Vector3(0,1,2),Vector3(0,1,2))
        yield "PackedVector3Array(0,1,2,0,1,2)", PackedVector3Array(Vector3(0,1,2),*(0,1,2))
class Test_PackedVector4Array(_StructureTest):
    _type = PackedVector4Array
    _parser_key = "value"
    def data(self,):
        yield "PackedVector4Array(0,1,2,3)", PackedVector4Array(0,1,2,3)
        yield "PackedVector4Array(0,1,2,3)", PackedVector4Array(Vector4(0,1,2,3))
        yield "PackedVector4Array(0,1,2,3,0,1,2,3)", PackedVector4Array(0,1,2,3,0,1,2,3)
        yield "PackedVector4Array(0,1,2,3,0,1,2,3)", PackedVector4Array(Vector4(0,1,2,3),Vector4(0,1,2,3))
        yield "PackedVector4Array(0,1,2,3,0,1,2,3)", PackedVector4Array(Vector4(0,1,2,3),*(0,1,2,3))
class Test_PackedColorArray(_StructureTest):
    _type = PackedColorArray
    _parser_key = "value"
    def data(self,):
        yield "PackedColorArray(0,1,2,3)", PackedColorArray(0,1,2,3)
        yield "PackedColorArray(0,1,2,3)", PackedColorArray(Color(0,1,2,3))
        yield "PackedColorArray(0,1,2,3,0,1,2,3)", PackedColorArray(0,1,2,3,0,1,2,3)
        yield "PackedColorArray(0,1,2,3,0,1,2,3)", PackedColorArray(Color(0,1,2,3),Color(0,1,2,3))
        yield "PackedColorArray(0,1,2,3,0,1,2,3)", PackedColorArray(Color(0,1,2,3),*(0,1,2,3))
    
class Test_PackedByteArray(_StructureTest):
    _type = PackedByteArray
    _parser_key = "value"
    def data(self,):
        yield 'PackedByteArray("")', PackedByteArray(b"")
        yield 'PackedByteArray("abc123")', PackedByteArray(b"abc123")