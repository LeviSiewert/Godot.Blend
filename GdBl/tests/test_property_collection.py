import bpy
from .utils import BlenderPytestAttr
from ..structure.core.properties import BlPropertyCollection

class TestPropertyCollection(BlenderPytestAttr):
    attr_value = bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore

    def _basic(self, gdtype:str, propname:str, value:Any ):
        propcol : BlPropertyCollection = self.get_attr()

        obj,ptr = propcol.new(gdtype, propname, value)
                
        assert(ptr.name == propname)
        assert(ptr == propcol.get(propname, return_ptr=True))
                
        assert(propcol.get(ptr.value) == obj)

        assert(obj.get_value() == value)
        
        del propcol[ptr.name]

        for c in propcol._yield_bins():
            assert(len(c) == 0)