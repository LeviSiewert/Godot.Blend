from typing import Type

from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

from ....GdPy.structure.values import (
    GdValueStringName,
    GdValueArray,
    GdValueVector2,
    GdValueVector3,
    GdValueVector4,
    GdValueVector2i,
    GdValueVector3i,
    GdValueVector4i,
    GdValueRect2,
    GdValueRect2i,
    GdValuePlane,
    GdValueColor,
    GdValueAABB,
    GdValueQuaternion,
    GdValueTransform2D,
    GdValueBasis,
    GdValueTransform3D,
    GdValuePackedByteArray,
    GdValuePackedInt32Array,
    GdValuePackedInt64Array,
    GdValuePackedFloat32Array,
    GdValuePackedFloat64Array,
    GdValuePackedStringArray,
    GdValuePackedVector2Array,
    GdValuePackedVector3Array,
    GdValuePackedVector4Array,
    GdValuePackedColorArray,
    GdValueDictionary,
)

from ..core.properties import BlPrimitive

class BlToPyRuleset_Property(BlToPyRuleset):
    ''' Key is stored on BlPrimitive in a different way than other Blender objects '''
    def _key_extractor(self, key):
        if isinstance(key, BlPrimitive):
            return (key.type,)
        return super()._key_extractor(key)


class PyToBl_Terminals(PyToBl):
    _keys = (bool,float,int,str)
    def transform(self, node, c, *args, **kwargs):
        prop : BlPrimitive = c.existing_object.get()
        x = c.key.get()
        if x is bool:
            prop.type = "BOOL"
            prop.val_boolean = node
        elif x is float:
            prop.type = "FLOAT"
            prop.val_float = node
        elif x is int:
            prop.type = "INT"
            prop.val_int = node
        elif x is str:
            prop.type = "STR"
            prop.val_str = node
        raise KeyError()
class BlToPy_Terminals(BlToPy):
    _keys = ("BOOL","FLOAT","INT","STR")
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        match c.key.get():
            case "BOOL":
                return node.val_boolean
            case "FLOAT":
                return node.val_float
            case "INT":
                return node.val_int
            case "STR":
                return node.val_str
        raise KeyError()
    
class PyToBl_GdValueStringName(PyToBl):
    _keys = (GdValueStringName,)
    def transform(self, node:GdValueStringName, c, *args, **kwargs):
        target : BlPrimitive = c.existing_object.get()
        target.type = "GdValueStringName"
        target.val_str = node.value
        return target 
class BlToPy_GdValueStringName(BlToPy):
    _keys = ("GdValueStringName",)
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        return GdValueStringName(node.val_str)

class PyToBl_GdValueArray(PyToBl):
    _keys = (GdValueArray,)
    def transform(self, node:GdValueArray, c, *args, **kwargs):
        target : BlPrimitive = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueArray: ", node, target)
class BlToPy_GdValueArray(BlToPy):
    _keys = ("GdValueArray",)
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueArray: ", node)
    
class _PyToBl_IntArray(PyToBl):
    _blkey : str
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("PyToBl Generic Int Array: ", node)
class _BlToPy_IntArray(BlToPy):
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("BlToPy Generic Int Array: ", node)

class _PyToBl_FloatArray(PyToBl):
    _blkey : str
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("BlToPy Generic Float Array: ", node)
class _BlToPy_FloatArray(BlToPy):
    _key : str
    _type : Type
    def get_keys(self):
        return (self._key,)
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("PyToBl Generic Float Array: ", node)

class PyToBl_GdValueVector2(_PyToBl_FloatArray):
    _keys = (GdValueVector2,)
    _blkey = "GdValueVector2"
class BlToPy_GdValueVector2(_BlToPy_FloatArray):
    _type = GdValueVector2
    _key = "GdValueVector2"
    
class PyToBl_GdValueVector3(_PyToBl_FloatArray):
    _keys = (GdValueVector3,)
class BlToPy_GdValueVector3(_BlToPy_FloatArray):
    _type = GdValueVector3
    _key = "GdValueVector3"

class PyToBl_GdValueVector4(_PyToBl_FloatArray):
    _keys = (GdValueVector4,)
    _blkey = "GdValueVector4"
class BlToPy_GdValueVector4(_BlToPy_FloatArray):
    _type = GdValueVector4
    _key = "GdValueVector4"

class PyToBl_GdValueVector2i(_PyToBl_IntArray):
    _blkey = "GdValueVector2i"
    _keys = (GdValueVector2i,)
class BlToPy_GdValueVector2i(_BlToPy_IntArray):
    _key = "GdValueVector2i"
    
class PyToBl_GdValueVector3i(_PyToBl_IntArray):
    _blkey = "GdValueVector3i"
    _keys = (GdValueVector3i,)
