import bpy 

from .core.tranformer_base import BlToPy, BlToPyRuleset
from .core.tranformer_base import PyToBl, PyToBlRuleset

from ...GdPy.structure.core.transformer_v2 import TERMINAL
from ...GdPy.structure.sub_resources import (
    SubResourceExt as GdSubResourceExt,
    SubResourceCategory as GdSubResourceCategory,
    SubResource as GdSubResource,
    SubResourceNode as GdSubResourceNode,
)

from .sub_resources import (
    SubResourceExt as BlSubResourceExt,
    SubResourceCategory as BlSubResourceCategory,
    SubResource as BlSubResource,
    SubResourceNode as BlSubResourceNode,
)

class BlToPy_SubResourceExt(BlToPy):
    _keys = (BlSubResourceExt,)
class PyToBl_SubResourceExt(PyToBl):
    _keys = (GdSubResourceExt,)

class BlToPy_SubResourceCategory(BlToPy):
    _keys = (BlSubResourceCategory,)
class PyToBl_SubResourceCategory(PyToBl):
    _keys = (GdSubResourceCategory,)

class BlToPy_SubResource(BlToPy):
    _keys = (BlSubResource,)
class PyToBl_SubResource(PyToBl):
    _keys = (GdSubResource,)

class BlToPy_SubResourceNode(BlToPy):
    _keys = (bpy.types.Object,)
class PyToBl_SubResourceNode(PyToBl):
    _keys = (GdSubResourceNode,)