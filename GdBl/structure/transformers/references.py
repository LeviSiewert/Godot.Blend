from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

class PyToBl_Properties(PyToBl):
    def transform(self, node, c, *args, **kwargs):
        raise NotImplementedError()
class BlToPy_Properties(BlToPy):
    def transform(self, node, c, *args, **kwargs):
        raise NotImplementedError()

py_to_bl_rulset = BlToPyRuleset(
    BlToPy_Properties,
    )
bl_to_gd_rulset = PyToBlRuleset(
    BlToPy_Properties,
    )