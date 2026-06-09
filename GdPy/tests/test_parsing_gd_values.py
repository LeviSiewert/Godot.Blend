# from pytest import fixture

from ..structure.standard_parser import gdparser 
from ..structure.values import *
from ..structure.references import *
from ..structure.core.primitives import Context

c = Context()
def _run(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)

def test_GdValueResourceID():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", "RID()"), GdValueResourceID)) 
    # assert(_run("value", "RID()") == GdValueResourceID())
    # assert(_run("value", 'RID("")') == GdValueResourceID())
def test_GdValueExtResource():
    assert(hasattr(gdparser._transformer,"extresource"))
    assert(isinstance(_run("value", 'ExtResource()'), GdValueExtResource))
    assert(isinstance(_run("value", 'ExtResource("")'), GdValueExtResource))
    # assert(_run("value", 'ExtResource()') == GdValueExtResource())
    # assert(_run("value", 'ExtResource("")') == GdValueExtResource())
def test_GdValueNodePath():
    assert(hasattr(gdparser._transformer,"nodepath"))
    assert(isinstance(_run("value", 'NodePath()'), GdValueNodePath))
    assert(isinstance(_run("value", 'NodePath("")'), GdValueNodePath))
    # assert(_run("value", 'NodePath()') == GdValueNodePath())
    # assert(_run("value", 'NodePath("")') == GdValueNodePath())
def test_GdValueSubResource():
    assert(hasattr(gdparser._transformer,"subresource"))
    assert(isinstance(_run("value", 'SubResource()'), GdValueSubResource))
    assert(isinstance(_run("value", 'SubResource("")'), GdValueSubResource))
    # assert(_run("value", 'SubResource()') == GdValueSubResource())
    # assert(_run("value", 'SubResource("")') == GdValueSubResource())

    
def test_GdValueStringName():
    assert(hasattr(gdparser._transformer,"STRINGNAME"))
    assert(isinstance(_run("value", '&"value"'), GdValueStringName))
    # assert(_run("value", '&"va) ==e()"') GdValueStringName))

def test_GdValueDictionary():
    assert(hasattr(gdparser._transformer,"dictionary"))
    assert(hasattr(gdparser._transformer,"dictionary_explicit"))
    assert(isinstance(_run("value", "{}"), GdValueDictionary))
    # assert(_run("value", "{}"), GdValueDiction) ==y())
    assert(isinstance(_run("value", "Dictionary()"), GdValueDictionary))
    assert(_run("value", "Dictionary()") == GdValueDictionary())
    assert(isinstance(_run("value", "Dictionary[Variant,Variant]()"), GdValueDictionary))
    # assert(_run("value", "Dictionary[Varia) ==,Variant()]()") GdValueDictionary))
def test_GdValueArray():
    assert(hasattr(gdparser._transformer, "array"))
    assert(isinstance(_run("value", "Array[Variant]()"), GdValueArray))
    # assert(_run("value", "Array[Vari) ==t()]()") GdValueArray))
    assert(isinstance(_run("value", "Array()"), GdValueArray))
    assert(_run("value", "Array()") == GdValueArray())
    assert(isinstance(_run("value", "[]"), GdValueArray))
    # assert(_run("value", "[]"), GdValueAr) ==y())

def test_GdValueVector2():
    assert(hasattr(gdparser._transformer, "vector2"))
    assert(isinstance(_run("value", "Vector2()"), GdValueVector2))
    assert(isinstance(_run("value", "Vector2(0,1)"), GdValueVector2))
    assert(isinstance(_run("value", "Vector2(0.0,1.0)"), GdValueVector2))
    assert(_run("value", "Vector2()") == GdValueVector2())
    assert(_run("value", "Vector2(0,1)") == _run("value", "Vector2(0.0,1.0)"))
    assert(_run("value", "Vector2(0,1)") == GdValueVector2((0,1)))
