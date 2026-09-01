from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule, PyToGdContext

from ...core.defininitions import GdDefType, GdDefProperty, GdDefSignal, GdDefValue, GdDefValueTyping

from lark import (
    Tree as LarkTree,
    Token as LarkToken, 
)

class GdToPy_GdDefValueTyping(PyToGdModule):
    _keys = ("type_anno",)
    def transform(self, c:PyToGdContext, node:LarkTree)->GdDefValueTyping:
        yield node.children
        return GdDefValueTyping(*c.children.get()) 

class PyToGd_GdDefValueTyping(PyToGdModule):
    _keys = (GdDefValueTyping,)
    def transform(self, c:PyToGdContext, node:GdDefValueTyping)->str:
        # node.contents_a, node.contents_b
        if node.contents_a is None:
            return ""
        elif node.contents_b is None:
            return "[" + node.contents_a + "]"
        return "[" + node.contents_a +","+ node.contents_b + "]"



gd_to_py_ruleset = GdToPyRuleset("STD_Terminals", *[
    GdToPy_GdDefValueTyping,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Terminals", *[
    PyToGd_GdDefValueTyping,
])