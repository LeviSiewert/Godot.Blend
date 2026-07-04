from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule, GdToPyContext, PyToGdContext

from typing import Type 

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
    def transform(self, c, node):
        yield node.children
        anno, addr = c.children.get()
        return NodePath(addr, type=anno)
class PyToGd_NodePath(PyToGdModule):
    _keys = (NodePath,)
    def transform(self, c, node:NodePath):
        if node._typing:
            yield (node._typing,)
            return f'NodePath[{c.children.get()[0]}]("{node.get_address()}")'
        return f'NodePath("{node.get_address()}")'

class GdToPy_StringName(GdToPyModule):
    _keys = ("stringname",)
    def transform(self, c, node):
        yield node.children
        return StringName(c.children.get()[0].strip('&"'))
class PyToGd_StringName(PyToGdModule):
    _keys = (StringName,)
    def transform(self, c, node):
        return f'&"{str(node)}"'

class GdToPy_ObjectArgs(GdToPyModule):
    _keys = ("object_args",)
    def transform(self, c, node):
        yield node.children
        res = {}
        for k,v in c.children.get():
            res[k] = v
        return res
class GdToPy_Object(GdToPyModule):
    _keys = ("object",)
    def transform(self, c, node):
        yield node.children
        type, props = c.children.get() 
        return Object(type, **props)
class PyToGd_Object(PyToGdModule):
    _keys = (Object,)
    def transform(self, c, node:Object):
        if node.kwargs:
            yield node.kwargs
            return f"Object({node.type}, {",".join(f"{k}={v}"for k,v in c.children.get()[0])})"
        return f"Object({node.type})"

class GdToPy_DictionaryImplicit(GdToPyModule):
    _keys = ("dictionary",)
    def transform(self, c, node):
        yield node.children 
        children = c.children.get() 
        return Dictionary(children)
class GdToPy_Dictionary(GdToPyModule):
    _keys = ("dictionary_explicit",)
    def transform(self, c, node):
        yield node.children 
        typing, children = c.children.get() 
        if children is None:
            return Dictionary(types=typing)
        return Dictionary(children, types=typing)
    
class PyToGd_Dictionary(PyToGdModule):
    _keys = (Dictionary,)
    def transform(self, c, node:Dictionary):

        yield node
        di = c.children.get()

        
        reps = tuple((f'{k}:{v}' for k,v in di.items()))
        inner = '{' + ",".join(reps) + '}'
        
        if (node._typing is None) or node._typing.is_variant():
            return inner

        yield (node._typing,)
        ty = c.children.get()[0]

        return f"Dictionary{ty}({inner})"

class GdToPy_ArrayImplicit(GdToPyModule):
    _keys = ("array",)
    def transform(self, c, node):
        yield node.children
        return Array(*c.children.get())

class GdToPy_Array(GdToPyModule):
    _keys = ("array_explicit",)
    def transform(self, c, node):
        yield node.children
        typing, children = c.children.get()
        if children is None:
            return Array(types=typing)
        return Array(*children, types=typing) 

class PyToGd_Array(PyToGdModule):
    _keys = (Array,)
    def transform(self, c, node:Array):
        yield node
        values = c.children.get()

        inner = '[' + ",".join(values) + ']'

        if (node._typing is None) or node._typing.is_variant():
            return inner

        yield (node._typing,)
        typing = c.children.get()[0]
        
        return f'Array[{typing}]({inner})'

class _GdToPy_FixedLenArray(GdToPyModule):
    _res_type : Type
    def transform(self, c, node):
        yield node.children
        return self._res_type(*c.children.get())
class _PyToGd_FixedLenArray(PyToGdModule):
    _res_key : str
    def transform(self, c:PyToGdContext, node):
        t = c.rendering.float_as_int_ok.set(True)
        yield node
        c.rendering.float_as_int_ok.reset(t)
        return f"{self._res_key}({",".join(c.children.get())})"


class GdToPy_Vector2i(_GdToPy_FixedLenArray):
    _keys = ("vector2i",)
    _res_type = Vector2i
class PyToGd_Vector2i(_PyToGd_FixedLenArray):
    _res_key = "Vector2i"
    _keys = (Vector2i,)