def test_GdValueVector3():
    assert(hasattr(gdparser._transformer, "vector3"))
    assert(isinstance(_run("value", "Vector3()"), GdValueVector3))
    assert(isinstance(_run("value", "Vector3(0,1,2)"), GdValueVector3))
    assert(isinstance(_run("value", "Vector3(0.0,1.0,2.0)"), GdValueVector3))
    assert(_run("value", "Vector3()") == GdValueVector3())
    assert(_run("value", "Vector3(0,1,2)") == _run("value", "Vector3(0.0,1.0,2.0)"))
    assert(_run("value", "Vector3(0,1,2)") == GdValueVector3((0,1,2)))
def test_GdValueVector4():
    assert(hasattr(gdparser._transformer, "vector4"))
    assert(isinstance(_run("value", "Vector4()"), GdValueVector4))
    assert(isinstance(_run("value", "Vector4(0,1,2)"), GdValueVector4))
    assert(isinstance(_run("value", "Vector4(0.0,1.0,2.0)"), GdValueVector4))
    assert(_run("value", "Vector4()") == GdValueVector4())
    assert(_run("value", "Vector4(0,1,2,3)") == _run("value", "Vector4(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Vector4(0,1,2,3)") == GdValueVector4((0,1,2,3)))


def test_GdValueVector2i():
    assert(hasattr(gdparser._transformer, "vector2i"))
    assert(isinstance(_run("value", "Vector2i()"), GdValueVector2i))
    assert(isinstance(_run("value", "Vector2i(0,1)"), GdValueVector2i))
    assert(_run("value", "Vector2i()") == GdValueVector2i())
    assert(_run("value", "Vector2i(0,1)") == GdValueVector2i((0,1)))
def test_GdValueVector3i():
    assert(hasattr(gdparser._transformer, "vector3i"))
    assert(isinstance(_run("value", "Vector3i()"), GdValueVector3i))
    assert(isinstance(_run("value", "Vector3i(0,1,2)"), GdValueVector3i))
    assert(_run("value", "Vector3i()") == GdValueVector3i())
    assert(_run("value", "Vector3i(0,1,2)") == GdValueVector3i((0,1,2)))
def test_GdValueVector4i():
    assert(hasattr(gdparser._transformer, "vector4i"))
    assert(isinstance(_run("value", "Vector4i()"), GdValueVector4i))
    assert(isinstance(_run("value", "Vector4i(0,1,2,3)"), GdValueVector4i))
    assert(_run("value", "Vector4i()") == GdValueVector4i())
    assert(_run("value", "Vector4i(0,1,2,3)") == GdValueVector4i((0,1,2,3)))


def test_GdValueRect2():
    assert(hasattr(gdparser._transformer, "rect2"))
    assert(isinstance(_run("value", "Rect2()"), GdValueRect2))
    assert(isinstance(_run("value", "Rect2(0,1,2,3)"), GdValueRect2))
    assert(isinstance(_run("value", "Rect2(0.0,1.0,2.0,3.0)"), GdValueRect2))
    assert(_run("value", "Rect2(0,1,2,3)") == _run("value", "Rect2(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Rect2()") == GdValueRect2())
    assert(_run("value", "Rect2(0,1,2,3)") == GdValueRect2((0,1,2,3)))
def test_GdValueRect2i():
    assert(hasattr(gdparser._transformer, "rect2i"))
    assert(isinstance(_run("value", "Rect2i()"), GdValueRect2i))
    assert(isinstance(_run("value", "Rect2i(0,1,2,3)"), GdValueRect2i))
    assert(_run("value", "Rect2i()") == GdValueRect2i())
    assert(_run("value", "Rect2i(0,1,2,3)") == GdValueRect2i((0,1,2,3)))

def test_GdValuePlane():
    assert(hasattr(gdparser._transformer, "plane"))
    assert(isinstance(_run("value", "Plane()"), GdValuePlane))
    assert(isinstance(_run("value", "Plane(0,1,2,3)"), GdValuePlane))
    assert(isinstance(_run("value", "Plane(0.0,1.0,2.0,3.0)"), GdValuePlane))
    assert(_run("value", "Plane()") == GdValuePlane())
    assert(_run("value", "Plane(0,1,2,3)") == _run("value", "Plane(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Plane(0,1,2,3)") == GdValueColor((0,1,2,3)))
