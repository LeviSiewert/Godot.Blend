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

from ...GdPy.structure.property_collection import PropertyCollection as GdPropertyCollection
from .property_collection import BlPropertyCollection

from .sub_resources import (
    SubResourceExt as BlSubResourceExt,
    SubResourceCategory as BlSubResourceCategory,
    SubResource as BlSubResource,
    SubResourceNode as BlSubResourceNode,
)

class BlToPy_SubResourceExt(BlToPy):
    _keys = (BlSubResourceExt,)
    def transform(self, node:BlSubResourceExt, tc, bc, *args, **kwargs):
        res = GdSubResourceExt()
        res.type  = node. gd_type
        res.uid = node.uid
        res.path = node.path
        res.id  = node.unique_id
        return res

class PyToBl_SubResourceExt(PyToBl):
    _keys = (GdSubResourceExt,)
    def transform(self, node:GdSubResourceExt, tc, bc, *args, **kwargs):
        res : BlSubResourceExt = bc.property_collection.get().add()
        res. gd_type = node.type
        res.uid = node.uid
        res.path = node.path
        res.unique_id = node.id
        return res
    

class BlSubResourceCategory(BlToPy):
    _keys = (BlSubResourceCategory,)
    def transform(self, node:BlSubResourceCategory, tc, bc, *args, **kwargs):

        yield {"props":node.properties}

        res = GdSubResourceCategory()
        res.name = node.name
        res.properties = tc.children.get()["props"]

        return res

class PySubResourceCategory(PyToBl):
    _keys = (GdSubResourceCategory,)
    def transform(self, node:GdSubResourceCategory, tc, bc, *args, **kwargs):
        res : BlSubResourceCategory = bc.property_collection.get().add()

        res.name = node.name

        t = bc.property_collection.set(res.properties) 
        yield (node.properties,) #Implicitly attached via bc.property_collection
        bc.property_collection.reset(t)

        return res
    
    
class BlToPy_SubResource(BlToPy):
    _keys = (BlSubResource,)
    def transform(self, node:BlSubResource, tc, bc, *args, **kwargs):

        yield {"props":node.properties}

        res = GdSubResource()
        res.type = node.gd_type
        res.id = node.unqiue_id
        res.properties = tc.children.get()["props"]

        return res

class PyToBl_SubResource(PyToBl):
    _keys = (GdSubResource,)
    def transform(self, node:GdSubResource, tc, bc, *args, **kwargs):
        res : BlSubResourceExt = bc.property_collection.get().add()

        res.gd_type = node.type
        res.unique_id = node.id

        t = bc.property_collection.set(res.properties) 
        yield (node.properties,) #Implicitly attached via bc.property_collection
        bc.property_collection.reset(t)

        return res


class BlToPy_SubResourceNode(BlToPy):
    _keys = (bpy.types.Object,)
    def transform(self, node:bpy.types.Object, tc, bc, *args, **kwargs):
        raise NotImplementedError(self.__class__.__name__)

class PyToBl_SubResourceNode(PyToBl):
    _keys = (GdSubResourceNode,)
    def transform(self, node:GdSubResourceNode, tc, bc, *args, **kwargs):
        raise NotImplementedError(self.__class__.__name__)


bl_to_py_ruleset = BlToPyRuleset(__file__,(
    BlToPy_SubResourceExt,
    BlToPy_SubResourceCategory,
    BlToPy_SubResource,
    BlToPy_SubResourceNode,
))
py_to_bl_ruleset = PyToBlRuleset(__file__,(
    PyToBl_SubResourceExt,
    PyToBl_SubResourceCategory,
    PyToBl_SubResource,
    PyToBl_SubResourceNode,
))