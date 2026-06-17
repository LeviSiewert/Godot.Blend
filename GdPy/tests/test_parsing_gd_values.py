# from pytest import fixture

from ..structure.values import *
from ..structure.references import *
from ..structure.core.primitives import Context

from ..structure.values_transformer import gd_to_py_ruleset as values_ruleset
from ..structure.sub_resources_transformer import gd_to_py_ruleset as subres_ruleset
from ..structure.sub_resource_collections_transformer import gd_to_py_ruleset as subrescol_ruleset
from ..structure.resources_transformer import gd_to_py_ruleset as res_ruleset
from ..structure.references_transformer import gd_to_py_ruleset as ref_ruleset

from ..structure.core.gd_parser import GdParser
from ..resources import grammer

gdparser = GdParser(grammer, (
    values_ruleset, 
    subres_ruleset,
    subrescol_ruleset,
    res_ruleset,
    ref_ruleset,
    ),
    start = "value")

c = Context()
def _run(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)

def test_GdValueResourceID():
    assert(gdparser._transformer.matcher(None, "rid"))
    assert(isinstance(_run("value", "RID()"), GdValueResourceID)) 
    # assert(_run("value", "RID()") == GdValueResourceID())
    # assert(_run("value", 'RID("")') == GdValueResourceID())
def test_GdValueExtResource():
    assert(gdparser._transformer.matcher(None, "extresource"))
    assert(isinstance(_run("value", 'ExtResource()'), GdValueExtResource))
    assert(isinstance(_run("value", 'ExtResource("")'), GdValueExtResource))
    # assert(_run("value", 'ExtResource()') == GdValueExtResource())
    # assert(_run("value", 'ExtResource("")') == GdValueExtResource())
def test_GdValueNodePath():
    assert(gdparser._transformer.matcher(None, "nodepath"))
    assert(isinstance(_run("value", 'NodePath()'), GdValueNodePath))
    assert(isinstance(_run("value", 'NodePath("")'), GdValueNodePath))
    # assert(_run("value", 'NodePath()') == GdValueNodePath())
    # assert(_run("value", 'NodePath("")') == GdValueNodePath())
def test_GdValueSubResource():
    assert(gdparser._transformer.matcher(None, "subresource"))
    assert(isinstance(_run("value", 'SubResource()'), GdValueSubResource))
    assert(isinstance(_run("value", 'SubResource("")'), GdValueSubResource))
    # assert(_run("value", 'SubResource()') == GdValueSubResource())
    # assert(_run("value", 'SubResource("")') == GdValueSubResource())

    
def test_GdValueStringName():
    assert(gdparser._transformer.matcher(None, "stringname"))
    assert(isinstance(_run("value", '&"value"'), GdValueStringName))
    # assert(_run("value", '&"va) ==e()"') GdValueStringName))

def test_GdValueDictionary():
    assert(gdparser._transformer.matcher(None, "dictionary"))
    assert(gdparser._transformer.matcher(None, "dictionary_explicit"))
    assert(isinstance(_run("value", "{}"), GdValueDictionary))
    # assert(_run("value", "{}"), GdValueDiction) ==y())
    assert(isinstance(_run("value", "Dictionary()"), GdValueDictionary))
    assert(_run("value", "Dictionary()") == GdValueDictionary())
    assert(isinstance(_run("value", "Dictionary[Variant,Variant]()"), GdValueDictionary))
    # assert(_run("value", "Dictionary[Varia) ==,Variant()]()") GdValueDictionary))
def test_GdValueArray():
    assert(gdparser._transformer.matcher(None,  "array"))
    assert(isinstance(_run("value", "Array[Variant]()"), GdValueArray))
    # assert(_run("value", "Array[Vari) ==t()]()") GdValueArray))
    assert(isinstance(_run("value", "Array()"), GdValueArray))
    assert(_run("value", "Array()") == GdValueArray())
    assert(isinstance(_run("value", "[]"), GdValueArray))
    # assert(_run("value", "[]"), GdValueAr) ==y())

def test_GdValueVector2():
    assert(gdparser._transformer.matcher(None,  "vector2"))
    assert(isinstance(_run("value", "Vector2()"), GdValueVector2))
    assert(isinstance(_run("value", "Vector2(0,1)"), GdValueVector2))
    assert(isinstance(_run("value", "Vector2(0.0,1.0)"), GdValueVector2))
    assert(_run("value", "Vector2()") == GdValueVector2())
    assert(_run("value", "Vector2(0,1)") == _run("value", "Vector2(0.0,1.0)"))
    assert(_run("value", "Vector2(0,1)") == GdValueVector2((0,1)))
