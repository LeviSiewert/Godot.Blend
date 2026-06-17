# from pytest import fixture

from ..structure.values import *
from ..structure.references import *
from ..structure.core.primitives import Context

from ..structure._standard_parser import construct_keyed_parser
gdparser = construct_keyed_parser("value")

c = Context()
def _parse(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)
def _render(object):
    return gdparser.render(c,object)

class TestGdValueResourceID():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "rid"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "RID()"), GdValueResourceID)) 
        # assert(_parse("value", "RID()") == GdValueResourceID())
        # assert(_parse("value", 'RID("")') == GdValueResourceID())
    # def test_rendering(self,):
    #     assert(_render(GdValueResourceID()) == "RID()")

class TestGdValueExtResource():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "extresource"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", 'ExtResource()'), GdValueExtResource))
        assert(isinstance(_parse("value", 'ExtResource("")'), GdValueExtResource))
        # assert(_parse("value", 'ExtResource()') == GdValueExtResource())
        # assert(_parse("value", 'ExtResource("")') == GdValueExtResource())

class TestGdValueNodePath():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "nodepath"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", 'NodePath()'), GdValueNodePath))
        assert(isinstance(_parse("value", 'NodePath("")'), GdValueNodePath))
        # assert(_parse("value", 'NodePath()') == GdValueNodePath())
        # assert(_parse("value", 'NodePath("")') == GdValueNodePath())

class TestGdValueSubResource():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "subresource"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", 'SubResource()'), GdValueSubResource))
        assert(isinstance(_parse("value", 'SubResource("")'), GdValueSubResource))
        # assert(_parse("value", 'SubResource()') == GdValueSubResource())
        # assert(_parse("value", 'SubResource("")') == GdValueSubResource())
    
class TestGdValueStringName():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "stringname"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", '&"value"'), GdValueStringName))
        assert (_parse("value", '&"value"') == GdValueStringName('value'))
        # assert(_parse("value", '&"va) ==e()"') GdValueStringName))
    def test_rendering(self,):
        assert(_render(GdValueResourceID()) == "RID()")

class TestGdValueDictionary():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "dictionary"))
    def test_parsing(self,):
        assert(gdparser._parser_transformer.matcher(None, "dictionary_explicit"))
        assert(isinstance(_parse("value", "{}"), GdValueDictionary))
        # assert(_parse("value", "{}"), GdValueDiction) ==y())
        assert(isinstance(_parse("value", "Dictionary()"), GdValueDictionary))
        assert(_parse("value", "Dictionary()") == GdValueDictionary())
        assert(isinstance(_parse("value", "Dictionary[Variant,Variant]()"), GdValueDictionary))
        # assert(_parse("value", "Dictionary[Varia) ==,Variant()]()") GdValueDictionary))

class TestGdValueArray():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Array[Variant]()"), GdValueArray))
        # assert(_parse("value", "Array[Vari) ==t()]()") GdValueArray))
        assert(isinstance(_parse("value", "Array()"), GdValueArray))
        assert(_parse("value", "Array()") == GdValueArray())
        assert(isinstance(_parse("value", "[]"), GdValueArray))
        # assert(_parse("value", "[]"), GdValueAr) ==y())

class TestGdValueVector2():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "vector2"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Vector2()"), GdValueVector2))
        assert(isinstance(_parse("value", "Vector2(0,1)"), GdValueVector2))
        assert(isinstance(_parse("value", "Vector2(0.0,1.0)"), GdValueVector2))
        assert(_parse("value", "Vector2()") == GdValueVector2())
        assert(_parse("value", "Vector2(0,1)") == _parse("value", "Vector2(0.0,1.0)"))
        assert(_parse("value", "Vector2(0,1)") == GdValueVector2((0,1)))

class TestGdValueVector3():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "vector3"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Vector3()"), GdValueVector3))
        assert(isinstance(_parse("value", "Vector3(0,1,2)"), GdValueVector3))
        assert(isinstance(_parse("value", "Vector3(0.0,1.0,2.0)"), GdValueVector3))
        assert(_parse("value", "Vector3()") == GdValueVector3())
        assert(_parse("value", "Vector3(0,1,2)") == _parse("value", "Vector3(0.0,1.0,2.0)"))
        assert(_parse("value", "Vector3(0,1,2)") == GdValueVector3((0,1,2)))

