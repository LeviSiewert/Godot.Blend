from .core.transformer_v2 import TransformerRuleset
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset

from .resources import (
    GdResourceFileScene,
    GdResourceFileImport,
)

class GdToPy_GdResourceFileScene(GdToPy):
    _keys = GdResourceFileScene.lark_keys()
    def _transform(self, *args, **kwargs)->GdResourceFileScene:
        return GdResourceFileScene.parse_lark(*args, **kwargs)
class PyToGd_GdResourceFileScene(PyToGd):
    _keys = (GdResourceFileScene,)
    def _transform(self, key, tc, gdc, node:GdResourceFileScene, *children)->str:
        raise NotImplementedError("Not yet implimented!")

class GdToPy_GdResourceFileImport(GdToPy):
    _keys = GdResourceFileImport.lark_keys()
    def _transform(self, *args, **kwargs)->GdResourceFileImport:
        return GdResourceFileImport.parse_lark(*args, **kwargs)
class PyToGd_GdResourceFileImport(PyToGd):
    _keys = (GdResourceFileImport,)
    def _transform(self, key, tc, gdc, node:GdResourceFileImport, *children)->str:
        raise NotImplementedError("Not yet implimented!")

gd_to_py_ruleset = GdToPyRuleset( __file__, (
    GdToPy_GdResourceFileScene(),
    GdToPy_GdResourceFileImport(),
))

py_to_gd_ruleset = PyToGdRuleset( __file__, (
    PyToGd_GdResourceFileScene(),
    PyToGd_GdResourceFileImport(),
))