def test_GdValueColor():
    assert(hasattr(gdparser._transformer, "color"))
    assert(isinstance(_run("value", "Color()"), GdValueColor))
    assert(isinstance(_run("value", "Color(0,1,2,3)"), GdValueColor))
    assert(isinstance(_run("value", "Color(0.0,1.0,2.0,3.0)"), GdValueColor))
    assert(_run("value", "Color()") == GdValueColor())
    assert(_run("value", "Color(0,1,2,3)") == _run("value", "Color(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Color(0,1,2,3)") == GdValueColor((0,1,2,3)))

def test_GdValueAABB():
    assert(hasattr(gdparser._transformer, "aabb"))
    assert(isinstance(_run("value", "AABB()"), GdValueAABB))
    assert(isinstance(_run("value", "AABB(1,2,3,4,5,6)"), GdValueAABB))
    assert(isinstance(_run("value", "AABB(1.0,2.0,3.0,4.0,5.0,6.0)"), GdValueAABB))
    assert(_run("value", "AABB()") == GdValueAABB())
    assert(_run("value", "AABB(1,2,3,4,5,6)")== _run("value", "AABB(1.0,2.0,3.0,4.0,5.0,6.0)"))

def test_GdValueQuaternion():
    assert(hasattr(gdparser._transformer, "quaternion"))
    assert(isinstance(_run("value", "Quaternion()"), GdValueQuaternion))
    assert(isinstance(_run("value", "Quaternion(0,1,2,3)"), GdValueQuaternion))
    assert(isinstance(_run("value", "Quaternion(0.0,1.0,2.0,3.0)"), GdValueQuaternion))
    assert(_run("value", "Quaternion()") == GdValueQuaternion())
    assert(_run("value", "Quaternion(0,1,2,3)") == _run("value", "Quaternion(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Quaternion(0,1,2,3)") == GdValueQuaternion((0,1,2,3)))

def test_GdValueBasis():
    assert(hasattr(gdparser._transformer, "basis"))
    assert(isinstance(_run("value", "Basis()"), GdValueBasis))
    assert(isinstance(_run("value", "Basis(0,1,2,3,4,5,6,7)"), GdValueBasis))
    assert(isinstance(_run("value", "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0)"), GdValueBasis))
    assert(_run("value", "Basis(0,1,2,3,4,5,6,7)") == _run("value", "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0)"))
    assert(_run("value", "Basis()") == GdValueBasis())
    assert(_run("value", "Basis(0,1,2,3,4,5,6,7)") == GdValueBasis((0,1,2,3,4,5,6,7)))

def test_GdValueTransform2D():
    assert(hasattr(gdparser._transformer, "transform2d"))
    assert(isinstance(_run("value", "Transform2D()"), GdValueTransform2D))
    assert(isinstance(_run("value", "Transform2D(0,1,2,3,4,5,6)"), GdValueTransform2D))
    assert(isinstance(_run("value", "Transform2D(0.0,1.0,2.0,3.0,4.0,5.0,6.0)"), GdValueTransform2D))
    assert(_run("value", "Transform2D(0,1,2,3,4,5,6)") == "Transform2D(0.0,1.0,2.0,3.0,4.0,5.0,6.0)")
    assert(_run("value", "Transform2D()") == GdValueTransform2D())
    assert(_run("value", "Transform2D(0,1,2,3,4,5,6)") == GdValueTransform2D((0,1,2,3,4,5,6)))

def test_GdValueTransform3D():
    assert(hasattr(gdparser._transformer, "transform3d"))
    assert(isinstance(_run("value", "Transform3D()"), GdValueTransform3D))
    assert(isinstance(_run("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10)"), GdValueTransform3D))
    assert(isinstance(_run("value", "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0)"), GdValueTransform3D))
    assert(_run("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10)") == _run("value", "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0)"))
    assert(_run("value", "Transform3D()") == GdValueTransform3D())
    assert(_run("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10)") == GdValueTransform3D((0,1,2,3,4,5,6,7,8,9,10)))