class GdToPy_Vector3i(_GdToPy_FixedLenArray):
    _keys = ("vector3i",)
    _res_type = Vector3i
class PyToGd_Vector3i(_PyToGd_FixedLenArray):
    _res_key = "Vector3i"
    _keys = (Vector3i,)

class GdToPy_Vector4i(_GdToPy_FixedLenArray):
    _keys = ("vector4i",)
    _res_type = Vector4i
class PyToGd_Vector4i(_PyToGd_FixedLenArray):
    _res_key = "Vector4i"
    _keys = (Vector4i,)

class GdToPy_Rect2i(_GdToPy_FixedLenArray):
    _keys = ("rect2i",)
    _res_type = Rect2i
class PyToGd_Rect2i(_PyToGd_FixedLenArray):
    _res_key = "Rect2i"
    _keys = (Rect2i,)

class GdToPy_Vector2(_GdToPy_FixedLenArray):
    _keys = ("vector2",)
    _res_type = Vector2
class PyToGd_Vector2(_PyToGd_FixedLenArray):
    _res_key = "Vector2"
    _keys = (Vector2,)

class GdToPy_Vector3(_GdToPy_FixedLenArray):
    _keys = ("vector3",)
    _res_type = Vector3
class PyToGd_Vector3(_PyToGd_FixedLenArray):
    _res_key = "Vector3"
    _keys = (Vector3,)

class GdToPy_Vector4(_GdToPy_FixedLenArray):
    _keys = ("vector4",)
    _res_type = Vector4
class PyToGd_Vector4(_PyToGd_FixedLenArray):
    _res_key = "Vector4"
    _keys = (Vector4,)

class GdToPy_Rect2(_GdToPy_FixedLenArray):
    _keys = ("rect2",)
    _res_type = Rect2
class PyToGd_Rect2(_PyToGd_FixedLenArray):
    _res_key = "Rect2"
    _keys = (Rect2,)

class GdToPy_Plane(_GdToPy_FixedLenArray):
    _keys = ("plane",)
    _res_type = Plane
class PyToGd_Plane(_PyToGd_FixedLenArray):
    _res_key = "Plane"
    _keys = (Plane,)

class GdToPy_Color(_GdToPy_FixedLenArray):
    _keys = ("color",)
    _res_type = Color
class PyToGd_Color(_PyToGd_FixedLenArray):
    _res_key = "Color"
    _keys = (Color,)

class GdToPy_AABB(_GdToPy_FixedLenArray):
    _keys = ("aabb",)
    _res_type = AABB
class PyToGd_AABB(_PyToGd_FixedLenArray):
    _res_key = "AABB"
    _keys = (AABB,)

class GdToPy_Quaternion(_GdToPy_FixedLenArray):
    _keys = ("quaternion",)
    _res_type = Quaternion
class PyToGd_Quaternion(_PyToGd_FixedLenArray):
    _res_key = "Quaternion"
    _keys = (Quaternion,)

class GdToPy_Transform2D(_GdToPy_FixedLenArray):
    _keys = ("transform2d",)
    _res_type = Transform2D
class PyToGd_Transform2D(_PyToGd_FixedLenArray):
    _res_key = "Transform2D"
    _keys = (Transform2D,)

class GdToPy_Transform3D(_GdToPy_FixedLenArray):
    _keys = ("transform3d",)
    _res_type = Transform3D
class PyToGd_Transform3D(_PyToGd_FixedLenArray):
    _res_key = "Transform3D"
    _keys = (Transform3D,)

class GdToPy_Basis(_GdToPy_FixedLenArray):
    _keys = ("basis",)
    _res_type = Basis
class PyToGd_Basis(_PyToGd_FixedLenArray):
    _res_key = "Basis"
    _keys = (Basis,)


class _GdToPy_PackedArray(GdToPyModule):
    _res_type : Type
    def transform(self, c, node):
        yield node.children
        return self._res_type(*c.children.get())
class _PyToGd_PackedArray(PyToGdModule):
    _res_key : str
    def transform(self, c, node):
        t = c.rendering.float_as_int_ok.set(True)
        yield node
        c.rendering.float_as_int_ok.reset(t)
        return f"{self._res_key}({",".join(c.children.get())})"

class GdToPy_PackedInt32Array(_GdToPy_PackedArray):
    _keys = ("packedint32array",)
    _res_type = PackedInt32Array
