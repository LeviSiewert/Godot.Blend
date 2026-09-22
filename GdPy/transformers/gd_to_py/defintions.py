from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
from ...core.defininitions import GdDefValueTyping

from contextvars import ContextVar
from contextlib import contextmanager
from typing import Generator, Any
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )

@contextmanager
def cvar_as(cvar: ContextVar, val:Any):
    t = cvar.set(val)
    yield
    cvar.reset(t)

class GdToPy_Options(TransformerOptions): ...
class PyToGd_Options(TransformerOptions): ...

class _Typing():
    class GdToPy(GdToPy_Transformer):
        keys = ["typing"]
        def transform(self, session:GdToPy_Session, node:LarkTree)->Generator[Flag, Any, GdDefValueTyping]:
            return GdDefValueTyping(*node.children)
        
    class PyToGd(PyToGd_Transformer):
        types = [GdDefValueTyping]
        def transform(self, session:PyToGd_Session, node:GdDefValueTyping)->Generator[Flag, Any, str]:
            with cvar_as(session.options["values"].str_use_quotations, False):
                children = yield TRANSFORM_CHILDREN((e for e in (node.contents_a, node.contents_b) if e))
                return f'[{",".join(children)}]'
                


gd_to_py = GdToPy_TransformerSet("STD::values.py", [  
    _Typing.GdToPy,
], 
options = {"definitions":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::values.py", [
    _Typing.PyToGd,
], 
options = {"definitions":PyToGd_Options} 
)