from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset, PyToBlContext

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
    def transform(self, node, c:PyToBlContext, *args, **kwargs):
        target : BlProperty = c.existing_object.get()
        target.type = "GdValueStringName"
        target.value = str(GdValueStringName)
        return target 
class BlToPy_GdValueStringName(BlToPy):
    _keys = ("GdValueStringName",)
    def transform(self, node, c, *args, **kwargs):
        return GdValueStringName(node.value)

bl_to_gd_rulset = PyToBlRuleset(
    BlToPy_GdValueStringName(),
)
py_to_bl_rulset = BlToPyRuleset_Property(
    PyToBl_GdValueStringName(),
)