class BlToPy_GdValueVector3i(_BlToPy_IntArray):
    _key = "GdValueVector3i"

class PyToBl_GdValueVector4i(_PyToBl_IntArray):
    _blkey = "GdValueVector4i"
    _keys = (GdValueVector4i,)
class BlToPy_GdValueVector4i(_BlToPy_IntArray):
    _key = "GdValueVector4i"

class PyToBl_GdValueRect2(_PyToBl_FloatArray):
    _keys = (GdValueRect2,)
    _blkey = "GdValueRect2"
class BlToPy_GdValueRect2(_BlToPy_FloatArray):
    _type = GdValueRect2
    _key = "GdValueRect2"

class PyToBl_GdValueRect2i(_PyToBl_IntArray):
    _blkey = "GdValueRect2i"
    _keys = (GdValueRect2i,)
class BlToPy_GdValueRect2i(_BlToPy_IntArray):
    _type = GdValueRect2i
    _key = "GdValueRect2i"

class PyToBl_GdValuePlane(_PyToBl_FloatArray):
    _keys = (GdValuePlane,)
    _blkey = "GdValuePlane"
class BlToPy_GdValuePlane(_BlToPy_FloatArray):
    _type = GdValuePlane
    _key = "GdValuePlane"

class PyToBl_GdValueColor(_PyToBl_FloatArray):
    _keys = (GdValueColor,)
    _blkey = "GdValueColor"
class BlToPy_GdValueColor(_BlToPy_FloatArray):
    _type = GdValueColor
    _key = "GdValueColor"

class PyToBl_GdValueAABB(_PyToBl_FloatArray):
    _keys = (GdValueAABB,)
    _blkey = "GdValueAABB"
class BlToPy_GdValueAABB(_BlToPy_FloatArray):
    _type = GdValueAABB
    _key = "GdValueAABB"

class PyToBl_GdValueQuaternion(_PyToBl_FloatArray):
    _keys = (GdValueQuaternion,)
    _blkey = "GdValueQuaternion"
class BlToPy_GdValueQuaternion(_BlToPy_FloatArray):
    _type = GdValueQuaternion
    _key = "GdValueQuaternion"

class PyToBl_GdValueTransform2D(_PyToBl_FloatArray):
    _keys = (GdValueTransform2D,)
    _blkey = "GdValueTransform2D"
class BlToPy_GdValueTransform2D(_BlToPy_FloatArray):
    _type = GdValueTransform2D
    _key = "GdValueTransform2D"

class PyToBl_GdValueBasis(_PyToBl_FloatArray):
    _keys = (GdValueBasis,)
    _blkey = "GdValueBasis"
class BlToPy_GdValueBasis(_BlToPy_FloatArray):
    _type = GdValueBasis
    _key = "GdValueBasis"

class PyToBl_GdValueTransform3D(_PyToBl_FloatArray):
    _keys = (GdValueTransform3D,)
    _blkey = "GdValueTransform3D"
class BlToPy_GdValueTransform3D(_BlToPy_FloatArray):
    _type = GdValueTransform3D
    _key = "GdValueTransform3D"
    
class _PyToBl_PackedArray(PyToBl):
    _keys = (GdValuePackedByteArray,)
    def transform(self, node:GdValuePackedByteArray, c, *args, **kwargs):
        target : BlPrimitive = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedByteArray: ", node, target)
class _BlToPy_PackedArray(BlToPy):
    _key : str
    def get_keys(self):
        return (self._key,)
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedByteArray: ", node)

class PyToBl_GdValuePackedByteArray(_PyToBl_PackedArray):
    _blkey = "GdValuePackedByteArray"
    _keys = (GdValuePackedByteArray,)
class BlToPy_GdValuePackedByteArray(_BlToPy_PackedArray):
    _key = "GdValuePackedByteArray"

class PyToBl_GdValuePackedInt32Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedInt32Array"
    _keys = (GdValuePackedInt32Array,)
class BlToPy_GdValuePackedInt32Array(_BlToPy_PackedArray):
    _key = "GdValuePackedInt32Array"

class PyToBl_GdValuePackedInt64Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedInt64Array"
    _keys = (GdValuePackedInt64Array,)
class BlToPy_GdValuePackedInt64Array(_BlToPy_PackedArray):
    _key = "GdValuePackedInt64Array"

class PyToBl_GdValuePackedFloat32Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedFloat32Array"
    _keys = (GdValuePackedFloat32Array,)
class BlToPy_GdValuePackedFloat32Array(_BlToPy_PackedArray):
    _key = "GdValuePackedFloat32Array"

class PyToBl_GdValuePackedFloat64Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedFloat64Array"
    _keys = (GdValuePackedFloat64Array,)
class BlToPy_GdValuePackedFloat64Array(_BlToPy_PackedArray):
    _key = "GdValuePackedFloat64Array"

