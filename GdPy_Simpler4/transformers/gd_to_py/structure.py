from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions, cvar_as
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
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


from contextvars import ContextVar
from typing import Generator, Any
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )

class GdToPy_Options(TransformerOptions): ... ## Instanciated at session creation.
class PyToGd_Options(TransformerOptions): ...

class _Properties():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _Project():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _ExtResource():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _File():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _Resource():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _NodePath():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _GdSignal():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...
class _Node():
    class GdToPy(GdToPy_Transformer):...
    class PyToGd(PyToGd_Transformer):...

gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    _Properties.GdToPy,
    _Project.GdToPy,
    _ExtResource.GdToPy,
    _File.GdToPy,
    _Resource.GdToPy,
    _NodePath.GdToPy,
    _GdSignal.GdToPy,
    _Node.GdToPy,
], 
options = {"structure":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::structure.py", [
    _Properties.PyToGd,
    _Project.PyToGd,
    _ExtResource.PyToGd,
    _File.PyToGd,
    _Resource.PyToGd,
    _NodePath.PyToGd,
    _GdSignal.PyToGd,
    _Node.PyToGd,
], 
options = {"structure":PyToGd_Options} 
)