from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
from ...core.structure_promise import StructReference, RefType


from contextvars import ContextVar
from typing import Generator, Any
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )

class GdToPy_Options(TransformerOptions): ...
class PyToGd_Options(TransformerOptions): ...

class _Promises():
    class GdToPy(GdToPy_Transformer):
        keys = ["ref_subresource", "ref_extresource", "ref_resource",]
        def transform(self, session, node:LarkTree)->Generator[Flag,str,StructReference]:
            address = yield TRANSFORM(node.children[0])
            match str(node.type):
                case "ref_subresource":
                    return StructReference(address, ref_type=RefType.SUB_RESOURCE)
                case "ref_extresource":
                    return StructReference(address, ref_type=RefType.EXT_RESOURCE)
                case "ref_resource":
                    return StructReference(address, ref_type=RefType.RID)
            raise KeyError(node)

    class PyToGd(PyToGd_Transformer):
        types = [StructReference]

        def transform(self, session:Session, node:StructReference)->Generator[Flag,Any,str]:
            match node.ref_type:
                case RefType.SUB_RESOURCE:
                    return f'SubResource("{node.key}")'
                case RefType.EXT_RESOURCE:
                    return f'ExtResource("{node.key}")'
                case RefType.RESOURCE:
                    # FutureWarning("Non-Normalized Structure")
                    return f'RID("{node.key}")'
                case RefType.RID:
                    return f'RID("{node.key}")'
                case RefType.FILE:
                    # FutureWarning("Non-Normalized Structure")
                    raise Exception()
                case RefType.DEFER:
                    # FutureWarning("Non-Normalized Structure")
                    raise Exception()
                case _:
                    raise KeyError(node.ref_type)

gd_to_py = GdToPy_TransformerSet("STD::promises.py", [  
    _Promises.GdToPy,
],
options = {"promises":GdToPy_Options}

)

py_to_gd = PyToGd_TransformerSet("STD::promises.py", [
    _Promises.PyToGd,
], 
options = {"promises":PyToGd_Options} 

)
