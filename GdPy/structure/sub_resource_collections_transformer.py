from .core.transformer_v2 import TransformerRuleset
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset

from .sub_resource_collections import (
    CollectionNodeRes,
    CollectionExtRes,
    CollectionEditRes,
    CollectionSubRes,
    CollectionCatRes,
)

class GdToPy_CollectionNodeRes(GdToPy):
    _keys = CollectionNodeRes.lark_keys()
    def _transform(self, *args, **kwargs)->CollectionNodeRes:
        return CollectionNodeRes.parse_lark(*args, **kwargs)
class PyToGd_CollectionNodeRes(PyToGd):
    _keys = (CollectionNodeRes,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_CollectionExtRes(GdToPy):
    _keys = CollectionExtRes.lark_keys()
    def _transform(self, *args, **kwargs)->CollectionExtRes:
        return CollectionExtRes.parse_lark(*args, **kwargs)
class PyToGd_CollectionExtRes(PyToGd):
    _keys = (CollectionExtRes,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_CollectionEditRes(GdToPy):
    _keys = CollectionEditRes.lark_keys()
    def _transform(self, *args, **kwargs)->CollectionEditRes:
        return CollectionEditRes.parse_lark(*args, **kwargs)
class PyToGd_CollectionEditRes(PyToGd):
    _keys = (CollectionEditRes,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_CollectionSubRes(GdToPy):
    _keys = CollectionSubRes.lark_keys()
    def _transform(self, *args, **kwargs)->CollectionSubRes:
        return CollectionSubRes.parse_lark(*args, **kwargs)
class PyToGd_CollectionSubRes(PyToGd):
    _keys = (CollectionSubRes,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_CollectionCatRes(GdToPy):
    _keys = CollectionCatRes.lark_keys()
    def _transform(self, *args, **kwargs)->CollectionCatRes:
        return CollectionCatRes.parse_lark(*args, **kwargs)
class PyToGd_CollectionCatRes(PyToGd):
    _keys = (CollectionCatRes,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

gd_to_py_ruleset = GdToPyRuleset((
    GdToPy_CollectionNodeRes(),
    GdToPy_CollectionExtRes(),
    GdToPy_CollectionEditRes(),
    GdToPy_CollectionSubRes(),
    GdToPy_CollectionCatRes(),
))

py_to_gd_ruleset = PyToGdRuleset((
    PyToGd_CollectionCatRes(),
    PyToGd_CollectionSubRes(),
    PyToGd_CollectionEditRes(),
    PyToGd_CollectionExtRes(),
    PyToGd_CollectionNodeRes(),
))