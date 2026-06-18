from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

from ....GdPy.structure.values import GdValueStringName
from ..core.properties import BlProperty

class BlToPyRuleset_Property(BlToPyRuleset):
    ''' Key is stored on BlProperty in a different way than other Blender objects '''
    def _key_extractor(self, key):
        if isinstance(key, BlProperty):
            return (key.type,)
        return super()._key_extractor(key)

class PyToBl_GdValueStringName(PyToBl):
    _keys = (GdValueStringName,)
    def transform(self, node, c, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        target.type = "GdValueStringName"
        target.value = str(GdValueStringName)
        return target 
class BlToPy_GdValueStringName(BlToPy):
    _keys = ("GdValueStringName",)
    def transform(self, node, c, *args, **kwargs):
        return GdValueStringName(node.value)

bl_to_py_ruleset = BlToPyRuleset_Property((
    BlToPy_GdValueStringName(),
))
py_to_bl_ruleset = PyToBlRuleset((
    PyToBl_GdValueStringName(),
))