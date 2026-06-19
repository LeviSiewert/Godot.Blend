from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPyRuleset, GdToPy, PyToGd, PyToGdRuleset
from .core.property_collection import PropertyCollection
from lark.visitors import Tree, Token #type:ignore
from abc import ABC, abstractmethod
from .core.primitives import Context
from typing import Any, Type

from .values import ( 
    GdValueStringName,
    GdValueArray,
#   _GdValueArrayPackedType,
#   _FixedTypeArray,
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

class GdToPy_Array(GdToPy):
    _keys = GdValueArray.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueArray:
        return GdValueArray.parse_lark(*args, **kwargs)
class PyToGd_Array(PyToGd):
    _keys = (GdValueArray,)
    def transform(self, node:GdValueArray, tc:TransformerContext, c:Context, *args, **kwargs):
        yield node.value
        children = tc.children.get()
        if children is None:
            children = tuple()
        if node._type == "Variant":
            return f'[{",".join(children)}]'
        return f'Array[{node._type}]({",".join(children)})'

## ARRAY TYPES:

class _GdToPy_FixedTypeArray(GdToPy):
    _type:Type
    def transform(self, node, tc, c, *args, **kwargs):
        children = tc.children.get()
        if len(children) == 0:
            return self._type()
        return self._type(children)
class _PyToGd_FixedTypeArray(PyToGd):
    _text_key : str 
    _type:Type
    
    def get_keys(self):
        return (self._type,)
    def transform(self, node:Any, tc:TransformerContext, c:Context, *args, **kwargs):
        yield node.value
        return f"{self._text_key}({",".join(tc.children.get())})"
    

class GdToPy_Vector2(_GdToPy_FixedTypeArray):
    _type = GdValueVector2
    _keys = ("vector2",)
class PyToGd_Vector2(_PyToGd_FixedTypeArray):
    _type = GdValueVector2
    _text_key = "Vector2"

class GdToPy_Vector3(_GdToPy_FixedTypeArray):
    _type = GdValueVector3
    _keys = ("vector3",)
class PyToGd_Vector3(_PyToGd_FixedTypeArray):
    _type = GdValueVector3
    _text_key = "Vector3"

class GdToPy_Vector4(_GdToPy_FixedTypeArray):
    _type = GdValueVector4
    _keys = ("vector4",)
class PyToGd_Vector4(_PyToGd_FixedTypeArray):
    _type = GdValueVector4
    _text_key = "Vector4"

class GdToPy_Vector2i(_GdToPy_FixedTypeArray):
    _type = GdValueVector2i
    _keys = ("vector2i",)
class PyToGd_Vector2i(_PyToGd_FixedTypeArray):
    _type = GdValueVector2i
    _text_key = "Vector2i"

class GdToPy_Vector3i(_GdToPy_FixedTypeArray):
    _type = GdValueVector3i
    _keys = ("vector3i",)
class PyToGd_Vector3i(_PyToGd_FixedTypeArray):
    _type = GdValueVector3i
    _text_key = "Vector3i"

class GdToPy_Vector4i(_GdToPy_FixedTypeArray):
    _type = GdValueVector4i
    _keys = ("vector4i",)
class PyToGd_Vector4i(_PyToGd_FixedTypeArray):
    _type = GdValueVector4i
    _text_key = "Vector4i"

class GdToPy_Rect2(_GdToPy_FixedTypeArray):
    _type = GdValueRect2
    _keys = ("rect2",)
class PyToGd_Rect2(_PyToGd_FixedTypeArray):
    _type = GdValueRect2
    _text_key = "Rect2"

class GdToPy_Rect2i(_GdToPy_FixedTypeArray):
    _type = GdValueRect2i
    _keys = ("rect2i",)
class PyToGd_Rect2i(_PyToGd_FixedTypeArray):
    _type = GdValueRect2i
    _text_key = "Rect2i"

class GdToPy_Plane(_GdToPy_FixedTypeArray):
    _type = GdValuePlane
    _keys = ("plane",)
class PyToGd_Plane(_PyToGd_FixedTypeArray):
    _type = GdValuePlane
    _text_key = "Plane"

class GdToPy_Color(_GdToPy_FixedTypeArray):
    _type = GdValueColor
    _keys = ("color",)
class PyToGd_Color(_PyToGd_FixedTypeArray):
    _type = GdValueColor
    _text_key = "Color"

class GdToPy_AABB(_GdToPy_FixedTypeArray):
    _type = GdValueAABB
    _keys = ("aabb",)
class PyToGd_AABB(_PyToGd_FixedTypeArray):
    _type = GdValueAABB
    _text_key = "AABB"

class GdToPy_Quaternion(_GdToPy_FixedTypeArray):
    _type = GdValueQuaternion
    _keys = ("quaternion",)
class PyToGd_Quaternion(_PyToGd_FixedTypeArray):
    _type = GdValueQuaternion
    _text_key = "Quaternion"

class GdToPy_Transform2D(_GdToPy_FixedTypeArray):
    _type = GdValueTransform2D
    _keys = ("transform2d",)
class PyToGd_Transform2D(_PyToGd_FixedTypeArray):
    _type = GdValueTransform2D
    _text_key = "Transform2D"

class GdToPy_Basis(_GdToPy_FixedTypeArray):
    _type = GdValueBasis
    _keys = ("basis",)
class PyToGd_Basis(_PyToGd_FixedTypeArray):
    _type = GdValueBasis
    _text_key = "Basis"

class GdToPy_Transform3D(_GdToPy_FixedTypeArray):
    _type = GdValueTransform3D
    _keys = ("transform3d",)
class PyToGd_Transform3D(_PyToGd_FixedTypeArray):
    _type = GdValueTransform3D
    _text_key = "Transform3D"

class GdToPy_PackedByteArray(_GdToPy_FixedTypeArray):
    _type = GdValuePackedByteArray
    _keys = ("packedbytearray",)
class PyToGd_PackedByteArray(_PyToGd_FixedTypeArray):
    _type = GdValuePackedByteArray
    _text_key = "PackedByteArray"

class GdToPy_PackedInt32Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedInt32Array
    _keys = ("packedint32array",)
class PyToGd_PackedInt32Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedInt32Array
    _text_key = "PackedInt32Array"

class GdToPy_PackedInt64Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedInt64Array
    _keys = ("packedint64array",)
class PyToGd_PackedInt64Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedInt64Array
    _text_key = "PackedInt64Array"

class GdToPy_PackedFloat32Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedFloat32Array
    _keys = ("packedfloat32array",)
class PyToGd_PackedFloat32Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedFloat32Array
    _text_key = "PackedFloat32Array"

class GdToPy_PackedFloat64Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedFloat64Array
    _keys = ("packedfloat64array",)
class PyToGd_PackedFloat64Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedFloat64Array
    _text_key = "PackedFloat64Array"

class GdToPy_PackedStringArray(_GdToPy_FixedTypeArray):
    _type = GdValuePackedStringArray
    _keys = ("packedstringarray",)
class PyToGd_PackedStringArray(_PyToGd_FixedTypeArray):
    _type = GdValuePackedStringArray
    _text_key = "PackedStringArray"

class GdToPy_PackedVector2Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedVector2Array
    _keys = ("packedvector2array",)
class PyToGd_PackedVector2Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedVector2Array
    _text_key = "PackedVector2Array"

class GdToPy_PackedVector3Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedVector3Array
    _keys = ("packedvector3array",)
class PyToGd_PackedVector3Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedVector3Array
    _text_key = "PackedVector3Array"

class GdToPy_PackedVector4Array(_GdToPy_FixedTypeArray):
    _type = GdValuePackedVector4Array
    _keys = ("packedvector4array",)
class PyToGd_PackedVector4Array(_PyToGd_FixedTypeArray):
    _type = GdValuePackedVector4Array
    _text_key = "PackedVector4Array"

class GdToPy_PackedColorArray(_GdToPy_FixedTypeArray):
    _type = GdValuePackedColorArray
    _keys = ("packedcolorarray",)
class PyToGd_PackedColorArray(_PyToGd_FixedTypeArray):
    _type = GdValuePackedColorArray
    _text_key = "PackedColorArray"


## DICTIONARY:

class GdToPy_Dictionary(GdToPy):
    _keys = GdValueDictionary.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueDictionary:
        return GdValueDictionary.parse_lark(*args, **kwargs)
class PyToGd_Dictionary(PyToGd):
    _keys = (GdValueDictionary,)
    
    def transform(self, node:GdValueArray, tc:TransformerContext, c:Context, *args, **kwargs):
        yield (*node.value.values(), *node.value.items())

        conv : dict = tc.children_map.get()

        reps = []
        for k,v in node.value.items():
            reps.append(f"{conv[k]}:{conv[v]}") 
        
        inner = '{' + ",".join(reps) + "}" 
        if (node.types == ("Variant", "Variant")):
            return inner
        if len(reps) != 0:
            return f"Dictionary[{",".join(node.types)}]({inner})"
        return f"Dictionary[{",".join(node.types)}]()"



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