def test_GdValueVector3():
    assert(gdparser._transformer.matcher(None,  "vector3"))
    assert(isinstance(_run("value", "Vector3()"), GdValueVector3))
    assert(isinstance(_run("value", "Vector3(0,1,2)"), GdValueVector3))
    assert(isinstance(_run("value", "Vector3(0.0,1.0,2.0)"), GdValueVector3))
    assert(_run("value", "Vector3()") == GdValueVector3())
    assert(_run("value", "Vector3(0,1,2)") == _run("value", "Vector3(0.0,1.0,2.0)"))
    assert(_run("value", "Vector3(0,1,2)") == GdValueVector3((0,1,2)))
def test_GdValueVector4():
    assert(gdparser._transformer.matcher(None,  "vector4"))
    assert(isinstance(_run("value", "Vector4()"), GdValueVector4))
    assert(isinstance(_run("value", "Vector4(0,1,2,3)"), GdValueVector4))
    assert(isinstance(_run("value", "Vector4(0.0,1.0,2.0,3.0)"), GdValueVector4))
    assert(_run("value", "Vector4()") == GdValueVector4())
    assert(_run("value", "Vector4(0,1,2,3)") == _run("value", "Vector4(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Vector4(0,1,2,3)") == GdValueVector4((0,1,2,3)))


def test_GdValueVector2i():
    assert(gdparser._transformer.matcher(None,  "vector2i"))
    assert(isinstance(_run("value", "Vector2i()"), GdValueVector2i))
    assert(isinstance(_run("value", "Vector2i(0,1)"), GdValueVector2i))
    assert(_run("value", "Vector2i()") == GdValueVector2i())
    assert(_run("value", "Vector2i(0,1)") == GdValueVector2i((0,1)))
def test_GdValueVector3i():
    assert(gdparser._transformer.matcher(None,  "vector3i"))
    assert(isinstance(_run("value", "Vector3i()"), GdValueVector3i))
    assert(isinstance(_run("value", "Vector3i(0,1,2)"), GdValueVector3i))
    assert(_run("value", "Vector3i()") == GdValueVector3i())
    assert(_run("value", "Vector3i(0,1,2)") == GdValueVector3i((0,1,2)))
def test_GdValueVector4i():
    assert(gdparser._transformer.matcher(None,  "vector4i"))
    assert(isinstance(_run("value", "Vector4i()"), GdValueVector4i))
    assert(isinstance(_run("value", "Vector4i(0,1,2,3)"), GdValueVector4i))
    assert(_run("value", "Vector4i()") == GdValueVector4i())
    assert(_run("value", "Vector4i(0,1,2,3)") == GdValueVector4i((0,1,2,3)))


def test_GdValueRect2():
    assert(gdparser._transformer.matcher(None,  "rect2"))
    assert(isinstance(_run("value", "Rect2()"), GdValueRect2))
    assert(isinstance(_run("value", "Rect2(0,1,2,3)"), GdValueRect2))
    assert(isinstance(_run("value", "Rect2(0.0,1.0,2.0,3.0)"), GdValueRect2))
    assert(_run("value", "Rect2(0,1,2,3)") == _run("value", "Rect2(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Rect2()") == GdValueRect2())
    assert(_run("value", "Rect2(0,1,2,3)") == GdValueRect2((0,1,2,3)))
def test_GdValueRect2i():
    assert(gdparser._transformer.matcher(None,  "rect2i"))
    assert(isinstance(_run("value", "Rect2i()"), GdValueRect2i))
    assert(isinstance(_run("value", "Rect2i(0,1,2,3)"), GdValueRect2i))
    assert(_run("value", "Rect2i()") == GdValueRect2i())
    assert(_run("value", "Rect2i(0,1,2,3)") == GdValueRect2i((0,1,2,3)))

