from .core import TransformerModule
from ....GdPy.structure.core.property_collection import PropertyCollection as GdPropertyCollection
from ..core.properties import PropertyCollection as BlPropertyCollection

class TrfmProperty(TransformerModule):
    _terminal = True

    @classmethod
    def get_gdbl_keys(cls):
        return (GdPropertyCollection, BlPropertyCollection)
    
    def to_blender(self, k, c, gd_item:GdPropertyCollection, _children):
        map_to : BlPropertyCollection = c.meta_tree.get()[-1].property_collection

        for k,v in gd_item.items.items():
            item = map_to.new(name=k)
            item.value = str(v)
        
    def fr_blender(self, k, c, bl_item:BlPropertyCollection, _children):
        res = BlPropertyCollection()
        for v in bl_item:
            res[v.name] = v.value
        return res

_all = (
    TrfmProperty,
)