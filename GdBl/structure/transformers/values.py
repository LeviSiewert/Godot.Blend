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

from ..core.properties import BlProperty

class BlToPyRuleset_Property(BlToPyRuleset):
    ''' Key is stored on BlProperty in a different way than other Blender objects '''
    def _key_extractor(self, key):
        if isinstance(key, BlProperty):
            return (key.type,)
        return super()._key_extractor(key)


class PyToBl_Terminals(PyToBl):
    _keys = (bool,float,int,str)
    def transform(self, node, c, *args, **kwargs):
        prop : BlProperty = c.existing_object.get()
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
    def transform(self, node:BlProperty, c, *args, **kwargs):
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
        target : BlProperty = c.existing_object.get()
        target.type = "GdValueStringName"
        target.val_str = node.value
        return target 
class BlToPy_GdValueStringName(BlToPy):
    _keys = ("GdValueStringName",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        return GdValueStringName(node.val_str)

class PyToBl_GdValueArray(PyToBl):
    _keys = (GdValueArray,)
    def transform(self, node:GdValueArray, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueArray: ", node, target)
class BlToPy_GdValueArray(BlToPy):
    _keys = ("GdValueArray",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueArray: ", node)
    
class PyToBl_GdValueVector2(PyToBl):
    _keys = (GdValueVector2,)
    def transform(self, node:GdValueVector2, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueVector2: ", node, target)
class BlToPy_GdValueVector2(BlToPy):
    _keys = ("GdValueVector2",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueVector2: ", node)
    
class PyToBl_GdValueVector3(PyToBl):
    _keys = (GdValueVector3,)
    def transform(self, node:GdValueVector3, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueVector3: ", node, target)
class BlToPy_GdValueVector3(BlToPy):
    _keys = ("GdValueVector3",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueVector3: ", node)

class PyToBl_GdValueVector4(PyToBl):
    _keys = (GdValueVector4,)
    def transform(self, node:GdValueVector4, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueVector4: ", node, target)
class BlToPy_GdValueVector4(BlToPy):
    _keys = ("GdValueVector4",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueVector4: ", node)

class PyToBl_GdValueVector2i(PyToBl):
    _keys = (GdValueVector2i,)
    def transform(self, node:GdValueVector2i, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueVector2i: ", node, target)
class BlToPy_GdValueVector2i(BlToPy):
    _keys = ("GdValueVector2i",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueVector2i: ", node)
    
class PyToBl_GdValueVector3i(PyToBl):
    _keys = (GdValueVector3i,)
    def transform(self, node:GdValueVector3i, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueVector3i: ", node, target)
class BlToPy_GdValueVector3i(BlToPy):
    _keys = ("GdValueVector3i",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueVector3i: ", node)

class PyToBl_GdValueVector4i(PyToBl):
    _keys = (GdValueVector4i,)
    def transform(self, node:GdValueVector4i, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueVector4i: ", node, target)
class BlToPy_GdValueVector4i(BlToPy):
    _keys = ("GdValueVector4i",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueVector4i: ", node)

class PyToBl_GdValueRect2(PyToBl):
    _keys = (GdValueRect2,)
    def transform(self, node:GdValueRect2, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueRect2: ", node, target)
class BlToPy_GdValueRect2(BlToPy):
    _keys = ("GdValueRect2",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueRect2: ", node)

class PyToBl_GdValueRect2i(PyToBl):
    _keys = (GdValueRect2i,)
    def transform(self, node:GdValueRect2i, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueRect2i: ", node, target)
class BlToPy_GdValueRect2i(BlToPy):
    _keys = ("GdValueRect2i",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueRect2i: ", node)

class PyToBl_GdValuePlane(PyToBl):
    _keys = (GdValuePlane,)
    def transform(self, node:GdValuePlane, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePlane: ", node, target)
class BlToPy_GdValuePlane(BlToPy):
    _keys = ("GdValuePlane",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePlane: ", node)

class PyToBl_GdValueColor(PyToBl):
    _keys = (GdValueColor,)
    def transform(self, node:GdValueColor, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueColor: ", node, target)
class BlToPy_GdValueColor(BlToPy):
    _keys = ("GdValueColor",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueColor: ", node)

class PyToBl_GdValueAABB(PyToBl):
    _keys = (GdValueAABB,)
    def transform(self, node:GdValueAABB, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueAABB: ", node, target)
class BlToPy_GdValueAABB(BlToPy):
    _keys = ("GdValueAABB",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueAABB: ", node)

class PyToBl_GdValueQuaternion(PyToBl):
    _keys = (GdValueQuaternion,)
    def transform(self, node:GdValueQuaternion, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueQuaternion: ", node, target)
class BlToPy_GdValueQuaternion(BlToPy):
    _keys = ("GdValueQuaternion",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueQuaternion: ", node)

class PyToBl_GdValueTransform2D(PyToBl):
    _keys = (GdValueTransform2D,)
    def transform(self, node:GdValueTransform2D, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueTransform2D: ", node, target)
class BlToPy_GdValueTransform2D(BlToPy):
    _keys = ("GdValueTransform2D",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueTransform2D: ", node)

class PyToBl_GdValueBasis(PyToBl):
    _keys = (GdValueBasis,)
    def transform(self, node:GdValueBasis, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueBasis: ", node, target)
class BlToPy_GdValueBasis(BlToPy):
    _keys = ("GdValueBasis",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueBasis: ", node)

class PyToBl_GdValueTransform3D(PyToBl):
    _keys = (GdValueTransform3D,)
    def transform(self, node:GdValueTransform3D, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueTransform3D: ", node, target)
class BlToPy_GdValueTransform3D(BlToPy):
    _keys = ("GdValueTransform3D",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueTransform3D: ", node)

class PyToBl_GdValuePackedByteArray(PyToBl):
    _keys = (GdValuePackedByteArray,)
    def transform(self, node:GdValuePackedByteArray, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedByteArray: ", node, target)
class BlToPy_GdValuePackedByteArray(BlToPy):
    _keys = ("GdValuePackedByteArray",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedByteArray: ", node)

class PyToBl_GdValuePackedInt32Array(PyToBl):
    _keys = (GdValuePackedInt32Array,)
    def transform(self, node:GdValuePackedInt32Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedInt32Array: ", node, target)
class BlToPy_GdValuePackedInt32Array(BlToPy):
    _keys = ("GdValuePackedInt32Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedInt32Array: ", node)

class PyToBl_GdValuePackedInt64Array(PyToBl):
    _keys = (GdValuePackedInt64Array,)
    def transform(self, node:GdValuePackedInt64Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedInt64Array: ", node, target)
class BlToPy_GdValuePackedInt64Array(BlToPy):
    _keys = ("GdValuePackedInt64Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedInt64Array: ", node)

class PyToBl_GdValuePackedFloat32Array(PyToBl):
    _keys = (GdValuePackedFloat32Array,)
    def transform(self, node:GdValuePackedFloat32Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedFloat32Array: ", node, target)
class BlToPy_GdValuePackedFloat32Array(BlToPy):
    _keys = ("GdValuePackedFloat32Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedFloat32Array: ", node)

class PyToBl_GdValuePackedFloat64Array(PyToBl):
    _keys = (GdValuePackedFloat64Array,)
    def transform(self, node:GdValuePackedFloat64Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedFloat64Array: ", node, target)
class BlToPy_GdValuePackedFloat64Array(BlToPy):
    _keys = ("GdValuePackedFloat64Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedFloat64Array: ", node)

class PyToBl_GdValuePackedStringArray(PyToBl):
    _keys = (GdValuePackedStringArray,)
    def transform(self, node:GdValuePackedStringArray, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedStringArray: ", node, target)
class BlToPy_GdValuePackedStringArray(BlToPy):
    _keys = ("GdValuePackedStringArray",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedStringArray: ", node)

class PyToBl_GdValuePackedVector2Array(PyToBl):
    _keys = (GdValuePackedVector2Array,)
    def transform(self, node:GdValuePackedVector2Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedVector2Array: ", node, target)
class BlToPy_GdValuePackedVector2Array(BlToPy):
    _keys = ("GdValuePackedVector2Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedVector2Array: ", node)

class PyToBl_GdValuePackedVector3Array(PyToBl):
    _keys = (GdValuePackedVector3Array,)
    def transform(self, node:GdValuePackedVector3Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedVector3Array: ", node, target)
class BlToPy_GdValuePackedVector3Array(BlToPy):
    _keys = ("GdValuePackedVector3Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedVector3Array: ", node)

class PyToBl_GdValuePackedVector4Array(PyToBl):
    _keys = (GdValuePackedVector4Array,)
    def transform(self, node:GdValuePackedVector4Array, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedVector4Array: ", node, target)
class BlToPy_GdValuePackedVector4Array(BlToPy):
    _keys = ("GdValuePackedVector4Array",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedVector4Array: ", node)

class PyToBl_GdValuePackedColorArray(PyToBl):
    _keys = (GdValuePackedColorArray,)
    def transform(self, node:GdValuePackedColorArray, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValuePackedColorArray: ", node, target)
class BlToPy_GdValuePackedColorArray(BlToPy):
    _keys = ("GdValuePackedColorArray",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValuePackedColorArray: ", node)

class PyToBl_GdValueDictionary(PyToBl):
    _keys = (GdValueDictionary,)
    def transform(self, node:GdValueDictionary, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        raise NotImplementedError("PyToBl GdValueDictionary: ", node, target)
class BlToPy_GdValueDictionary(BlToPy):
    _keys = ("GdValueDictionary",)
    def transform(self, node:BlProperty, c, *args, **kwargs):
        raise NotImplementedError("PyToBl GdValueDictionary: ", node)


bl_to_py_ruleset = BlToPyRuleset_Property((
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
py_to_bl_ruleset = PyToBlRuleset((
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