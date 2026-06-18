from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPyRuleset, GdToPy, PyToGd, PyToGdRuleset
from .core.property_collection import PropertyCollection
from lark.visitors import Tree, Token #type:ignore
from abc import ABC, abstractmethod
from .core.primitives import Context
from typing import Any

from .values import ( 
    GdValueStringName,
    GdValueArray,
#   _GdValueArrayPackedType,
#   _GdValueArrayFixedLength,
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
#   _GdValueArrayPackedTypeComplex,
    GdValuePackedVector2Array,
    GdValuePackedVector3Array,
    GdValuePackedVector4Array,
    GdValuePackedColorArray,
    GdValueDictionary,
)




class GdToPy_Terminals(GdToPy):
    ''' Terminals Wrapper, where node's value is simple '''
    def get_keys(self,):
        return ("BOOL", "NULL", "INF", "INF_NEG", "STRING", "NUMBER", "FLOAT", "WORD", None)
    def _transform(self, key, tc, gdc, *children):
        node = tc.node.get()
        if node is None:
            return None
            # raise Exception("Node is None!")
        assert(isinstance(node, Token))
        match tc.key.get():
            case "BOOL":
                if tc.node.get() == "true": 
                    return True
                return False
            case "INF":
                return float("inf")
            case "INF_NEG":
                return -float("inf")
            case "STRING":
                return str(tc.node.get()).strip('"')
            case "NUMBER":
                return int(tc.node.get())
            case "FLOAT":
                return float(tc.node.get())
            case "WORD":
                return str(tc.node.get())
            case _:
                raise Exception("Could not match type of node", node.type)

class GdToPy_Simple(GdToPy):
    ''' Simple Children Wrapper, where node's value is typically simple to impliment '''
    def get_keys(self,):
        return ("value","type_anno","type", "property", "properties", "resource_header", "resource_body", "packed_2", "packed_2i", "packed_3", "packed_3i", "packed_4", "packed_4i", "packed_6", "packed_9", "packed_12")
    def _transform(self, key, tc, gdc, *children):
        node = tc.node.get()
        assert(isinstance(node, Tree))
        match tc.key.get():
            case "value":
                return tc.children.get()[0]
            case "type_anno":
                return tc.children.get()
            case "type":
                return tc.children.get()[0] ## expected: Str|None
            case "property":
                return tc.children.get()
            case "properties":
                props = tc.children.get()
                res = PropertyCollection()
                for kv in props:
                    if kv is None: 
                        continue
                    res[kv[0]] = kv[1]
                return res
            case "resource_header":
                return tc.children.get()[0] ## expected: PropertiesCollection
            case "resource_body":
                return tc.children.get()[0] ## expected: PropertiesCollection
            case "packed_2":
                return tc.children.get()
            case "packed_2i":
                return tc.children.get()
            case "packed_3":
                return tc.children.get()
            case "packed_3i":
                return tc.children.get()
            case "packed_4":
                return tc.children.get()
            case "packed_4i":
                return tc.children.get()
            case "packed_6":
                return tc.children.get()
            case "packed_9":
                return tc.children.get()
            case "packed_12":
                return tc.children.get()
            case _:
                raise Exception("Could not match type of tree", node.type)


class GdToPy_StringName(GdToPy):
    _keys = GdValueStringName.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueStringName:
        return GdValueStringName.parse_lark(*args, **kwargs)
class PyToGd_StringName(PyToGd):
    _keys = (GdValueStringName,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *children)->str:
        assert(isinstance(node, self._keys))
        if node.value is None:
            return f'&""'
        return f'&"{node.value}"'
        # raise NotImplementedError("Not yet implimented!")

class GdToPy_Array(GdToPy):
    _keys = GdValueArray.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueArray:
        return GdValueArray.parse_lark(*args, **kwargs)
class PyToGd_Array(PyToGd):
    _keys = (GdValueArray,)
    def _transform(self, key, tc, gdc, node:GdValueArray, *children)->str:
        raise NotImplementedError("Not yet implimented!")
          
class GdToPy_Vector2(GdToPy):
    _keys = GdValueVector2.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueVector2:
        return GdValueVector2.parse_lark(*args, **kwargs)