class PyToBl_GdValuePackedStringArray(_PyToBl_PackedArray):
    _blkey = "GdValuePackedStringArray"
    _keys = (GdValuePackedStringArray,)
class BlToPy_GdValuePackedStringArray(_BlToPy_PackedArray):
    _key = "GdValuePackedStringArray"

class PyToBl_GdValuePackedVector2Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedVector2Array"
    _keys = (GdValuePackedVector2Array,)
class BlToPy_GdValuePackedVector2Array(_BlToPy_PackedArray):
    _key = "GdValuePackedVector2Array"

class PyToBl_GdValuePackedVector3Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedVector3Array"
    _keys = (GdValuePackedVector3Array,)
class BlToPy_GdValuePackedVector3Array(_BlToPy_PackedArray):
    _key = "GdValuePackedVector3Array"

class PyToBl_GdValuePackedVector4Array(_PyToBl_PackedArray):
    _blkey = "GdValuePackedVector4Array"
    _keys = (GdValuePackedVector4Array,)
class BlToPy_GdValuePackedVector4Array(_BlToPy_PackedArray):
    _key = "GdValuePackedVector4Array"

class PyToBl_GdValuePackedColorArray(_PyToBl_PackedArray):
    _blkey = "GdValuePackedColorArray"
    _keys = (GdValuePackedColorArray,)
class BlToPy_GdValuePackedColorArray(_BlToPy_PackedArray):
    _key = "GdValuePackedColorArray"

class PyToBl_GdValueDictionary(PyToBl):
    _keys = (GdValueDictionary,)
    def transform(self, node:GdValueDictionary, c, *args, **kwargs):
        target : BlPrimitive = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueDictionary: ", node, target)
class BlToPy_GdValueDictionary(BlToPy):
    _keys = ("GdValueDictionary",)
    def transform(self, node:BlPrimitive, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueDictionary: ", node)


bl_to_py_ruleset = BlToPyRuleset_Property(__file__,(
    PyToBl_Terminals(),
    BlToPy_GdValueStringName(),
    BlToPy_GdValueArray(),
    BlToPy_GdValueVector2(),
    BlToPy_GdValueVector3(),
    BlToPy_GdValueVector4(),
    BlToPy_GdValueVector2i(),
    BlToPy_GdValueVector3i(),
    BlToPy_GdValueVector4i(),
    BlToPy_GdValueRect2(),
    BlToPy_GdValueRect2i(),
    BlToPy_GdValuePlane(),
    BlToPy_GdValueColor(),
    BlToPy_GdValueAABB(),
    BlToPy_GdValueQuaternion(),
    BlToPy_GdValueTransform2D(),
    BlToPy_GdValueBasis(),
    BlToPy_GdValueTransform3D(),
    BlToPy_GdValuePackedByteArray(),
    BlToPy_GdValuePackedInt32Array(),
    BlToPy_GdValuePackedInt64Array(),
    BlToPy_GdValuePackedFloat32Array(),
    BlToPy_GdValuePackedFloat64Array(),
    BlToPy_GdValuePackedStringArray(),
    BlToPy_GdValuePackedVector2Array(),
    BlToPy_GdValuePackedVector3Array(),
    BlToPy_GdValuePackedVector4Array(),
    BlToPy_GdValuePackedColorArray(),
    BlToPy_GdValueDictionary(),
))
py_to_bl_ruleset = PyToBlRuleset(__file__,(
    BlToPy_Terminals(),
    PyToBl_GdValueStringName(),
    PyToBl_GdValueArray(),
    PyToBl_GdValueVector2(),
    PyToBl_GdValueVector3(),
    PyToBl_GdValueVector4(),
    PyToBl_GdValueVector2i(),
    PyToBl_GdValueVector3i(),
    PyToBl_GdValueVector4i(),
    PyToBl_GdValueRect2(),
    PyToBl_GdValueRect2i(),
    PyToBl_GdValuePlane(),
    PyToBl_GdValueColor(),
    PyToBl_GdValueAABB(),
    PyToBl_GdValueQuaternion(),
    PyToBl_GdValueTransform2D(),
    PyToBl_GdValueBasis(),
    PyToBl_GdValueTransform3D(),
    PyToBl_GdValuePackedByteArray(),
    PyToBl_GdValuePackedInt32Array(),
    PyToBl_GdValuePackedInt64Array(),
    PyToBl_GdValuePackedFloat32Array(),
    PyToBl_GdValuePackedFloat64Array(),
    PyToBl_GdValuePackedStringArray(),
    PyToBl_GdValuePackedVector2Array(),
    PyToBl_GdValuePackedVector3Array(),
    PyToBl_GdValuePackedVector4Array(),
    PyToBl_GdValuePackedColorArray(),
    PyToBl_GdValueDictionary(),
))