class PyToGd_PackedInt32Array(_PyToGd_PackedArray):
    _keys = (PackedInt32Array,)
    _res_key = "PackedInt32Array"

class GdToPy_PackedInt64Array(_GdToPy_PackedArray):
    _keys = ("packedint64array",)
    _res_type = PackedInt64Array
class PyToGd_PackedInt64Array(_PyToGd_PackedArray):
    _keys = (PackedInt64Array,)
    _res_key = "PackedInt64Array"

class GdToPy_PackedFloat32Array(_GdToPy_PackedArray):
    _keys = ("packedfloat32array",)
    _res_type = PackedFloat32Array
class PyToGd_PackedFloat32Array(_PyToGd_PackedArray):
    _keys = (PackedFloat32Array,)
    _res_key = "PackedFloat32Array"

class GdToPy_PackedFloat64Array(_GdToPy_PackedArray):
    _keys = ("packedfloat64array",)
    _res_type = PackedFloat64Array
class PyToGd_PackedFloat64Array(_PyToGd_PackedArray):
    _keys = (PackedFloat64Array,)
    _res_key = "PackedFloat64Array"

class GdToPy_PackedStringArray(_GdToPy_PackedArray):
    _keys = ("packedstringarray",)
    _res_type = PackedStringArray
class PyToGd_PackedStringArray(_PyToGd_PackedArray):
    _keys = (PackedStringArray,)
    _res_key = "PackedStringArray"


class _GdToPy_PackedArrayComplex(GdToPyModule):
    _res_type : Type
    def transform(self, c, node):
        yield node.children
        return self._res_type(*c.children.get())
class _PyToGd_PackedArrayComplex(PyToGdModule):
    _res_key : str
    def transform(self, c, node):
        ## generator is streamed, and yielded from
        def each_item_joined():
            for i in node:
                yield from i

        t = c.rendering.float_as_int_ok.set(True)
        yield each_item_joined()
        c.rendering.float_as_int_ok.reset(t)
        return f"{self._res_key}({",".join(c.children.get())})"

class GdToPy_PackedVector2Array(_GdToPy_PackedArrayComplex):
    _keys = ("packedvector2array",)
    _res_type = PackedVector2Array
class PyToGd_PackedVector2Array(_PyToGd_PackedArrayComplex):
    _keys = (PackedVector2Array,)
    _res_key = "PackedVector2Array"

class GdToPy_PackedVector3Array(_GdToPy_PackedArrayComplex):
    _keys = ("packedvector3array",)
    _res_type = PackedVector3Array
class PyToGd_PackedVector3Array(_PyToGd_PackedArrayComplex):
    _keys = (PackedVector3Array,)
    _res_key = "PackedVector3Array"

class GdToPy_PackedVector4Array(_GdToPy_PackedArrayComplex):
    _keys = ("packedvector4array",)
    _res_type = PackedVector4Array
class PyToGd_PackedVector4Array(_PyToGd_PackedArrayComplex):
    _keys = (PackedVector4Array,)
    _res_key = "PackedVector4Array"

class GdToPy_PackedColorArray(_GdToPy_PackedArrayComplex):
    _keys = ("packedcolorarray",)
    _res_type = PackedColorArray
class PyToGd_PackedColorArray(_PyToGd_PackedArrayComplex):
    _keys = (PackedColorArray,)
    _res_key = "PackedColorArray"


class GdToPy_PackedByteArray(GdToPyModule):
    _keys = ("packedbytearray",)
    def transform(self, c, node):
        yield node.children
        txt = c.children.get()[0]
        return PackedByteArray(txt.encode("utf-8"))
class PyToGd_PackedByteArray(PyToGdModule):
    _keys = (PackedByteArray,)
    def transform(self, c, node:PackedByteArray):
        return f'PackedByteArray("{node.decode("utf-8")}")'


gd_to_py_ruleset = GdToPyRuleset("STD_Values", [
    GdToPy_NodePath,
    GdToPy_StringName,
    GdToPy_ObjectArgs,
    GdToPy_Object,
    GdToPy_Dictionary,
    GdToPy_DictionaryImplicit,
    GdToPy_Array,
    GdToPy_ArrayImplicit,
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