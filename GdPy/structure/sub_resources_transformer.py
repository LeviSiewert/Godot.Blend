from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset

from .sub_resources import (
    SubResourceExt,
    SubResourceEdit,
    SubResource,
    SubResourceNode,
    SubResourceCategory,
    ResourceContainer,
)

class GdToPy_SubResourceExt(GdToPy):
    _keys = SubResourceExt.lark_keys()
    def _transform(self, *args, **kwargs)->SubResourceExt:
        return SubResourceExt.parse_lark(*args, **kwargs)
class PyToGd_SubResourceExt(PyToGd):
    _keys = (SubResourceExt,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_SubResourceEdit(GdToPy):
    _keys = SubResourceEdit.lark_keys()
    def _transform(self, *args, **kwargs)->SubResourceEdit:
        return SubResourceEdit.parse_lark(*args, **kwargs)
class PyToGd_SubResourceEdit(PyToGd):
    _keys = (SubResourceEdit,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_SubResource(GdToPy):
    _keys = SubResource.lark_keys()
    def _transform(self, *args, **kwargs)->SubResource:
        return SubResource.parse_lark(*args, **kwargs)
class PyToGd_SubResource(PyToGd):
    _keys = (SubResource,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_SubResourceNode(GdToPy):
    _keys = SubResourceNode.lark_keys()
    def _transform(self, *args, **kwargs)->SubResourceNode:
        return SubResourceNode.parse_lark(*args, **kwargs)
class PyToGd_SubResourceNode(PyToGd):
    _keys = (SubResourceNode,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_SubResourceCategory(GdToPy):
    _keys = SubResourceCategory.lark_keys()
    def _transform(self, *args, **kwargs)->SubResourceCategory:
        return SubResourceCategory.parse_lark(*args, **kwargs)
class PyToGd_SubResourceCategory(PyToGd):
    _keys = (SubResourceCategory,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_ResourceContainer(GdToPy):
    _keys = ResourceContainer.lark_keys()
    def _transform(self, *args, **kwargs)->ResourceContainer:
        return ResourceContainer.parse_lark(*args, **kwargs)
class PyToGd_ResourceContainer(PyToGd):
    _keys = (ResourceContainer,)
    def _transform(self, *args, **kwargs)->str:
        raise NotImplementedError("Not yet implimented!")

gd_to_py_ruleset = GdToPyRuleset((
    GdToPy_SubResourceExt(),
    GdToPy_SubResourceEdit(),
    GdToPy_SubResource(),
    GdToPy_SubResourceNode(),
    GdToPy_SubResourceCategory(),
    GdToPy_ResourceContainer(),
))
py_to_gd_ruleset = PyToGdRuleset((
    PyToGd_SubResourceExt(),
    PyToGd_SubResourceEdit(),
    PyToGd_SubResource(),
    PyToGd_SubResourceNode(),
    PyToGd_SubResourceCategory(),
    PyToGd_ResourceContainer(),
))