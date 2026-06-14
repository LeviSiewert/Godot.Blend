from ...structure.transformers.core import TransformerModule, Transformer
from ...structure.core.primitives import BlContext

from ...structure.transformers.properties import TrfmProperty
from ..utils import BlenderPytestAttr

from ...structure.core.properties import BlPropertyCollection
from bpy.props import PointerProperty

from ....GdPy.structure.core.property_collection import PropertyCollection as GdPropertyCollection

import bpy


class TestProperties(BlenderPytestAttr):
    attr_name = "property_collection" 
    attr_value = PointerProperty(type=BlPropertyCollection)

    def test_attr(self):
        c = BlContext()
        transformer = Transformer([TrfmProperty])
        
        vals = {"testa":"1", "testb":"2"}

        source_data = GdPropertyCollection(vals.items())

        c.meta_tree.set((self.get_attr_loc()[0],))
        transformer.to_blender(c, source_data)
        
        col = self.get_attr()

        for k,v in vals.items():
            assert(k in col.items.keys())
            assert(col[k].value == v)

        # raise Exception("Not yet implimented")


    