import bpy
from .utils import BlenderPytestAttr
from ..structure.core.properties import BlPropertyCollection
from typing import Any

class TestPropertyCollection(BlenderPytestAttr):
    attr_value = bpy.props.PointerProperty(type = BlPropertyCollection) #type:ignore

    def _basic(self, gdtype:str, propname:str, value:Any ):
        propcol : BlPropertyCollection = self.get_attr()

        obj,ptr = propcol.new(gdtype, propname, value)
                
        assert(ptr.name == propname)
        assert(ptr == propcol.get(propname, return_ptr=True))
                
        assert(propcol.get(ptr.value) == obj)

        assert(obj.get_value() == value)
        
        yield obj,ptr

        del propcol[ptr.name]

        for c in propcol._yield_bins():
            assert(len(c) == 0)

    def test_basics(self,):
        with self._basic("string", "test", "Value") as (obj,ptr):
            pass
        with self._basic("GdValueStringName", "test", "Value") as (obj,ptr):
            pass
        with self._basic("int", "test", 1) as (obj,ptr):
            pass
        with self._basic("float", "test", 0.01) as (obj,ptr):
            pass
        