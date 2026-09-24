from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
# from ...core.structure_promise import Promise, RefType

from ...core.structure import Promise

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
        def transform(self, session, node:LarkTree)->Generator[Flag,str,Promise]:
            address = yield TRANSFORM(node.children[0])
            match str(node.type):
                case "ref_subresource":
                    return Promise(address, ref_type=Promise.RefType.SUB_RESOURCE)
                case "ref_extresource":
                    return Promise(address, ref_type=Promise.RefType.EXT_RESOURCE)
                case "ref_resource":
                    return Promise(address, ref_type=Promise.RefType.RID)
            raise KeyError(node)

    class PyToGd(PyToGd_Transformer):
        types = [Promise]

        def transform(self, session:Session, node:Promise)->Generator[Flag,Any,str]:
            match node.ref_type:
                case Promise.RefType.SUB_RESOURCE:
                    return f'SubResource("{node.key}")'
                case Promise.RefType.EXT_RESOURCE_DIRECT:
                    return f'ExtResource("{node.key}")'
                case Promise.RefType.RESOURCE:
                    return f'RID("{node.key}")'
                case Promise.RefType.RID:
                    return f'RID("{node.key}")'
                case Promise.RefType.FILE:
                    # return f'FILE("{node.key}")'
                    raise Exception("Unknown how file should be rendered.")
                case Promise.RefType.EXT_RESOURCE:
                    ## TODO : Need to find contextexual id, unknown otherwise
                    raise NotImplementedError() 


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