class TestGdValueVector4():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "vector4"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Vector4()"), GdValueVector4))
        assert(isinstance(_parse("value", "Vector4(0,1,2,3)"), GdValueVector4))
        assert(isinstance(_parse("value", "Vector4(0.0,1.0,2.0,3.0)"), GdValueVector4))
        assert(_parse("value", "Vector4()") == GdValueVector4())
        assert(_parse("value", "Vector4(0,1,2,3)") == _parse("value", "Vector4(0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "Vector4(0,1,2,3)") == GdValueVector4((0,1,2,3)))

class TestGdValueVector2i():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "vector2i"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Vector2i()"), GdValueVector2i))
        assert(isinstance(_parse("value", "Vector2i(0,1)"), GdValueVector2i))
        assert(_parse("value", "Vector2i()") == GdValueVector2i())
        assert(_parse("value", "Vector2i(0,1)") == GdValueVector2i((0,1)))

class TestGdValueVector3i():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "vector3i"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Vector3i()"), GdValueVector3i))
        assert(isinstance(_parse("value", "Vector3i(0,1,2)"), GdValueVector3i))
        assert(_parse("value", "Vector3i()") == GdValueVector3i())
        assert(_parse("value", "Vector3i(0,1,2)") == GdValueVector3i((0,1,2)))

class TestGdValueVector4i():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "vector4i"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Vector4i()"), GdValueVector4i))
        assert(isinstance(_parse("value", "Vector4i(0,1,2,3)"), GdValueVector4i))
        assert(_parse("value", "Vector4i()") == GdValueVector4i())
        assert(_parse("value", "Vector4i(0,1,2,3)") == GdValueVector4i((0,1,2,3)))


class TestGdValueRect2():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "rect2"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Rect2()"), GdValueRect2))
        assert(isinstance(_parse("value", "Rect2(0,1,2,3)"), GdValueRect2))
        assert(isinstance(_parse("value", "Rect2(0.0,1.0,2.0,3.0)"), GdValueRect2))
        assert(_parse("value", "Rect2(0,1,2,3)") == _parse("value", "Rect2(0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "Rect2()") == GdValueRect2())
        assert(_parse("value", "Rect2(0,1,2,3)") == GdValueRect2((0,1,2,3)))

class TestGdValueRect2i():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "rect2i"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Rect2i()"), GdValueRect2i))
        assert(isinstance(_parse("value", "Rect2i(0,1,2,3)"), GdValueRect2i))
        assert(_parse("value", "Rect2i()") == GdValueRect2i())
        assert(_parse("value", "Rect2i(0,1,2,3)") == GdValueRect2i((0,1,2,3)))

class TestGdValuePlane():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "plane"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Plane()"), GdValuePlane))
        assert(isinstance(_parse("value", "Plane(0,1,2,3)"), GdValuePlane))
        assert(isinstance(_parse("value", "Plane(0.0,1.0,2.0,3.0)"), GdValuePlane))
        assert(_parse("value", "Plane()") == GdValuePlane())
        assert(_parse("value", "Plane(0,1,2,3)") == _parse("value", "Plane(0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "Plane(0,1,2,3)") == GdValueColor((0,1,2,3)))

class TestGdValueColor():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "color"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Color()"), GdValueColor))
        assert(isinstance(_parse("value", "Color(0,1,2,3)"), GdValueColor))
        assert(isinstance(_parse("value", "Color(0.0,1.0,2.0,3.0)"), GdValueColor))
        assert(_parse("value", "Color()") == GdValueColor())
        assert(_parse("value", "Color(0,1,2,3)") == _parse("value", "Color(0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "Color(0,1,2,3)") == GdValueColor((0,1,2,3)))

class TestGdValueAABB():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "aabb"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "AABB()"), GdValueAABB))
        assert(isinstance(_parse("value", "AABB(1,2,3,4,5,6)"), GdValueAABB))
        assert(isinstance(_parse("value", "AABB(1.0,2.0,3.0,4.0,5.0,6.0)"), GdValueAABB))
        assert(_parse("value", "AABB()") == GdValueAABB())
        assert(_parse("value", "AABB(1,2,3,4,5,6)")== _parse("value", "AABB(1.0,2.0,3.0,4.0,5.0,6.0)"))

class TestGdValueQuaternion():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "quaternion"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Quaternion()"), GdValueQuaternion))
        assert(isinstance(_parse("value", "Quaternion(0,1,2,3)"), GdValueQuaternion))
        assert(isinstance(_parse("value", "Quaternion(0.0,1.0,2.0,3.0)"), GdValueQuaternion))
        assert(_parse("value", "Quaternion()") == GdValueQuaternion())
        assert(_parse("value", "Quaternion(0,1,2,3)") == _parse("value", "Quaternion(0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "Quaternion(0,1,2,3)") == GdValueQuaternion((0,1,2,3)))

class TestGdValueBasis():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "basis"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Basis()"), GdValueBasis))
        assert(isinstance(_parse("value", "Basis(0,1,2,3,4,5,6,7,8)"), GdValueBasis))
        assert(isinstance(_parse("value", "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0)"), GdValueBasis))
        assert(_parse("value", "Basis(0,1,2,3,4,5,6,7,8)") == _parse("value", "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0)"))
        assert(_parse("value", "Basis()") == GdValueBasis())
        assert(_parse("value", "Basis(0,1,2,3,4,5,6,7,8)") == GdValueBasis((0,1,2,3,4,5,6,7,8)))

class TestGdValueTransform2D():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "transform2d"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Transform2D()"), GdValueTransform2D))
        assert(isinstance(_parse("value", "Transform2D(0,1,2,3,4,5)"), GdValueTransform2D))
        assert(isinstance(_parse("value", "Transform2D(0.0,1.0,2.0,3.0,4.0,5.0)"), GdValueTransform2D))
        assert(_parse("value", "Transform2D(0,1,2,3,4,5)") == _parse("value","Transform2D(0.0,1.0,2.0,3.0,4.0,5.0)"))
        assert(_parse("value", "Transform2D()") == GdValueTransform2D())
        assert(_parse("value", "Transform2D(0,1,2,3,4,5)") == GdValueTransform2D((0,1,2,3,4,5)))

class TestGdValueTransform3D():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "transform3d"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Transform3D()"), GdValueTransform3D))
        assert(isinstance(_parse("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)"), GdValueTransform3D))
        assert(isinstance(_parse("value", "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0)"), GdValueTransform3D))
        assert(_parse("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)") == _parse("value", "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0)"))
        assert(_parse("value", "Transform3D()") == GdValueTransform3D())
        assert(_parse("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)") == GdValueTransform3D((0,1,2,3,4,5,6,7,8,9,10,11)))

class TestGdValuePackedByteArray():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedbytearray"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedByteArray()"), GdValuePackedByteArray))
        assert(isinstance(_parse("value", 'PackedByteArray("abc123")'), GdValuePackedByteArray))
        assert(_parse("value", "PackedByteArray()") == GdValuePackedByteArray())
        assert(_parse("value", 'PackedByteArray("abc123")') == GdValuePackedByteArray(("abc123",)))

class TestGdValuePackedInt32Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedint32array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedInt32Array()"), GdValuePackedInt32Array))
        assert(isinstance(_parse("value", "PackedInt32Array(0,1,2,3)"), GdValuePackedInt32Array))
        assert(_parse("value", "PackedInt32Array()") == GdValuePackedInt32Array())
        assert(_parse("value", "PackedInt32Array(0,1,2,3,4)") == GdValuePackedInt32Array((0,1,2,3,4)))

class TestGdValuePackedInt64Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedint64array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedInt64Array()"), GdValuePackedInt64Array))
        assert(isinstance(_parse("value", "PackedInt64Array(0,1,2,3)"), GdValuePackedInt64Array))
        assert(_parse("value", "PackedInt64Array()") == GdValuePackedInt64Array())
        assert(_parse("value", "PackedInt64Array(0,1,2,3,4)") == GdValuePackedInt64Array((0,1,2,3,4)))

class TestGdValuePackedFloat32Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedfloat32array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedFloat32Array()"), GdValuePackedFloat32Array))
        assert(isinstance(_parse("value", "PackedFloat32Array(0,1,2,3,4)"), GdValuePackedFloat32Array))
        assert(isinstance(_parse("value", "PackedFloat32Array(0.0,1.0,2.0,3.0,4.0)"), GdValuePackedFloat32Array))
        assert(_parse("value", "PackedFloat32Array()") == GdValuePackedFloat32Array())
        assert(_parse("value", "PackedFloat32Array(0,1,2,3,4)") == _parse("value", "PackedFloat32Array(0.0,1.0,2.0,3.0,4.0)"))
        assert(_parse("value", "PackedFloat32Array(0,1,2,3,4)") == GdValuePackedFloat32Array((0,1,2,3,4)))
class TestGdValuePackedFloat64Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedfloat64array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedFloat64Array()"), GdValuePackedFloat64Array))
        assert(isinstance(_parse("value", "PackedFloat64Array(0,1,2,3,4)"), GdValuePackedFloat64Array))
        assert(isinstance(_parse("value", "PackedFloat64Array(0.0,1.0,2.0,3.0,4.0)"), GdValuePackedFloat64Array))
        assert(_parse("value", "PackedFloat64Array(0,1,2,3,4)") == _parse("value", "PackedFloat64Array(0.0,1.0,2.0,3.0,4.0)"))
        assert(_parse("value", "PackedFloat64Array(0,1,2,3,4)") == GdValuePackedFloat64Array((0,1,2,3,4)))
        assert(_parse("value", "PackedFloat64Array()") == GdValuePackedFloat64Array())

class TestGdValuePackedStringArray():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedstringarray"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedStringArray()"), GdValuePackedStringArray))
        assert(isinstance(_parse("value", 'PackedStringArray("a","b")'), GdValuePackedStringArray))
        assert(_parse("value", "PackedStringArray()") == GdValuePackedStringArray())
        assert(_parse("value", 'PackedStringArray("a","b")') != GdValuePackedStringArray(("ab",)))
        assert(_parse("value", 'PackedStringArray("a","b")') == GdValuePackedStringArray(("a","b")))

class TestGdValuePackedVector2Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedvector2array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedVector2Array()"), GdValuePackedVector2Array))
        assert(isinstance(_parse("value", "PackedVector2Array(0,1,2,3)"), GdValuePackedVector2Array))
        assert(isinstance(_parse("value", "PackedVector2Array(0.0,1.0,2.0,3.0)"), GdValuePackedVector2Array))
        assert(_parse("value", "PackedVector2Array(0,1,2,3)") == _parse("value", "PackedVector2Array(0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "PackedVector2Array()") == GdValuePackedVector2Array())
        assert(2 == len(GdValuePackedVector2Array((0,1,2,3))))
        assert(3 == len(GdValuePackedVector2Array((0,1,2,3,4,5))))
        assert(_parse("value", "PackedVector2Array(0,1,2,3)") == GdValuePackedVector2Array((0,1,2,3)))
        assert(_parse("value", "PackedVector2Array(0,1,2,3)") == GdValuePackedVector2Array(((0,1),(2,3))))
        assert(_parse("value", "PackedVector2Array(0,1,2,3)") == GdValuePackedVector2Array((GdValueVector2((0,1)),GdValueVector2((2,3)))))
class TestGdValuePackedVector3Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedvector3array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedVector3Array()"), GdValuePackedVector3Array))
        assert(isinstance(_parse("value", "PackedVector3Array(0,1,2,0,1,2)"), GdValuePackedVector3Array))
        assert(isinstance(_parse("value", "PackedVector3Array(0.0,1.0,2.0,0.0,1.0,2.0)"), GdValuePackedVector3Array))
        assert(_parse("value", "PackedVector3Array()") == GdValuePackedVector3Array())
        assert(_parse("value", "PackedVector3Array(0,1,2,0,1,2)") == _parse("value", "PackedVector3Array(0.0,1.0,2.0,0.0,1.0,2.0)"))
        assert(_parse("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array((0,1,2,0,1,2)))
        assert(_parse("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array(((0,1,2),(0,1,2))))
        assert(_parse("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array((GdValueVector3((0,1,2)),GdValueVector3((0,1,2)))))
class TestGdValuePackedVector4Array():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedvector4array"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedVector4Array()"), GdValuePackedVector4Array))
        assert(isinstance(_parse("value", "PackedVector4Array(0,1,2,3,0,1,2,3)"), GdValuePackedVector4Array))
        assert(isinstance(_parse("value", "PackedVector4Array(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"), GdValuePackedVector4Array))
        assert(_parse("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == _parse("value", "PackedVector4Array(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"))
        assert(_parse("value", "PackedVector4Array()") == GdValuePackedVector4Array())
        assert(_parse("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == GdValuePackedVector4Array((0,1,2,3,0,1,2,3)))
        assert(_parse("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == GdValuePackedVector4Array(((0,1,2,3),(0,1,2,3))))
        assert(_parse("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == GdValuePackedVector4Array((GdValueVector4((0,1,2,3)),GdValueVector4((0,1,2,3)))))

class TestGdValuePackedColorArray():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None,  "packedcolorarray" ))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "PackedColorArray()"), GdValuePackedColorArray))
        assert(_parse("value", "PackedColorArray()")== GdValuePackedColorArray())
        assert(isinstance(_parse("value", "PackedColorArray(0,1,2,3,0,1,2,3)"), GdValuePackedColorArray))
        assert(isinstance(_parse("value", "PackedColorArray(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"), GdValuePackedColorArray))
        assert(_parse("value", "PackedColorArray(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)") == _parse("value", "PackedColorArray(0,1,2,3,0,1,2,3)"))
        assert(_parse("value", "PackedColorArray(0,1,2,3,0,1,2,3)") == GdValuePackedColorArray((0,1,2,3,0,1,2,3)))
        assert(_parse("value", "PackedColorArray(0,1,2,3,0,1,2,3)") == GdValuePackedColorArray((GdValueColor((0,1,2,3)),GdValueColor((0,1,2,3)))))