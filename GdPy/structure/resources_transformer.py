from .core.transformer_v2 import TransformerRuleset
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset

from .resources import (
    ResourceScene,
    ResourceImport,
    ResourceTres,
)

class GdToPy_ResourceTres(GdToPy):
    _keys = ResourceTres.lark_keys()
    def _transform(self, *args, **kwargs)->ResourceTres:
        return ResourceTres.parse_lark(*args, **kwargs)
class PyToGd_ResourceTres(PyToGd):
    _keys = (ResourceTres,)
    def _transform(self, key, tc, gdc, node:ResourceScene, *children)->str:
        raise NotImplementedError("Not yet implimented!")
    
class GdToPy_ResourceScene(GdToPy):
    _keys = ResourceScene.lark_keys()
    def _transform(self, *args, **kwargs)->ResourceScene:
        return ResourceScene.parse_lark(*args, **kwargs)
class PyToGd_ResourceScene(PyToGd):
    _keys = (ResourceScene,)
    def _transform(self, key, tc, gdc, node:ResourceScene, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_ResourceImport(GdToPy):
    _keys = ResourceImport.lark_keys()
    def _transform(self, *args, **kwargs)->ResourceImport:
        return ResourceImport.parse_lark(*args, **kwargs)
class PyToGd_ResourceImport(PyToGd):
    _keys = (ResourceImport,)
    def _transform(self, key, tc, gdc, node:ResourceImport, *children)->str:
        raise NotImplementedError("Not yet implimented!")

gd_to_py_ruleset = GdToPyRuleset( __file__, (
    GdToPy_ResourceScene(),
    GdToPy_ResourceImport(),
))

py_to_gd_ruleset = PyToGdRuleset( __file__, (
    PyToGd_ResourceScene(),
    PyToGd_ResourceImport(),
))