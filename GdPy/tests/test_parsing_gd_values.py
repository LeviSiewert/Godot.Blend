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
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", 'ExtResource("")'), GdValueExtResource))
    assert(isinstance(_run("value", 'ExtResource()'), GdValueExtResource))
def test_GdValueNodePath():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", 'NodePath("")'), GdValueNodePath))
    assert(isinstance(_run("value", 'NodePath()'), GdValueNodePath))
def test_GdValueSubResource():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", 'SubResource("")'), GdValueSubResource))
    assert(isinstance(_run("value", 'SubResource()'), GdValueSubResource))

    
def test_GdValueStringName():
    assert(isinstance(_run("value", '&"value"'), GdValueStringName))

def test_GdValueDictionary():
    assert(isinstance(_run("value", "Dictionary[Variant,Variant]()"), GdValueDictionary))
    assert(isinstance(_run("value", "Dictionary()"), GdValueDictionary))
    assert(isinstance(_run("value", "{}"), GdValueDictionary))
def test_GdValueArray():
    assert(isinstance(_run("value", "Array[Variant]()"), GdValueArray))
    assert(isinstance(_run("value", "Array()"), GdValueArray))
    assert(isinstance(_run("value", "[]"), GdValueArray))

def test_GdValueVector2():
    assert(isinstance(_run("value", "Vector2()"), GdValueVector2))
def test_GdValueVector3():
    assert(isinstance(_run("value", "Vector3()"), GdValueVector3))
def test_GdValueVector4():
    assert(isinstance(_run("value", "Vector4()"), GdValueVector4))
def test_GdValueVector2i():
    assert(isinstance(_run("value", "Vector2i()"), GdValueVector2i))
def test_GdValueVector3i():
    assert(isinstance(_run("value", "Vector3i()"), GdValueVector3i))
def test_GdValueVector4i():
    assert(isinstance(_run("value", "Vector4i()"), GdValueVector4i))
def test_GdValueRect2():
    assert(isinstance(_run("value", "Rect2()"), GdValueRect2))
def test_GdValueRect2i():
    assert(isinstance(_run("value", "Rect2i()"), GdValueRect2i))
def test_GdValuePlane():
    assert(isinstance(_run("value", "Plane()"), GdValuePlane))
def test_GdValueColor():
    assert(isinstance(_run("value", "Color()"), GdValueColor))
def test_GdValueAABB():
    assert(isinstance(_run("value", "AABB()"), GdValueAABB))
def test_GdValueQuaternion():
    assert(isinstance(_run("value", "Quaternion()"), GdValueQuaternion))
def test_GdValueBasis():
    assert(isinstance(_run("value", "Basis()"), GdValueBasis))
def test_GdValueTransform2D():
    assert(isinstance(_run("value", "Transform2D()"), GdValueTransform2D))
def test_GdValueTransform3D():
    assert(isinstance(_run("value", "Transform3D()"), GdValueTransform3D))

def test_GdValuePackedByteArray():
    assert(isinstance(_run("value", "PackedByteArray()"), GdValuePackedByteArray))
def test_GdValuePackedInt32Array():
    assert(isinstance(_run("value", "PackedInt32Array()"), GdValuePackedInt32Array))
def test_GdValuePackedInt64Array():
    assert(isinstance(_run("value", "PackedInt64Array()"), GdValuePackedInt64Array))
def test_GdValuePackedFloat32Array():
    assert(isinstance(_run("value", "PackedFloat32Array()"), GdValuePackedFloat32Array))
def test_GdValuePackedFloat64Array():
    assert(isinstance(_run("value", "PackedFloat64Array()"), GdValuePackedFloat64Array))
def test_GdValuePackedStringArray():
    assert(isinstance(_run("value", "PackedStringArray()"), GdValuePackedStringArray))
def test_GdValuePackedVector2Array():
    assert(isinstance(_run("value", "PackedVector2Array()"), GdValuePackedVector2Array))
def test_GdValuePackedVector3Array():
    assert(isinstance(_run("value", "PackedVector3Array()"), GdValuePackedVector3Array))
def test_GdValuePackedVector4Array():
    assert(isinstance(_run("value", "PackedVector4Array()"), GdValuePackedVector4Array))
def test_GdValuePackedColorArray():
    assert(isinstance(_run("value", "PackedColorArray(0,1,2,3)"), GdValuePackedColorArray))