def test_GdValuePlane():
    assert(gdparser._transformer.matcher(None,  "plane"))
    assert(isinstance(_run("value", "Plane()"), GdValuePlane))
    assert(isinstance(_run("value", "Plane(0,1,2,3)"), GdValuePlane))
    assert(isinstance(_run("value", "Plane(0.0,1.0,2.0,3.0)"), GdValuePlane))
    assert(_run("value", "Plane()") == GdValuePlane())
    assert(_run("value", "Plane(0,1,2,3)") == _run("value", "Plane(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Plane(0,1,2,3)") == GdValueColor((0,1,2,3)))
def test_GdValueColor():
    assert(gdparser._transformer.matcher(None,  "color"))
    assert(isinstance(_run("value", "Color()"), GdValueColor))
    assert(isinstance(_run("value", "Color(0,1,2,3)"), GdValueColor))
    assert(isinstance(_run("value", "Color(0.0,1.0,2.0,3.0)"), GdValueColor))
    assert(_run("value", "Color()") == GdValueColor())
    assert(_run("value", "Color(0,1,2,3)") == _run("value", "Color(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Color(0,1,2,3)") == GdValueColor((0,1,2,3)))

def test_GdValueAABB():
    assert(gdparser._transformer.matcher(None,  "aabb"))
    assert(isinstance(_run("value", "AABB()"), GdValueAABB))
    assert(isinstance(_run("value", "AABB(1,2,3,4,5,6)"), GdValueAABB))
    assert(isinstance(_run("value", "AABB(1.0,2.0,3.0,4.0,5.0,6.0)"), GdValueAABB))
    assert(_run("value", "AABB()") == GdValueAABB())
    assert(_run("value", "AABB(1,2,3,4,5,6)")== _run("value", "AABB(1.0,2.0,3.0,4.0,5.0,6.0)"))

