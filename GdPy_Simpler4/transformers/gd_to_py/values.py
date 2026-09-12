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
    str_use_quotations : ContextVar[bool] = True

    float_as_int_ok : ContextVar[bool] = True
    float_percision : ContextVar[int] = -1
    float_tail_req_len : ContextVar[int] = -1

    def __init__(self, session:Session):
        uid = str(id(self))
        self.str_use_quotations = ContextVar(uid+"::str_use_quotations", default=False)
        self.float_as_int_ok = ContextVar(uid+"::float_as_int_ok", default = True )
        self.float_percision = ContextVar(uid+"::float_percision", default = -1 )
        self.float_tail_req_len = ContextVar(uid+"::float_tail_req_len", default = -1 ) 
    
    def render_float(self, f:float)->str:
        if self.float_as_int_ok.get() and f.is_integer():
            return str(int(f))
        return f'{f:g}'

class MACROS:
    def default(item, /, default:Any=None, callable = lambda x:x):
        if item is None:
            return default
        return callable(item)

    def default_yield(item, /, default:Any=None, flag:Flag=TRANSFORM_CHILDREN, settings={}):
        if item is None:
            return default
        res = yield flag(item, **settings)
        return res

    def gdtopy_pairs_to_dict(item:list[LarkTree])->Generator[Flag,tuple,dict]:
        res = {}
        for pair in item:
            k,v = yield TRANSFORM_CHILDREN(pair.children)
            res[k] = v
        return res

    def pytogd_dict_to_str(item:dict, seperator="=", join=",")->Generator:
        res = []
        for pair in item.items():
            k,v = yield TRANSFORM_CHILDREN(pair) 
            res.append(k + seperator + v)
        return join.join(res)



