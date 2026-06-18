from .utils import BlenderPytestAttr

from ...GdPy.structure.values import GdValueStringName
from ..structure.core.properties import BlPropertyCollection, BlProperty
from ..structure.transformers import BlToPyTransformer, PyToBlTransformer
from ...GdPy.structure.core.transformer_v2 import TransformerContext as TC

from contextlib import contextmanager

import bpy #type:ignore

bl_to_py_c = TC(transformer=BlToPyTransformer)

def _bl_to_py(node):
    return BlToPyTransformer.transform_tree(bl_to_py_c, node)

class _Base(BlenderPytestAttr):
    @contextmanager
    def _bl(self,**kwargs):
        prop, original_values = self.set_prop(**kwargs)
        t = bl_to_py_c.existing_object.set(prop)
        yield prop
        bl_to_py_c.existing_object.reset(t)
        self.clean_prop(prop, original_values)

    def set_prop(self, **kwargs)->tuple[BlProperty,dict]:
        prop = self.get_attr()
        original = {}
        for k,v in kwargs.items():
            original[k]=getattr(prop,k)
            setattr(prop,k,v)
        return prop,original

    def clean_prop(self, prop:BlProperty, original_values:dict):
        for k,v in original_values.items():
            setattr(prop,k,v)


class TestGdValueStringName(_Base):
    attr_name = "test"
    attr_value = bpy.props.PointerProperty(type=BlProperty)

    def test_bl_to_py(self,):
        with self._bl(type="GdValueStringName", value="value") as prop:
            assert(_bl_to_py(prop) == GdValueStringName("value"))
        
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


    