def test_GdValueQuaternion():
    assert(gdparser._transformer.matcher(None,  "quaternion"))
    assert(isinstance(_run("value", "Quaternion()"), GdValueQuaternion))
    assert(isinstance(_run("value", "Quaternion(0,1,2,3)"), GdValueQuaternion))
    assert(isinstance(_run("value", "Quaternion(0.0,1.0,2.0,3.0)"), GdValueQuaternion))
    assert(_run("value", "Quaternion()") == GdValueQuaternion())
    assert(_run("value", "Quaternion(0,1,2,3)") == _run("value", "Quaternion(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "Quaternion(0,1,2,3)") == GdValueQuaternion((0,1,2,3)))

def test_GdValueBasis():
    assert(gdparser._transformer.matcher(None,  "basis"))
    assert(isinstance(_run("value", "Basis()"), GdValueBasis))
    assert(isinstance(_run("value", "Basis(0,1,2,3,4,5,6,7,8)"), GdValueBasis))
    assert(isinstance(_run("value", "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0)"), GdValueBasis))
    assert(_run("value", "Basis(0,1,2,3,4,5,6,7,8)") == _run("value", "Basis(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0)"))
    assert(_run("value", "Basis()") == GdValueBasis())
    assert(_run("value", "Basis(0,1,2,3,4,5,6,7,8)") == GdValueBasis((0,1,2,3,4,5,6,7,8)))

def test_GdValueTransform2D():
    assert(gdparser._transformer.matcher(None,  "transform2d"))
    assert(isinstance(_run("value", "Transform2D()"), GdValueTransform2D))
    assert(isinstance(_run("value", "Transform2D(0,1,2,3,4,5)"), GdValueTransform2D))
    assert(isinstance(_run("value", "Transform2D(0.0,1.0,2.0,3.0,4.0,5.0)"), GdValueTransform2D))
    assert(_run("value", "Transform2D(0,1,2,3,4,5)") == _run("value","Transform2D(0.0,1.0,2.0,3.0,4.0,5.0)"))
    assert(_run("value", "Transform2D()") == GdValueTransform2D())
    assert(_run("value", "Transform2D(0,1,2,3,4,5)") == GdValueTransform2D((0,1,2,3,4,5)))

def test_GdValueTransform3D():
    assert(gdparser._transformer.matcher(None,  "transform3d"))
    assert(isinstance(_run("value", "Transform3D()"), GdValueTransform3D))
    assert(isinstance(_run("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)"), GdValueTransform3D))
    assert(isinstance(_run("value", "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0)"), GdValueTransform3D))
    assert(_run("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)") == _run("value", "Transform3D(0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0)"))
    assert(_run("value", "Transform3D()") == GdValueTransform3D())
    assert(_run("value", "Transform3D(0,1,2,3,4,5,6,7,8,9,10,11)") == GdValueTransform3D((0,1,2,3,4,5,6,7,8,9,10,11)))

def test_GdValuePackedByteArray():
    assert(gdparser._transformer.matcher(None,  "packedbytearray"))
    assert(isinstance(_run("value", "PackedByteArray()"), GdValuePackedByteArray))
    assert(isinstance(_run("value", 'PackedByteArray("abc123")'), GdValuePackedByteArray))
    assert(_run("value", "PackedByteArray()") == GdValuePackedByteArray())
    assert(_run("value", 'PackedByteArray("abc123")') == GdValuePackedByteArray(("abc123",)))

def test_GdValuePackedInt32Array():
    assert(gdparser._transformer.matcher(None,  "packedint32array"))
    assert(isinstance(_run("value", "PackedInt32Array()"), GdValuePackedInt32Array))
    assert(isinstance(_run("value", "PackedInt32Array(0,1,2,3)"), GdValuePackedInt32Array))
    assert(_run("value", "PackedInt32Array()") == GdValuePackedInt32Array())
    assert(_run("value", "PackedInt32Array(0,1,2,3,4)") == GdValuePackedInt32Array((0,1,2,3,4)))
def test_GdValuePackedInt64Array():
    assert(gdparser._transformer.matcher(None,  "packedint64array"))
    assert(isinstance(_run("value", "PackedInt64Array()"), GdValuePackedInt64Array))
    assert(isinstance(_run("value", "PackedInt64Array(0,1,2,3)"), GdValuePackedInt64Array))
    assert(_run("value", "PackedInt64Array()") == GdValuePackedInt64Array())
    assert(_run("value", "PackedInt64Array(0,1,2,3,4)") == GdValuePackedInt64Array((0,1,2,3,4)))

def test_GdValuePackedFloat32Array():
    assert(gdparser._transformer.matcher(None,  "packedfloat32array"))
    assert(isinstance(_run("value", "PackedFloat32Array()"), GdValuePackedFloat32Array))
    assert(isinstance(_run("value", "PackedFloat32Array(0,1,2,3,4)"), GdValuePackedFloat32Array))
    assert(isinstance(_run("value", "PackedFloat32Array(0.0,1.0,2.0,3.0,4.0)"), GdValuePackedFloat32Array))
    assert(_run("value", "PackedFloat32Array()") == GdValuePackedFloat32Array())
    assert(_run("value", "PackedFloat32Array(0,1,2,3,4)") == _run("value", "PackedFloat32Array(0.0,1.0,2.0,3.0,4.0)"))
    assert(_run("value", "PackedFloat32Array(0,1,2,3,4)") == GdValuePackedFloat32Array((0,1,2,3,4)))
def test_GdValuePackedFloat64Array():
    assert(gdparser._transformer.matcher(None,  "packedfloat64array"))
    assert(isinstance(_run("value", "PackedFloat64Array()"), GdValuePackedFloat64Array))
    assert(isinstance(_run("value", "PackedFloat64Array(0,1,2,3,4)"), GdValuePackedFloat64Array))
    assert(isinstance(_run("value", "PackedFloat64Array(0.0,1.0,2.0,3.0,4.0)"), GdValuePackedFloat64Array))
    assert(_run("value", "PackedFloat64Array(0,1,2,3,4)") == _run("value", "PackedFloat64Array(0.0,1.0,2.0,3.0,4.0)"))
    assert(_run("value", "PackedFloat64Array(0,1,2,3,4)") == GdValuePackedFloat64Array((0,1,2,3,4)))
    assert(_run("value", "PackedFloat64Array()") == GdValuePackedFloat64Array())

def test_GdValuePackedStringArray():
    assert(gdparser._transformer.matcher(None,  "packedstringarray"))
    assert(isinstance(_run("value", "PackedStringArray()"), GdValuePackedStringArray))
    assert(isinstance(_run("value", 'PackedStringArray("a","b")'), GdValuePackedStringArray))
    assert(_run("value", "PackedStringArray()") == GdValuePackedStringArray())
    assert(_run("value", 'PackedStringArray("a","b")') != GdValuePackedStringArray(("ab",)))
    assert(_run("value", 'PackedStringArray("a","b")') == GdValuePackedStringArray(("a","b")))

def test_GdValuePackedVector2Array():
    assert(gdparser._transformer.matcher(None,  "packedvector2array"))
    assert(isinstance(_run("value", "PackedVector2Array()"), GdValuePackedVector2Array))
    assert(isinstance(_run("value", "PackedVector2Array(0,1,2,3)"), GdValuePackedVector2Array))
    assert(isinstance(_run("value", "PackedVector2Array(0.0,1.0,2.0,3.0)"), GdValuePackedVector2Array))
    assert(_run("value", "PackedVector2Array(0,1,2,3)") == _run("value", "PackedVector2Array(0.0,1.0,2.0,3.0)"))
    assert(_run("value", "PackedVector2Array()") == GdValuePackedVector2Array())
    assert(2 == len(GdValuePackedVector2Array((0,1,2,3))))
    assert(3 == len(GdValuePackedVector2Array((0,1,2,3,4,5))))
    assert(_run("value", "PackedVector2Array(0,1,2,3)") == GdValuePackedVector2Array((0,1,2,3)))
    assert(_run("value", "PackedVector2Array(0,1,2,3)") == GdValuePackedVector2Array(((0,1),(2,3))))
    assert(_run("value", "PackedVector2Array(0,1,2,3)") == GdValuePackedVector2Array((GdValueVector2((0,1)),GdValueVector2((2,3)))))
def test_GdValuePackedVector3Array():
    assert(gdparser._transformer.matcher(None,  "packedvector3array"))
    assert(isinstance(_run("value", "PackedVector3Array()"), GdValuePackedVector3Array))
    assert(isinstance(_run("value", "PackedVector3Array(0,1,2,0,1,2)"), GdValuePackedVector3Array))
    assert(isinstance(_run("value", "PackedVector3Array(0.0,1.0,2.0,0.0,1.0,2.0)"), GdValuePackedVector3Array))
    assert(_run("value", "PackedVector3Array()") == GdValuePackedVector3Array())
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == _run("value", "PackedVector3Array(0.0,1.0,2.0,0.0,1.0,2.0)"))
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array((0,1,2,0,1,2)))
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array(((0,1,2),(0,1,2))))
    assert(_run("value", "PackedVector3Array(0,1,2,0,1,2)") == GdValuePackedVector3Array((GdValueVector3((0,1,2)),GdValueVector3((0,1,2)))))
