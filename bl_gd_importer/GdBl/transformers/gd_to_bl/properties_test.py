import bpy

from typing import Generator

from ._test_utils import TransformerDirect
from .properties import *

class TestProperties(TransformerDirect):
    source : Properties
    target : Properties

    def setup(self):
        super().setup()
        bpy.types.Scene.source = bpy.props.PointerProperty(type=Properties)
        bpy.types.Scene.target = bpy.props.PointerProperty(type=Properties)
        self.source = bpy.types.Scene.source
        self.target = bpy.types.Scene.target
    
    def teardown(self):
        self.source = None
        self.target = None
        del bpy.types.Scene.source
        del bpy.types.Scene.target
        super().teardown()

    def bl_bl_compare(self, source:bpy.types.Object, target:bpy.types.Object):
        assert source.export() == target.export()
        
    def gd_gd_compare(self, source:GdProperties, target:GdProperties):
        assert isinstance(source, GdProperties)
        assert isinstance(target, GdProperties)
        if source != target:
            raise ValueError(source._dif(target))
    
    def data(self)->Generator[None,tuple,None]:
        ''' Yield Blender data and GdResource eq. Within context of load_bl_file for entire duration '''
        
        self.gd_to_bl.options["properties"].properties.set(self.target)
        self.bl_to_gd.options["properties"].properties.set(self.target)
        ## Gd->Bl Transformer requires a pre-set target object (as new object cannot be instanced and attached)

        def clean():
            self.source.clear()
            self.target.clear()
        
        val = GdProperties()
        self.source.store(val)
        yield self.source, val 
        clean()

        val = GdProperties({"a":"b"})
        self.source.store(val)
        yield self.source, val 
        clean()

        val = GdProperties({"a":1.1})
        self.source.store(val)
        yield self.source, val 
        clean()

        val = GdProperties({"a":["a","b"]})
        self.source.store(val)
        yield self.source, val 
        clean()

        val = GdProperties({"a":{"a":"b"}})
        self.source.store(val)
        yield self.source, val 
        clean()
        