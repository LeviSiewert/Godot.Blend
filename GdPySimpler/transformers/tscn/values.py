from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule

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

class GdToPy_NodePath(GdToPyModule):
    _keys = ("nodepath",)
class PyToGd_NodePath(PyToGdModule):
    _keys = (NodePath,)

class GdToPy_StringName(GdToPyModule):
    _keys = ("stringname",)
class PyToGd_StringName(PyToGdModule):
    _keys = (StringName,)

class GdToPy_Object(GdToPyModule):
    _keys = ("object",)
class PyToGd_Object(PyToGdModule):
    _keys = (Object,)

class GdToPy_Dictionary(GdToPyModule):
    _keys = ("dictionary",)
class PyToGd_Dictionary(PyToGdModule):
    _keys = (Dictionary,)

class GdToPy_Array(GdToPyModule):
    _keys = ("array",)
class PyToGd_Array(PyToGdModule):
    _keys = (Array,)

class GdToPy_Vector2i(GdToPyModule):
    _keys = ("vector2i",)
class PyToGd_Vector2i(PyToGdModule):
    _keys = (Vector2i,)

class GdToPy_Vector3i(GdToPyModule):
    _keys = ("vector3i",)
class PyToGd_Vector3i(PyToGdModule):
    _keys = (Vector3i,)

class GdToPy_Vector4i(GdToPyModule):
    _keys = ("vector4i",)
class PyToGd_Vector4i(PyToGdModule):
    _keys = (Vector4i,)

class GdToPy_Rect2i(GdToPyModule):
    _keys = ("rect2i",)
class PyToGd_Rect2i(PyToGdModule):
    _keys = (Rect2i,)

class GdToPy_Vector2(GdToPyModule):
    _keys = ("vector2",)
class PyToGd_Vector2(PyToGdModule):
    _keys = (Vector2,)

class GdToPy_Vector3(GdToPyModule):
    _keys = ("vector3",)
class PyToGd_Vector3(PyToGdModule):
    _keys = (Vector3,)

class GdToPy_Vector4(GdToPyModule):
    _keys = ("vector4",)
class PyToGd_Vector4(PyToGdModule):
    _keys = (Vector4,)

class GdToPy_Rect2(GdToPyModule):
    _keys = ("rect2",)
class PyToGd_Rect2(PyToGdModule):
    _keys = (Rect2,)

class GdToPy_Plane(GdToPyModule):
    _keys = ("plane",)
class PyToGd_Plane(PyToGdModule):
    _keys = (Plane,)

class GdToPy_Color(GdToPyModule):
    _keys = ("color",)
class PyToGd_Color(PyToGdModule):
    _keys = (Color,)

class GdToPy_AABB(GdToPyModule):
    _keys = ("aabb",)
class PyToGd_AABB(PyToGdModule):
    _keys = (AABB,)

class GdToPy_Quaternion(GdToPyModule):
    _keys = ("quaternion",)
class PyToGd_Quaternion(PyToGdModule):
    _keys = (Quaternion,)

class GdToPy_Transform2D(GdToPyModule):
    _keys = ("transform2d",)
class PyToGd_Transform2D(PyToGdModule):
    _keys = (Transform2D,)

class GdToPy_Transform3D(GdToPyModule):
    _keys = ("transform3d",)
class PyToGd_Transform3D(PyToGdModule):
    _keys = (Transform3D,)

class GdToPy_Basis(GdToPyModule):
    _keys = ("basis",)
class PyToGd_Basis(PyToGdModule):
    _keys = (Basis,)

class GdToPy_PackedInt32Array(GdToPyModule):
    _keys = ("packedint32array",)
class PyToGd_PackedInt32Array(PyToGdModule):
    _keys = (PackedInt32Array,)

class GdToPy_PackedInt64Array(GdToPyModule):
    _keys = ("packedint64array",)
class PyToGd_PackedInt64Array(PyToGdModule):
    _keys = (PackedInt64Array,)

