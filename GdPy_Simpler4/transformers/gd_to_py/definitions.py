from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule, PyToGdContext

from ...core.defininitions import GdDefType, GdDefProperty, GdDefSignal, GdDefValue

from lark import (
    Tree as LarkTree,
    Token as LarkToken, 
)

class GdToPy_GdDefType(PyToGdModule):
    _keys = ("type_anno",)
    def transform(self, c:PyToGdContext, node:LarkTree)->GdDefType:
        raise NotImplementedError
    
class PyToGd_GdDefType(PyToGdModule):
    _keys = (GdDefType,)
    def transform(self, c:PyToGdContext, node:GdDefType)->str:
        raise NotImplementedError            


gd_to_py_ruleset = GdToPyRuleset("STD_Terminals", *[
    GdToPy_GdDefType,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Terminals", *[
    PyToGd_GdDefType,
])