def test_GdValuePackedByteArray():
    assert(hasattr(gdparser._transformer, "packedbytearray"))
    assert(isinstance(_run("value", "PackedByteArray()"), GdValuePackedByteArray))
    assert(isinstance(_run("value", "PackedByteArray(abc123)"), GdValuePackedByteArray))
    assert(_run("value", "PackedByteArray()") == GdValuePackedByteArray())
    assert(_run("value", "PackedByteArray(abc123)") == GdValuePackedByteArray("abc123"))

def test_GdValuePackedInt32Array():
    assert(hasattr(gdparser._transformer, "packedint32array"))
    assert(isinstance(_run("value", "PackedInt32Array()"), GdValuePackedInt32Array))
    assert(isinstance(_run("value", "PackedInt32Array(0,1,2,3)"), GdValuePackedInt32Array))
    assert(_run("value", "PackedInt32Array()") == GdValuePackedInt32Array())
    assert(_run("value", "PackedInt32Array(0,1,2,3,4)") == GdValuePackedInt32Array((0,1,2,3,4)))
def test_GdValuePackedInt64Array():
    assert(hasattr(gdparser._transformer, "packedint64array"))
    assert(isinstance(_run("value", "PackedInt64Array()"), GdValuePackedInt64Array))
    assert(isinstance(_run("value", "PackedInt64Array(0,1,2,3)"), GdValuePackedInt64Array))
    assert(_run("value", "PackedInt64Array()") == GdValuePackedInt64Array())
    assert(_run("value", "PackedInt64Array(0,1,2,3,4)") == GdValuePackedInt64Array((0,1,2,3,4)))

def test_GdValuePackedFloat32Array():
    assert(hasattr(gdparser._transformer, "packedfloat32array"))
    assert(isinstance(_run("value", "PackedFloat32Array()"), GdValuePackedFloat32Array))
    assert(isinstance(_run("value", "PackedFloat32Array(0,1,2,3,4)"), GdValuePackedFloat32Array))
    assert(isinstance(_run("value", "PackedFloat32Array(0.0,1.0,2.0,3.0,4.0)"), GdValuePackedFloat32Array))
    assert(_run("value", "PackedFloat32Array()") == GdValuePackedFloat32Array())
    assert(_run("value", "PackedFloat32Array(0,1,2,3,4)") == _run("value", "PackedFloat32Array(0.0,1.0,2.0,3.0,4.0)"))
    assert(_run("value", "PackedFloat32Array(0,1,2,3,4)") == GdValuePackedFloat32Array((0,1,2,3,4)))
def test_GdValuePackedFloat64Array():
    assert(hasattr(gdparser._transformer, "packedfloat64array"))
    assert(isinstance(_run("value", "PackedFloat64Array()"), GdValuePackedFloat64Array))
    assert(isinstance(_run("value", "PackedFloat64Array(0,1,2,3,4)"), GdValuePackedFloat64Array))
    assert(isinstance(_run("value", "PackedFloat64Array(0.0,1.0,2.0,3.0,4.0)"), GdValuePackedFloat64Array))
    assert(_run("value", "PackedFloat64Array(0,1,2,3,4)") == _run("value", "PackedFloat64Array(0.0,1.0,2.0,3.0,4.0)"))
    assert(_run("value", "PackedFloat64Array(0,1,2,3,4)") == GdValuePackedFloat64Array((0,1,2,3,4)))
    assert(_run("value", "PackedFloat64Array()") == GdValuePackedFloat64Array())

def test_GdValuePackedStringArray():
    assert(hasattr(gdparser._transformer, "packedstringarray"))
    assert(isinstance(_run("value", "PackedStringArray()"), GdValuePackedStringArray))
    assert(isinstance(_run("value", 'PackedStringArray("a","b")'), GdValuePackedStringArray))
    assert(_run("value", "PackedStringArray()") == GdValuePackedStringArray())
    assert(_run("value", 'PackedStringArray("a","b")') != GdValuePackedStringArray("ab"))
    assert(_run("value", 'PackedStringArray("a","b")') == GdValuePackedStringArray(("a","b")))

