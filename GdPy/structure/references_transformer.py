from .core.transformer_v2 import TransformerRuleset
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset

from .references import (
    GdValueExtResource,
    GdValueNodePath,
    GdValueSubResource,
    GdValueResourceID,
)

class GdToPy_GdValueExtResource(GdToPy):
    _keys = GdValueExtResource.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueExtResource:
        return GdValueExtResource.parse_lark(*args, **kwargs)
class PyToGd_GdValueExtResource(PyToGd):
    _keys = (GdValueExtResource,)
    def _transform(self, *args, **kwargs)->GdValueExtResource:
        raise Exception("Not yet implimented!")

class GdToPy_GdValueNodePath(GdToPy):
    _keys = GdValueNodePath.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueNodePath:
        return GdValueNodePath.parse_lark(*args, **kwargs)
class PyToGd_GdValueNodePath(PyToGd):
    _keys = (GdValueNodePath,)
    def _transform(self, *args, **kwargs)->GdValueNodePath:
        raise Exception("Not yet implimented!")

class GdToPy_GdValueSubResource(GdToPy):
    _keys = GdValueSubResource.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueSubResource:
        return GdValueSubResource.parse_lark(*args, **kwargs)
class PyToGd_GdValueSubResource(PyToGd):
    _keys = (GdValueSubResource,)
    def _transform(self, *args, **kwargs)->GdValueSubResource:
        raise Exception("Not yet implimented!")

class GdToPy_GdValueResourceID(GdToPy):
    _keys = GdValueResourceID.lark_keys()
    def _transform(self, *args, **kwargs)->GdValueResourceID:
        return GdValueResourceID.parse_lark(*args, **kwargs)
class PyToGd_GdValueResourceID(PyToGd):
    _keys = (GdValueResourceID,)
    def _transform(self, *args, **kwargs)->GdValueResourceID:
        raise Exception("Not yet implimented!")

gd_to_py_ruleset = GdToPyRuleset((
    GdToPy_GdValueExtResource(),
    GdToPy_GdValueNodePath(),
    GdToPy_GdValueSubResource(),
    GdToPy_GdValueResourceID(),
))

py_to_gd_ruleset = TransformerRuleset((
    PyToGd_GdValueExtResource(),
    PyToGd_GdValueNodePath(),
    PyToGd_GdValueSubResource(),
    PyToGd_GdValueResourceID(),
))