class _Null:
    class GdToPy(GdToPy_Transformer):
        keys = ["NULL"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->float:
            return None

    class PyToGd(PyToGd_Transformer):
        types = [None]
        def match(self, session:Session, node:Any)->bool:
            return node is None
        def transform(self, session:PyToGd_Session, node:float)->str:
            return "null"
        

class _Float:
    class GdToPy(GdToPy_Transformer):
        keys = ["FLOAT","INF"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->float:
            return float(node)

    class PyToGd(PyToGd_Transformer):
        types = [float]
        def transform(self, session:PyToGd_Session, node:float)->str:
            return session.options["values"].render_float(node) 

class _Int:
    class GdToPy(GdToPy_Transformer):
        keys = ["INTEGER"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->int:
            return int(node)

    class PyToGd(PyToGd_Transformer):
        types = [int]
        def transform(self, session:PyToGd_Session, node:int)->str:
            return str(node)


class _Bool:
    class GdToPy(GdToPy_Transformer):
        keys = ["BOOL"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->str:
            return node.value == "true"

    class PyToGd(PyToGd_Transformer):
        types = [bool]
        def transform(self, session:PyToGd_Session, node:bool)->str:
            if node is True:
                return 'true'
            elif node is False:
                return 'false'
            raise ValueError(node)

class _String:
    class GdToPy(GdToPy_Transformer):
        keys = ["STRING", "WORD"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->str:
            return str(node.value).strip('"')
        
    class PyToGd(PyToGd_Transformer):
        types = [str]
        def transform(self, session:PyToGd_Session, node:str)->str:
            if session.options["values"].str_use_quotations.get():
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
        keys = ["stringname"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->Generator[Flag, Any, NodePath]:
            return StringName(MACROS.default(node.children[0], default="", callable=lambda x: x.strip('"')))
        
    class PyToGd(PyToGd_Transformer):
        types = [StringName]
        def transform(self, session:PyToGd_Session, node:NodePath)->Generator[Flag, Any, str]:
            return f'&"{node}"'

class _Object():
    class GdToPy(GdToPy_Transformer):
        keys = ["object"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, Object]:
            kwargs = yield from MACROS.gdtopy_pairs_to_dict(node.children[1:])
            return Object(type=node.children[0].value, **kwargs)
        
    class PyToGd(PyToGd_Transformer):
        types = [Object]
        def transform(self, session:PyToGd_Session, node:Object)->Generator[Flag, Any, str]:
            if len(node.kwargs):
                kwargs : str = yield from MACROS.pytogd_dict_to_str(node.kwargs)
                return f'Object({node.type}, {kwargs})'
                
            return f'Object({node.type})'
            # return f'&"{node}"'


class _Dictionary:
    class GdToPy_implicit(GdToPy_Transformer):
        keys = ["dict"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, Object]:
            kwargs = yield from MACROS.gdtopy_pairs_to_dict(node.children[1:])
            return Dictionary(kwargs)
        
    class GdToPy(GdToPy_Transformer):
        keys = ["explicit_dict"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, Object]:
            # raise Exception(node)
            kwargs = yield from MACROS.gdtopy_pairs_to_dict(node.children[1:])
            typing = yield from MACROS.default_yield(node.children[0], default=None, flag=TRANSFORM)
            return Dictionary(kwargs, typing=typing)
        
    class PyToGd(PyToGd_Transformer):
        types = [Dictionary, dict]
        def transform(self, session:PyToGd_Session, node:Dictionary)->Generator[Flag, Any, str]:
            if isinstance(node,Dictionary) and (not (node.typing is None)):
                typing = yield TRANSFORM(node.typing)
                body = yield from MACROS.pytogd_dict_to_str(node, seperator=":")
                return f'Dictionary{typing}(' + '{' + body + "})" 

            body = yield from MACROS.pytogd_dict_to_str(node)
            return '{' + body + "}" 


class _Array:
    class GdToPy_implicit(GdToPy_Transformer):
        keys = ["list","array"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, Array]:
            body = yield TRANSFORM_CHILDREN(node.children)
            return Array(*body, typing=None)
        

    class GdToPy(GdToPy_Transformer):
        keys = ["explicit_list","explicit_array"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, Array]:
            body = yield TRANSFORM_CHILDREN(node.children)
            typing = yield from MACROS.default_yield(node.children[0], default=tuple(), flag=TRANSFORM_CHILDREN)
            return Array(*body, typing=typing)
        
    class PyToGd(PyToGd_Transformer):
        types = [Array, list]
        def transform(self, session:PyToGd_Session, node:Array)->Generator[Flag, Any, str]:
            if isinstance(node,Array) and (not (node.typing is None)):
                typing = yield TRANSFORM(node.typing)
                body = yield TRANSFORM_CHILDREN(node)
                return f'Array{typing}(' + '[' + body + "])" 

            body = yield TRANSFORM_CHILDREN(node)
            return '[' + body + "]" 


class _Vectors():
    class GdToPy(GdToPy_Transformer):
        keys = ["vector2i", "vector3i", "vector4i", "vector2", "vector3", "vector4","plane","color","aabb","quaternion","transform2d","transform3d","basis","rect2","rect2i"]
        def transform(self, session:Session, node:LarkTree)->Generator[Flag,None,Any]:
            children = yield TRANSFORM_CHILDREN(node.children)
            match str(node.data):
                case "vector2i":
                    return Vector2i(*children) 
                case "vector3i":
                    return Vector3i(*children) 
                case "vector4i":
                    return Vector4i(*children) 
                case "vector2":
                    return Vector2(*children) 
                case "vector3":
                    return Vector3(*children) 
                case "vector4":
                    return Vector4(*children) 
                case "plane":
                    return Plane(*children) 
                case "color":
                    return Color(*children) 
                case "aabb":
                    return AABB(*children) 
                case "quaternion":
                    return Quaternion(*children) 
                case "transform2d":
                    return Transform2D(*children) 
                case "transform3d":
                    return Transform3D(*children) 
                case "basis":
                    return Basis(*children) 
                case "rect2":
                    return Rect2(*children) 
                case "rect2i":
                    return Rect2i(*children) 
            raise KeyError(node)
                
    class PyToGd(PyToGd_Transformer):
        types = [Vector2i, Vector3i, Vector4i, Vector2, Vector3, Vector4,Plane,Color,AABB,Quaternion,Transform2D,Transform3D,Basis, Rect2i, Rect2]

        def transform(self, session:Session, node:Any)->Generator[Flag,Any,str]:
            children = yield TRANSFORM_CHILDREN(node)
            return f"{node.__class__.__name__}({",".join(children)})"


class _PackedByteArray():
    class GdToPy(GdToPy_Transformer):
        keys = ["packed_byte_array"]
        def transform(self, session, node):
            return PackedByteArray(str(node.children[0].value))
    class PyToGd(PyToGd_Transformer):
        types = [PackedByteArray]
        def transform(self, session, node:PackedByteArray):
            return f'PackedByteArray("{str(node)}")'


class _PackedComplex():
                
    class GdToPy(GdToPy_Transformer):
        keys = ["packed_vector2_array", "packed_vector3_array", "packed_vector4_array", "packed_color_array"]
        def transform(self, session:Session, node:Any)->Generator[Flag,Any,str]:
            children = yield TRANSFORM_CHILDREN(node.children)

            match str(node.data):
                case "packed_vector2_array":
                    return PackedVector2Array(*children)
                case "packed_vector3_array":
                    return PackedVector3Array(*children)
                case "packed_vector4_array":
                    return PackedVector4Array(*children)
                case "packed_color_array":
                    return PackedColorArray(*children)
            raise KeyError(node)

    class PyToGd(PyToGd_Transformer):
        types = [PackedVector2Array, PackedVector3Array, PackedVector4Array, PackedColorArray,]

        def transform(self, session:Session, node:Any)->Generator[Flag,Any,str]:
            # children = yield TRANSFORM_CHILDREN(node)
            children = []
            for i in node:
                r = yield TRANSFORM_CHILDREN(i)
                children.extend(r)
            return f"{node.__class__.__name__}({",".join(children)})"

class _PackedSimple():
    class GdToPy(GdToPy_Transformer):
        keys = ["packed_int32_array", "packed_int64_array", "packed_float32_array", "packed_float64_array", "packed_string_array"]

        def transform(self, session:Session, node:Any)->Generator[Flag,Any,str]:

            children = yield TRANSFORM_CHILDREN(node.children)
            
            match str(node.data):
                case "packed_int32_array":
                    return PackedInt32Array(*children)
                case "packed_int64_array":
                    return PackedInt64Array(*children)
                case "packed_float32_array":
                    return PackedFloat32Array(*children)
                case "packed_float64_array":
                    return PackedFloat64Array(*children)
                case "packed_string_array":
                    return PackedStringArray(*children)
            raise KeyError(node)

    class PyToGd(PyToGd_Transformer):
        types = [PackedInt32Array, PackedInt64Array, PackedFloat32Array, PackedFloat64Array, PackedStringArray,]

        def transform(self, session:Session, node:Any)->Generator[Flag,Any,str]:
            children = yield TRANSFORM_CHILDREN(node)
            return f"{node.__class__.__name__}({",".join(children)})"




gd_to_py = GdToPy_TransformerSet("STD::values.py", [  
    _String.GdToPy,
    _NodePath.GdToPy,
    _StringName.GdToPy,
    _Object.GdToPy,
    _Bool.GdToPy,
    _Int.GdToPy,
    _Float.GdToPy,
    _Dictionary.GdToPy,
    _Dictionary.GdToPy_implicit,
    _Array.GdToPy,
    _Array.GdToPy_implicit,
    _Vectors.GdToPy,
    _PackedSimple.GdToPy,
    _PackedComplex.GdToPy,
    _PackedByteArray.GdToPy,
    _Null.GdToPy,
], 
options = {"values":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::values.py", [
    _String.PyToGd,
    _NodePath.PyToGd,
    _StringName.PyToGd,
    _Object.PyToGd,
    _Bool.PyToGd,
    _Int.PyToGd,
    _Float.PyToGd,
    _Dictionary.PyToGd,
    _Array.PyToGd,
    _Vectors.PyToGd,
    _PackedSimple.PyToGd,
    _PackedComplex.PyToGd,
    _PackedByteArray.PyToGd,
    _Null.PyToGd,
], 
options = {"values":PyToGd_Options} 
)