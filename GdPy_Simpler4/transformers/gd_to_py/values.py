from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions
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

## Value Rendering Options:

class GdToPy_Options(TransformerOptions): ... ## Instanciated at session creation.
class PyToGd_Options(TransformerOptions):
    ''' Options are instantiated at Session creation '''
    use_quotations : ContextVar[bool] = True
    def __init__(self, session:Session):
        self.use_quotations = ContextVar(str(id(self))+"::use_quotations", default=False)


class MACROS:
    def default(item, /, default:Any=None, callable = lambda x:x):
        if item is None:
            return default
        return callable(item)

    def default_yield(item, /, default:Any=None):
        if item is None:
            return default
        res = yield TRANSFORM(item)
        return res



class _String:
    class GdToPy(GdToPy_Transformer):
        keys = ["STRING"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->str:
            return node
        
    class PyToGd(PyToGd_Transformer):
        types = [str]
        def transform(self, session:PyToGd_Session, node:str)->str:
            if session.options["values"].use_quotations.get():
                return f'"{node}"'
            return f'{node}'


class _NodePath():
    class GdToPy(GdToPy_Transformer):
        keys = ["ref_nodepath"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->Generator[Flag, Any, NodePath]:
            typing = yield from MACROS.default_yield(node.children[0], default=None)
            string = MACROS.default(node.children[1], default="", callable=lambda x: x.strip('"'))
            return NodePath(string, typing = typing )
        
    class PyToGd(PyToGd_Transformer):
        types = [NodePath]
        def transform(self, session:PyToGd_Session, node:NodePath)->Generator[Flag, Any, str]:
            typing = yield from MACROS.default_yield(node._typing, default="")
            return f'NodePath{typing}("{node}")'


class _StringName():
    class GdToPy(GdToPy_Transformer):
        keys = ["string_name"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->Generator[Flag, Any, NodePath]:
            return StringName(node.value.strip('"'))
        
    class PyToGd(PyToGd_Transformer):
        types = [StringName]
        def transform(self, session:PyToGd_Session, node:NodePath)->Generator[Flag, Any, str]:
            return f'&"{node}"'

class _Object():
    class GdToPy(GdToPy_Transformer):
        keys = ["object"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, Object]:
            
            return Object(type=node.children[0].value, **kwargs)
        
    class PyToGd(PyToGd_Transformer):
        types = [Object]
        def transform(self, session:PyToGd_Session, node:Object)->Generator[Flag, Any, str]:
            return f'&"{node}"'
    

gd_to_py = GdToPy_TransformerSet("STD::values.py", [  
    _String.GdToPy,
    _NodePath.GdToPy,
    _StringName.GdToPy,
    _Object.GdToPy,
], 
options = {"values":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::values.py", [
    _String.PyToGd,
    _NodePath.PyToGd,
    _StringName.PyToGd,
    _Object.PyToGd,
], 
options = {"values":PyToGd_Options} 
)