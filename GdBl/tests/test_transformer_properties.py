from .utils import BlenderPytestAttr

from ...GdPy.structure.values import GdValueStringName
from ..structure.core.properties import BlPropertyCollection, BlProperty
from ..structure.transformers import BlToPyTransformer, PyToBlTransformer
from ...GdPy.structure.core.transformer_v2 import TransformerContext as TC

import bpy #type:ignore


bl_to_py_c = TC(transformer=BlToPyTransformer)

def _bl_to_py(node):
    return BlToPyTransformer.transform_tree(bl_to_py_c, node)

class TestGdValueStringName(BlenderPytestAttr):
    attr_name = "test"
    attr_value = bpy.props.PointerProperty(type=BlProperty)

    def _bl(self,type:str,value:str):
        prop : BlProperty = self.get_attr()
        prop.type = type
        prop.value = value
        
        return prop

    def test_bl_to_py(self,):
        prop = self._bl("GdValueStringName","value")
        t = bl_to_py_c.existing_object.set(prop)
        assert (_bl_to_py(prop)  == GdValueStringName("value"))
        bl_to_py_c.existing_object.reset(t)

    def test_py_to_bl(self,):
        raise NotImplementedError()
    

# class TestProperties(BlenderPytestAttr):
#     attr_name = "property_collection" 
#     attr_value = PointerProperty(type=BlPropertyCollection)

#     def test_attr(self):
#         c = BlContext()
#         transformer = Transformer([TrfmProperty])
        
#         vals = {"testa":"1", "testb":"2"}

#         source_data = GdPropertyCollection(vals.items())

#         c.meta_tree.set((self.get_attr_loc()[0],))
#         transformer.to_blender(c, source_data)
        
#         col = self.get_attr()

#         for k,v in vals.items():
#             assert(k in col.items.keys())
#             assert(col[k].value == v)

#         # raise Exception("Not yet implimented")


    