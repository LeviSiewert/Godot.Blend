import bpy
import pytest

from typing import Generator

from ._core import make_bl_to_gd, make_gd_to_bl
from ....GdPy.core.transformer import Session

from ..._test_utils import addon_ensure
from ....addon_config import id_name, addon_path, flag_testing, flag_debug
from ....GdPy.core.structure import (Resource as GdResource, Node as GdNode)


class TransformerDirect():
    ''' Test Gd|Bl Transformer directly
    Project object, if required, impliment in load_bl_file 
        - Side effects of modules also done there
    '''

    bl_to_gd : Session
    gd_to_bl : Session

    def setup(self):
        addon_ensure(True)
        self.bl_to_gd = make_bl_to_gd()
        self.gd_to_bl = make_gd_to_bl()
        self.load_bl_file()

    def teardown(self):
        self.dump_bl_file()        
        self.bl_to_gd = None
        self.gd_to_bl = None
        addon_ensure(False)
        
    def load_bl_file(self):
        ''' Yield and dump blender data w/a. 
        Usefull for setting up visual tests instead of setup & breakdown via code 
        Preferences included 
        '''
    def dump_bl_file(self):
        ''' Yield and dump blender data w/a. 
        Usefull for setting up visual tests instead of setup & breakdown via code 
        Preferences included 
        '''

    def transform_gd_to_bl(self,target:bpy.types.Object|bpy.types.Collection)->GdResource|GdNode:
        return self.gd_to_bl.transform(target)
    
    def transform_bl_to_gd(self,target:GdResource|GdNode)->bpy.types.Object|bpy.types.Collection:
        ''' Transform to new collection, trawl tree && specific attributes '''
        return self.bl_to_gd.transform(target)

    def data(self)->Generator[None,tuple[bpy.types.Object|bpy.types.Collection, GdResource|GdNode],None]:
        ''' Yield Blender data and GdResource eq. Within context of load_bl_file for entire duration '''
        raise NotImplementedError()
        yield None,None

    def test_bl_to_gd(self):
        for bl,gd in self.data():
            source = gd
            result = self.transform_bl_to_gd(bl)
            self.gd_gd_compare(source,result)
    
    def test_gd_to_bl(self):
        for bl,gd in self.data():
            source = gd
            result = self.transform_gd_to_bl(bl)
            self.bl_bl_compare(source,result)

    def test_round_trip_bl(self):
        for bl,gd in self.data():
            source = bl
            result = self.transform_gd_to_bl(self.transform_bl_to_gd(bl))
            self.bl_bl_compare(source, result)

    def test_round_trip_gd(self):
        for bl,gd in self.data():
            source = gd
            result = self.transform_bl_to_gd(self.transform_gd_to_bl(gd))
            self.gd_gd_compare(source, result)

    def bl_bl_compare(self, source, target):
        ## TODO: possibly via dif tree evalation?
        raise NotImplementedError() 

    def gd_gd_compare(self, source, target):
        ## TODO: possibly via dif tree evalation?
        raise NotImplementedError() 

class Test(TransformerDirect):
    ''' Smell test, verify that utilities is calling data as expected '''
    def data(self):
        assert is_addon_registered()
        return
        yield 
