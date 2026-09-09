from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session

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


class String:
    class GdToPy(GdToPy_Transformer):
        keys = ["STRING"]
        def transform(self, session:GdToPy_Session, node:LarkToken)->str: #Generator[Flag, Any, str] if non-terminal
            return node
        
    class PyToGd(PyToGd_Transformer):
        types = [str]
        def transform(self, session:PyToGd_Session, node:str)->str: #Generator[Flag, Any, str] if non-terminal
            if session.options["values"].use_quotations.get():
                return f'"{node}"'
            return f'{node}'


gd_to_py = GdToPy_TransformerSet("STD::values.py", [  
    String.GdToPy,
], 
options = {"values":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::values.py", [
    String.PyToGd,
], 
options = {"values":PyToGd_Options} 
)