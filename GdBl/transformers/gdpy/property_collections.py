from ....GdPy.core.property_collection import (
    PropertyCollection as PyPropertyCollection,
)

from ....GdPy.core.values import (
    NodePath as PyNodePath,
    StringName as PyStringName,
    Object as PyObject,
    Dictionary as PyDictionary,
    Array as PyArray,
    Vector2i as PyVector2i,
    Vector3i as PyVector3i,
    Vector4i as PyVector4i,
    Rect2i as PyRect2i,
    Vector2 as PyVector2,
    Vector3 as PyVector3,
    Vector4 as PyVector4,
    Rect2 as PyRect2,
    Plane as PyPlane,
    Color as PyColor,
    AABB as PyAABB,
    Quaternion as PyQuaternion,
    Transform2D as PyTransform2D,
    Transform3D as PyTransform3D,
    Basis as PyBasis,
    PackedInt32Array as PyPackedInt32Array,
    PackedInt64Array as PyPackedInt64Array,
    PackedFloat32Array as PyPackedFloat32Array,
    PackedFloat64Array as PyPackedFloat64Array,
    PackedStringArray as PyPackedStringArray,
    PackedVector2Array as PyPackedVector2Array,
    PackedVector3Array as PyPackedVector3Array,
    PackedVector4Array as PyPackedVector4Array,
    PackedColorArray as PyPackedColorArray,
    PackedByteArray as PyPackedByteArray,
)

from ...core.property_collection import (
    GdDictionary as BlGdDictionary,
    GdArray as BlGdArray,
    GdPrimitive as BlGdPrimitive,
    GdVector as BlGdVector,
    GdReference as BlGdReference,
    GdPropertyCollection as BlGdPropertyCollection,
)

from ._transformer import (
    PyToBlContext, 
    PyToBlRuleset, 
    PyToBlModule, 
    BlToPyContext, 
    BlToPyRuleset,
    BlToPyModule,
)


class PyToBl_Values(PyToBlModule):
    _keys = (PyNodePath, PyStringName, PyObject, PyDictionary, PyArray, PyVector2i, PyVector3i, PyVector4i, PyRect2i, PyVector2, PyVector3, PyVector4, PyRect2, PyPlane, PyColor, PyAABB, PyQuaternion, PyTransform2D, PyTransform3D, PyBasis, PyPackedInt32Array, PyPackedInt64Array, PyPackedFloat32Array, PyPackedFloat64Array, PyPackedStringArray, PyPackedVector2Array, PyPackedVector3Array, PyPackedVector4Array, PyPackedColorArray, PyPackedByteArray)
    def transform(self, c, node):
        raise NotImplementedError(c.key.get())

class BlToPy_Values(BlToPyModule):
    _keys = (BlGdDictionary, BlGdArray, BlGdPrimitive, BlGdVector)
    def transform(self, c, node):
        raise NotImplementedError(c.key.get())


_COL_py_to_bl_ruleset = PyToBlRuleset("Values :: COLLECTION",
    PyToBl_Values,
)

_COL_bl_to_py_ruleset = BlToPyRuleset("Values :: COLLECTION",
    BlToPy_Values,
)


class PyToBl_PropertyCollection(PyToBlModule):
    _keys = (PyPropertyCollection,)
    def transform(self, c, node:PyPropertyCollection):
        target = c.existing_object.get()
        t = c.rulesets.set(_COL_py_to_bl_ruleset)
        raise NotImplementedError()
        yield
        t = c.rulesets.reset(t)

class BlToPy_PropertyCollection(BlToPyModule):
    _keys = (BlGdPropertyCollection,)
    def transform(self, c, node:BlGdPropertyCollection):
        t = c.rulesets.set(_COL_bl_to_py_ruleset)
        raise NotImplementedError()
        yield
        t = c.rulesets.reset(t)


py_to_bl_ruleset = PyToBlRuleset("PropCol :: STD",

    PyToBl_PropertyCollection,
)

bl_to_py_ruleset = BlToPyRuleset("PropCol :: STD",
    BlToPy_PropertyCollection,
)