def test_GdValuePackedVector4Array():
    assert(gdparser._transformer.matcher(None,  "packedvector4array"))
    assert(isinstance(_run("value", "PackedVector4Array()"), GdValuePackedVector4Array))
    assert(isinstance(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)"), GdValuePackedVector4Array))
    assert(isinstance(_run("value", "PackedVector4Array(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"), GdValuePackedVector4Array))
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == _run("value", "PackedVector4Array(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"))
    assert(_run("value", "PackedVector4Array()") == GdValuePackedVector4Array())
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == GdValuePackedVector4Array((0,1,2,3,0,1,2,3)))
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == GdValuePackedVector4Array(((0,1,2,3),(0,1,2,3))))
    assert(_run("value", "PackedVector4Array(0,1,2,3,0,1,2,3)") == GdValuePackedVector4Array((GdValueVector4((0,1,2,3)),GdValueVector4((0,1,2,3)))))

def test_GdValuePackedColorArray():
    assert(gdparser._transformer.matcher(None,  "packedcolorarray" ))
    assert(isinstance(_run("value", "PackedColorArray()"), GdValuePackedColorArray))
    assert(_run("value", "PackedColorArray()")== GdValuePackedColorArray())
    assert(isinstance(_run("value", "PackedColorArray(0,1,2,3,0,1,2,3)"), GdValuePackedColorArray))
    assert(isinstance(_run("value", "PackedColorArray(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)"), GdValuePackedColorArray))
    assert(_run("value", "PackedColorArray(0.0,1.0,2.0,3.0,0.0,1.0,2.0,3.0)") == _run("value", "PackedColorArray(0,1,2,3,0,1,2,3)"))
    assert(_run("value", "PackedColorArray(0,1,2,3,0,1,2,3)") == GdValuePackedColorArray((0,1,2,3,0,1,2,3)))
    assert(_run("value", "PackedColorArray(0,1,2,3,0,1,2,3)") == GdValuePackedColorArray((GdValueColor((0,1,2,3)),GdValueColor((0,1,2,3)))))