class GdToPy_PackedFloat32Array(GdToPyModule):
    _keys = ("packedfloat32array",)
class PyToGd_PackedFloat32Array(PyToGdModule):
    _keys = (PackedFloat32Array,)

class GdToPy_PackedFloat64Array(GdToPyModule):
    _keys = ("packedfloat64array",)
class PyToGd_PackedFloat64Array(PyToGdModule):
    _keys = (PackedFloat64Array,)

class GdToPy_PackedStringArray(GdToPyModule):
    _keys = ("packedstringarray",)
class PyToGd_PackedStringArray(PyToGdModule):
    _keys = (PackedStringArray,)

class GdToPy_PackedVector2Array(GdToPyModule):
    _keys = ("packedvector2array",)
class PyToGd_PackedVector2Array(PyToGdModule):
    _keys = (PackedVector2Array,)

class GdToPy_PackedVector3Array(GdToPyModule):
    _keys = ("packedvector3array",)
class PyToGd_PackedVector3Array(PyToGdModule):
    _keys = (PackedVector3Array,)

class GdToPy_PackedVector4Array(GdToPyModule):
    _keys = ("packedvector4array",)
class PyToGd_PackedVector4Array(PyToGdModule):
    _keys = (PackedVector4Array,)

class GdToPy_PackedColorArray(GdToPyModule):
    _keys = ("packedcolorarray",)
class PyToGd_PackedColorArray(PyToGdModule):
    _keys = (PackedColorArray,)

class GdToPy_PackedByteArray(GdToPyModule):
    _keys = ("packedbytearray",)
class PyToGd_PackedByteArray(PyToGdModule):
    _keys = (PackedByteArray,)

gd_to_py_ruleset = GdToPyRuleset("STD_Values", [
    GdToPy_NodePath,
    GdToPy_StringName,
    GdToPy_Object,
    GdToPy_Dictionary,
    GdToPy_Array,
    GdToPy_Vector2i,
    GdToPy_Vector3i,
    GdToPy_Vector4i,
    GdToPy_Rect2i,
    GdToPy_Vector2,
    GdToPy_Vector3,
    GdToPy_Vector4,
    GdToPy_Rect2,
    GdToPy_Plane,
    GdToPy_Color,
    GdToPy_AABB,
    GdToPy_Quaternion,
    GdToPy_Transform2D,
    GdToPy_Transform3D,
    GdToPy_Basis,
    GdToPy_PackedInt32Array,
    GdToPy_PackedInt64Array,
    GdToPy_PackedFloat32Array,
    GdToPy_PackedFloat64Array,
    GdToPy_PackedStringArray,
    GdToPy_PackedVector2Array,
    GdToPy_PackedVector3Array,
    GdToPy_PackedVector4Array,
    GdToPy_PackedColorArray,
    GdToPy_PackedByteArray,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Values", [
    PyToGd_NodePath,
    PyToGd_StringName,
    PyToGd_Object,
    PyToGd_Dictionary,
    PyToGd_Array,
    PyToGd_Vector2i,
    PyToGd_Vector3i,
    PyToGd_Vector4i,
    PyToGd_Rect2i,
    PyToGd_Vector2,
    PyToGd_Vector3,
    PyToGd_Vector4,
    PyToGd_Rect2,
    PyToGd_Plane,
    PyToGd_Color,
    PyToGd_AABB,
    PyToGd_Quaternion,
    PyToGd_Transform2D,
    PyToGd_Transform3D,
    PyToGd_Basis,
    PyToGd_PackedInt32Array,
    PyToGd_PackedInt64Array,
    PyToGd_PackedFloat32Array,
    PyToGd_PackedFloat64Array,
    PyToGd_PackedStringArray,
    PyToGd_PackedVector2Array,
    PyToGd_PackedVector3Array,
    PyToGd_PackedVector4Array,
    PyToGd_PackedColorArray,
    PyToGd_PackedByteArray,
])