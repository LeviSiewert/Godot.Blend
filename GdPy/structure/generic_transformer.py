from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset
from .core.property_collection import PropertyCollection

from .generic import GdObject

class GdToPy_GdObject(GdToPy):
    _keys = ("object",)
    def transform(self, node, tc, c, *args, **kwargs):
        raise NotImplementedError("Not yet implimented!")
class PyToGd_GdObject(PyToGd):
    _keys = (GdObject,)
    def transform(self, node:GdObject, tc, c, *args, **kwargs):
        yield node.properties.items
        props = []
        for k,v in tc.children.get():
            props.append(f"{k}:{v}")
        props = "{" + ",".join(props) + "}"
        return f"Object({node.gdtype} {props})"

gd_to_py_ruleset = GdToPyRuleset( __file__, (
    GdToPy_GdObject,
))
py_to_gd_ruleset = PyToGdRuleset( __file__, (
    PyToGd_GdObject,
))