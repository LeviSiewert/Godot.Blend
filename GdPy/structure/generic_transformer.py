from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset
from .core.property_collection import PropertyCollection
from .generic import GdObject
from .values import GdValueDictionary

class GdToPy_GdObject(GdToPy):
    _keys = ("object",)
    def transform(self, node, tc, c, *args, **kwargs):
        gdtype, *sets = tc.children.get()
        props = {}
        for k,v in sets:
            props[k] = v
        return GdObject(gdtype, **props)
        
class PyToGd_GdObject(PyToGd):
    _keys = (GdObject,)
    def transform(self, node:GdObject, tc, c, *args, **kwargs):
        yield node.properties.items
        props = []
        for k,v in tc.children.get():
            props.append(f"{k}:{v}")
        return f"Object({node.gdtype} {",".join(props)})"

gd_to_py_ruleset = GdToPyRuleset( __file__, (
    GdToPy_GdObject,
))
py_to_gd_ruleset = PyToGdRuleset( __file__, (
    PyToGd_GdObject,
))