class PyToGd_Vector2(PyToGd):
    _keys = (GdValueVector2,)
    def _transform(self, key, tc, gdc, node:GdValueVector2, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Vector3(GdToPy):
    _keys = GdValueVector3.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueVector3:
        return GdValueVector3.parse_lark(*args, **kwargs)
class PyToGd_Vector3(PyToGd):
    _keys = (GdValueVector3,)
    def _transform(self, key, tc, gdc, node:GdValueVector3, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Vector4(GdToPy):
    _keys = GdValueVector4.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueVector4:
        return GdValueVector4.parse_lark(*args, **kwargs)
class PyToGd_Vector4(PyToGd):
    _keys = (GdValueVector4,)
    def _transform(self, key, tc, gdc, node:GdValueVector4, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Vector2i(GdToPy):
    _keys = GdValueVector2i.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueVector2i:
        return GdValueVector2i.parse_lark(*args, **kwargs)
class PyToGd_Vector2i(PyToGd):
    _keys = (GdValueVector2i,)
    def _transform(self, key, tc, gdc, node:GdValueVector2i, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Vector3i(GdToPy):
    _keys = GdValueVector3i.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueVector3i:
        return GdValueVector3i.parse_lark(*args, **kwargs)
class PyToGd_Vector3i(PyToGd):
    _keys = (GdValueVector3i,)
    def _transform(self, key, tc, gdc, node:GdValueVector3i, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Vector4i(GdToPy):
    _keys = GdValueVector4i.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueVector4i:
        return GdValueVector4i.parse_lark(*args, **kwargs)
class PyToGd_Vector4i(PyToGd):
    _keys = (GdValueVector4i,)
    def _transform(self, key, tc, gdc, node:GdValueVector4i, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Rect2(GdToPy):
    _keys = GdValueRect2.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueRect2:
        return GdValueRect2.parse_lark(*args, **kwargs)
class PyToGd_Rect2(PyToGd):
    _keys = (GdValueRect2,)
    def _transform(self, key, tc, gdc, node:GdValueRect2, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Rect2i(GdToPy):
    _keys = GdValueRect2i.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueRect2i:
        return GdValueRect2i.parse_lark(*args, **kwargs)
class PyToGd_Rect2i(PyToGd):
    _keys = (GdValueRect2i,)
    def _transform(self, key, tc, gdc, node:GdValueRect2i, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Plane(GdToPy):
    _keys = GdValuePlane.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePlane:
        return GdValuePlane.parse_lark(*args, **kwargs)
class PyToGd_Plane(PyToGd):
    _keys = (GdValuePlane,)
    def _transform(self, key, tc, gdc, node:GdValuePlane, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Color(GdToPy):
    _keys = GdValueColor.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueColor:
        return GdValueColor.parse_lark(*args, **kwargs)
class PyToGd_Color(PyToGd):
    _keys = (GdValueColor,)
    def _transform(self, key, tc, gdc, node:GdValueColor, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_AABB(GdToPy):
    _keys = GdValueAABB.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueAABB:
        return GdValueAABB.parse_lark(*args, **kwargs)
class PyToGd_AABB(PyToGd):
    _keys = (GdValueAABB,)
    def _transform(self, key, tc, gdc, node:GdValueAABB, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Quaternion(GdToPy):
    _keys = GdValueQuaternion.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueQuaternion:
        return GdValueQuaternion.parse_lark(*args, **kwargs)
class PyToGd_Quaternion(PyToGd):
    _keys = (GdValueQuaternion,)
    def _transform(self, key, tc, gdc, node:GdValueQuaternion, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Transform2D(GdToPy):
    _keys = GdValueTransform2D.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueTransform2D:
        return GdValueTransform2D.parse_lark(*args, **kwargs)
class PyToGd_Transform2D(PyToGd):
    _keys = (GdValueTransform2D,)
    def _transform(self, key, tc, gdc, node:GdValueTransform2D, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Basis(GdToPy):
    _keys = GdValueBasis.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueBasis:
        return GdValueBasis.parse_lark(*args, **kwargs)
class PyToGd_Basis(PyToGd):
    _keys = (GdValueBasis,)
    def _transform(self, key, tc, gdc, node:GdValueBasis, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Transform3D(GdToPy):
    _keys = GdValueTransform3D.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueTransform3D:
        return GdValueTransform3D.parse_lark(*args, **kwargs)
class PyToGd_Transform3D(PyToGd):
    _keys = (GdValueTransform3D,)
    def _transform(self, key, tc, gdc, node:GdValueTransform3D, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedByteArray(GdToPy):
    _keys = GdValuePackedByteArray.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedByteArray:
        return GdValuePackedByteArray.parse_lark(*args, **kwargs)
class PyToGd_PackedByteArray(PyToGd):
    _keys = (GdValuePackedByteArray,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedByteArray)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedInt32Array(GdToPy):
    _keys = GdValuePackedInt32Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedInt32Array:
        return GdValuePackedInt32Array.parse_lark(*args, **kwargs)
class PyToGd_PackedInt32Array(PyToGd):
    _keys = (GdValuePackedInt32Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedInt32Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedInt64Array(GdToPy):
    _keys = GdValuePackedInt64Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedInt64Array:
        return GdValuePackedInt64Array.parse_lark(*args, **kwargs)
class PyToGd_PackedInt64Array(PyToGd):
    _keys = (GdValuePackedInt64Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedInt64Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedFloat32Array(GdToPy):
    _keys = GdValuePackedFloat32Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedFloat32Array:
        return GdValuePackedFloat32Array.parse_lark(*args, **kwargs)
class PyToGd_PackedFloat32Array(PyToGd):
    _keys = (GdValuePackedFloat32Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedFloat32Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedFloat64Array(GdToPy):
    _keys = GdValuePackedFloat64Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedFloat64Array:
        return GdValuePackedFloat64Array.parse_lark(*args, **kwargs)
class PyToGd_PackedFloat64Array(PyToGd):
    _keys = (GdValuePackedFloat64Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedFloat64Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedStringArray(GdToPy):
    _keys = GdValuePackedStringArray.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedStringArray:
        return GdValuePackedStringArray.parse_lark(*args, **kwargs)
class PyToGd_PackedStringArray(PyToGd):
    _keys = (GdValuePackedStringArray,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedStringArray)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedVector2Array(GdToPy):
    _keys = GdValuePackedVector2Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedVector2Array:
        return GdValuePackedVector2Array.parse_lark(*args, **kwargs)
class PyToGd_PackedVector2Array(PyToGd):
    _keys = (GdValuePackedVector2Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedVector2Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedVector3Array(GdToPy):
    _keys = GdValuePackedVector3Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedVector3Array:
        return GdValuePackedVector3Array.parse_lark(*args, **kwargs)
class PyToGd_PackedVector3Array(PyToGd):
    _keys = (GdValuePackedVector3Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedVector3Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedVector4Array(GdToPy):
    _keys = GdValuePackedVector4Array.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedVector4Array:
        return GdValuePackedVector4Array.parse_lark(*args, **kwargs)
class PyToGd_PackedVector4Array(PyToGd):
    _keys = (GdValuePackedVector4Array,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedVector4Array)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_PackedColorArray(GdToPy):
    _keys = GdValuePackedColorArray.lark_keys()
    def _transform(self, *args, **kwargs)->GdValuePackedColorArray:
        return GdValuePackedColorArray.parse_lark(*args, **kwargs)
class PyToGd_PackedColorArray(PyToGd):
    _keys = (GdValuePackedColorArray,)
    def _transform(self, key, tc, gdc, node:GdValueStringName, *GdValuePackedColorArray)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_Dictionary(GdToPy):
    _keys = GdValueDictionary.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueDictionary:
        return GdValueDictionary.parse_lark(*args, **kwargs)
class PyToGd_Dictionary(PyToGd):
    _keys = (GdValueDictionary,)
    def _transform(self, key, tc, gdc, node:GdValueDictionary, *children)->str:
        raise NotImplementedError("Not yet implimented!")



gd_to_py_ruleset = GdToPyRuleset((
    GdToPy_Terminals(),
    GdToPy_Simple(),
    GdToPy_StringName(),
    GdToPy_Array(),
    GdToPy_Vector2(),
    GdToPy_Vector3(),
    GdToPy_Vector4(),
    GdToPy_Vector2i(),
    GdToPy_Vector3i(),
    GdToPy_Vector4i(),
    GdToPy_Rect2(),
    GdToPy_Rect2i(),
    GdToPy_Plane(),
    GdToPy_Color(),
    GdToPy_AABB(),
    GdToPy_Quaternion(),
    GdToPy_Transform2D(),
    GdToPy_Basis(),
    GdToPy_Transform3D(),
    GdToPy_PackedByteArray(),
    GdToPy_PackedInt32Array(),
    GdToPy_PackedInt64Array(),
    GdToPy_PackedFloat32Array(),
    GdToPy_PackedFloat64Array(),
    GdToPy_PackedStringArray(),
    GdToPy_PackedVector2Array(),
    GdToPy_PackedVector3Array(),
    GdToPy_PackedVector4Array(),
    GdToPy_PackedColorArray(),
    GdToPy_Dictionary(),
    ))


py_to_gd_ruleset = PyToGdRuleset((
    PyToGd_StringName(),
    PyToGd_Array(),
    PyToGd_Vector2(),
    PyToGd_Vector3(),
    PyToGd_Vector4(),
    PyToGd_Vector2i(),
    PyToGd_Vector3i(),
    PyToGd_Vector4i(),
    PyToGd_Rect2(),
    PyToGd_Rect2i(),
    PyToGd_Plane(),
    PyToGd_Color(),
    PyToGd_AABB(),
    PyToGd_Quaternion(),
    PyToGd_Transform2D(),
    PyToGd_Basis(),
    PyToGd_Transform3D(),
    PyToGd_PackedByteArray(),
    PyToGd_PackedInt32Array(),
    PyToGd_PackedInt64Array(),
    PyToGd_PackedFloat32Array(),
    PyToGd_PackedFloat64Array(),
    PyToGd_PackedStringArray(),
    PyToGd_PackedVector2Array(),
    PyToGd_PackedVector3Array(),
    PyToGd_PackedVector4Array(),
    PyToGd_PackedColorArray(),
    PyToGd_Dictionary(),
    ))
