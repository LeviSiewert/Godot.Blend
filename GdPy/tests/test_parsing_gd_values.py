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
def test_GdValueExtResource():
    assert(hasattr(gdparser._transformer,"extresource"))
    assert(isinstance(_run("value", 'ExtResource("")'), GdValueExtResource))
    assert(isinstance(_run("value", 'ExtResource()'), GdValueExtResource))
def test_GdValueNodePath():
    assert(hasattr(gdparser._transformer,"nodepath"))
    assert(isinstance(_run("value", 'NodePath("")'), GdValueNodePath))
    assert(isinstance(_run("value", 'NodePath()'), GdValueNodePath))
def test_GdValueSubResource():
    assert(hasattr(gdparser._transformer,"subresource"))
    assert(isinstance(_run("value", 'SubResource("")'), GdValueSubResource))
    assert(isinstance(_run("value", 'SubResource()'), GdValueSubResource))

    
def test_GdValueStringName():
    assert(hasattr(gdparser._transformer,"STRINGNAME"))
    assert(isinstance(_run("value", '&"value"'), GdValueStringName))

def test_GdValueDictionary():
    assert(hasattr(gdparser._transformer,"dictionary"))
    assert(hasattr(gdparser._transformer,"dictionary_explicit"))
    assert(isinstance(_run("value", "{}"), GdValueDictionary))
    assert(isinstance(_run("value", "Dictionary()"), GdValueDictionary))
    assert(isinstance(_run("value", "Dictionary[Variant,Variant]()"), GdValueDictionary))
def test_GdValueArray():
    assert(hasattr(gdparser._transformer, "array"))
    assert(isinstance(_run("value", "Array[Variant]()"), GdValueArray))
    assert(isinstance(_run("value", "Array()"), GdValueArray))
    assert(isinstance(_run("value", "[]"), GdValueArray))

def test_GdValueVector2():
    assert(hasattr(gdparser._transformer, "vector2"))
    assert(isinstance(_run("value", "Vector2()"), GdValueVector2))
def test_GdValueVector3():
    assert(hasattr(gdparser._transformer, "vector3"))
    assert(isinstance(_run("value", "Vector3()"), GdValueVector3))
def test_GdValueVector4():
    assert(hasattr(gdparser._transformer, "vector4"))
    assert(isinstance(_run("value", "Vector4()"), GdValueVector4))
def test_GdValueVector2i():
    assert(hasattr(gdparser._transformer, "vector2i"))
    assert(isinstance(_run("value", "Vector2i()"), GdValueVector2i))
def test_GdValueVector3i():
    assert(hasattr(gdparser._transformer, "vector3i"))
    assert(isinstance(_run("value", "Vector3i()"), GdValueVector3i))
def test_GdValueVector4i():
    assert(hasattr(gdparser._transformer, "vector4i"))
    assert(isinstance(_run("value", "Vector4i()"), GdValueVector4i))
def test_GdValueRect2():
    assert(hasattr(gdparser._transformer, "rect2"))
    assert(isinstance(_run("value", "Rect2()"), GdValueRect2))
def test_GdValueRect2i():
    assert(hasattr(gdparser._transformer, "rect2i"))
    assert(isinstance(_run("value", "Rect2i()"), GdValueRect2i))
def test_GdValuePlane():
    assert(hasattr(gdparser._transformer, "plane"))
    assert(isinstance(_run("value", "Plane()"), GdValuePlane))
def test_GdValueColor():
    assert(hasattr(gdparser._transformer, "color"))
    assert(isinstance(_run("value", "Color()"), GdValueColor))
def test_GdValueAABB():
    assert(hasattr(gdparser._transformer, "aabb"))
    assert(isinstance(_run("value", "AABB()"), GdValueAABB))
def test_GdValueQuaternion():
    assert(hasattr(gdparser._transformer, "quaternion"))
    assert(isinstance(_run("value", "Quaternion()"), GdValueQuaternion))
def test_GdValueBasis():
    assert(hasattr(gdparser._transformer, "basis"))
    assert(isinstance(_run("value", "Basis()"), GdValueBasis))
def test_GdValueTransform2D():
    assert(hasattr(gdparser._transformer, "transform2d"))
    assert(isinstance(_run("value", "Transform2D()"), GdValueTransform2D))
def test_GdValueTransform3D():
    assert(hasattr(gdparser._transformer, "transform3d"))
    assert(isinstance(_run("value", "Transform3D()"), GdValueTransform3D))

def test_GdValuePackedByteArray():
    assert(hasattr(gdparser._transformer, "packedbytearray"))
    assert(isinstance(_run("value", "PackedByteArray()"), GdValuePackedByteArray))
def test_GdValuePackedInt32Array():
    assert(hasattr(gdparser._transformer, "packedint32array"))
    assert(isinstance(_run("value", "PackedInt32Array()"), GdValuePackedInt32Array))
def test_GdValuePackedInt64Array():
    assert(hasattr(gdparser._transformer, "packedint64array"))
    assert(isinstance(_run("value", "PackedInt64Array()"), GdValuePackedInt64Array))
def test_GdValuePackedFloat32Array():
    assert(hasattr(gdparser._transformer, "packedfloat32array"))
    assert(isinstance(_run("value", "PackedFloat32Array()"), GdValuePackedFloat32Array))
def test_GdValuePackedFloat64Array():
    assert(hasattr(gdparser._transformer, "packedfloat64array"))
    assert(isinstance(_run("value", "PackedFloat64Array()"), GdValuePackedFloat64Array))
def test_GdValuePackedStringArray():
    assert(hasattr(gdparser._transformer, "packedstringarray"))
    assert(isinstance(_run("value", "PackedStringArray()"), GdValuePackedStringArray))
def test_GdValuePackedVector2Array():
    assert(hasattr(gdparser._transformer, "packedvector2array"))
    assert(isinstance(_run("value", "PackedVector2Array()"), GdValuePackedVector2Array))
def test_GdValuePackedVector3Array():
    assert(hasattr(gdparser._transformer, "packedvector3array"))
    assert(isinstance(_run("value", "PackedVector3Array()"), GdValuePackedVector3Array))
def test_GdValuePackedVector4Array():
    assert(hasattr(gdparser._transformer, "packedvector4array"))
    assert(isinstance(_run("value", "PackedVector4Array()"), GdValuePackedVector4Array))
def test_GdValuePackedColorArray():
    assert(hasattr(gdparser._transformer, "packedcolorarray" ))
    assert(isinstance(_run("value", "PackedColorArray(0,1,2,3)"), GdValuePackedColorArray))