def test_GdValuePackedVector2Array():
    assert(hasattr(gdparser._transformer, "packedvector2array"))
    assert(isinstance(_run("value", "PackedVector2Array()"), GdValuePackedVector2Array))
    assert(isinstance(_run("value", "PackedVector2Array(0,1,2,3)"), GdValuePackedVector2Array))
    assert(isinstance(_run("value", "PackedVector2Array(0.0,1.0,2.0,3.0)"), GdValuePackedVector2Array))
    assert(_run("value", "PackedVector2Array(0,1,0,1)") == _run("value", "PackedVector2Array(0.0,1.0,0.0,1.0)"))
    assert(_run("value", "PackedVector2Array()") == GdValuePackedVector2Array())
    assert(_run("value", "PackedVector2Array(0,1,0,1)") == GdValuePackedVector2Array((0,1,0,1)))
    assert(_run("value", "PackedVector2Array(0,1,0,1)") == GdValuePackedVector2Array(((0,1),(0,1))))
    assert(_run("value", "PackedVector2Array(0,1,0,1)") == GdValuePackedVector2Array((GdValueVector3(0,1),GdValueVector3(0,1))))
def test_GdValuePackedVector3Array():
    assert(hasattr(gdparser._transformer, "packedvector3array"))
    assert(isinstance(_run("value", "PackedVector3Array()"), GdValuePackedVector3Array))
    assert(isinstance(_run("value", "PackedVector3Array(0,1,2,0,1,2)"), GdValuePackedVector3Array))
    assert(isinstance(_run("value", "PackedVector3Array(0.0,1.0,2.0,0.0,1.0,2.0)"), GdValuePackedVector3Array))
    assert(_run("value", "PackedVector3Array()") == GdValuePackedVector3Array())
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == _run("value", "PackedVector3Array(0.0,1.0,2.0,0.0,1.0,2.0)"))
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array((0,1,2,0,1,2)))
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array(((0,1,2),(0,1,2))))
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array((GdValueVector3(0,1,2),GdValueVector3(0,1,2))))
def test_GdValuePackedVector4Array():
    assert(hasattr(gdparser._transformer, "packedvector4array"))
    assert(isinstance(_run("value", "PackedVector4Array()"), GdValuePackedVector4Array))
    assert(isinstance(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)"), GdValuePackedVector4Array))
    assert(isinstance(_run("value", "PackedVector4Array(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"), GdValuePackedVector4Array))
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == _run("value", "PackedVector4Array(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"))
    assert(_run("value", "PackedVector4Array()") == GdValuePackedVector4Array())
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)" == GdValuePackedVector4Array((0,1,2,3,0,1,2,3))))
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)" == GdValuePackedVector4Array((0,1,2,3),(0,1,2,3))))
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)" == GdValuePackedVector4Array(GdValueVector4(0,1,2,3),GdValueVector4(0,1,2,3))))

def test_GdValuePackedColorArray():
    assert(hasattr(gdparser._transformer, "packedcolorarray" ))
    assert(isinstance(_run("value", "PackedColorArray()"), GdValuePackedColorArray))
    assert(_run("value", "PackedColorArray()")== GdValuePackedColorArray())
    assert(isinstance(_run("value", "PackedColorArray(0,1,2,3,0,1,2,3)"), GdValuePackedColorArray))
    assert(isinstance(_run("value", "PackedColorArray(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"), GdValuePackedColorArray))
    assert(_run("value", "PackedColorArray(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)") == _run("value", "PackedColorArray(0,1,2,3,0,1,2,3)"))
    assert(_run("value", "PackedColorArray(0,1,2,3,0,1,2,3)") == GdValuePackedColorArray((0,1,2,3,0,1,2,3)))
    assert(_run("value", "PackedColorArray(0,1,2,3,0,1,2,3)") == GdValuePackedColorArray((GdValueColor(0,1,2,3),GdValueColor(0,1,2,3))))