from .core.transformer_v2 import TransformerRuleset
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset

from .core.property_collection import PropertyCollection

class GdToPy_PropertyCollection(GdToPy):
    _keys = ("properties",)
    def transform(self, node, tc, c, *args, **kwargs):
        props = tc.children.get()
        res = PropertyCollection()
        for kv in props:
            if kv is None: 
                continue
            res[kv[0]] = kv[1]
        return res

class PyToGd_PropertyCollection(PyToGd):
    _keys = (PropertyCollection,)
    def transform(self, node:PropertyCollection, tc, c, *args, **kwargs):
        yield node.items
        res = []
        for k,v in tc.children.get().items():
            res.append(f"{k} = {v}")
        return "\n".join(res)

gd_to_py_ruleset = GdToPyRuleset( __file__, (
    GdToPy_PropertyCollection,
))

py_to_gd_ruleset = PyToGdRuleset( __file__, (
    PyToGd_PropertyCollection,
))
