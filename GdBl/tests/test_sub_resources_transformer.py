import bpy
from ._utils import BlenderPytestAttr, BlenderPytest

from ..structure.sub_resources import (
    SubResource as BlSubResource, 
    SubResourceCategory as BlSubResourceCategory, 
    SubResourceExt as BlSubResourceExt, 
    SubResourceNode as BlSubResourceNode
    )
from ...GdPy.structure.sub_resources import (
    SubResource as GdSubResource, 
    SubResourceCategory as GdSubResourceCategory, 
    SubResourceExt as GdSubResourceExt, 
    SubResourceNode as GdSubResourceNode
    )

class TestSubResourceExt(BlenderPytestAttr):
    attr = bpy.props.PointerProperty(type = BlSubResource)

    def test_bl_to_py(self,):
        raise NotImplementedError(self.__class__.__name__)
    def test_py_to_bl(self,):
        raise NotImplementedError(self.__class__.__name__)
    
class TestSubResourceCategory(BlenderPytestAttr):
    attr = bpy.props.PointerProperty(type = BlSubResourceCategory)

    def test_bl_to_py(self,):
        raise NotImplementedError(self.__class__.__name__)
    def test_py_to_bl(self,):
        raise NotImplementedError(self.__class__.__name__)
    
class TestSubResource(BlenderPytestAttr):
    attr = bpy.props.PointerProperty(type = BlSubResourceExt)

    def test_bl_to_py(self,):
        raise NotImplementedError(self.__class__.__name__)
    def test_py_to_bl(self,):
        raise NotImplementedError(self.__class__.__name__)

class TestSubResourceNode(BlenderPytest):
    ''' Generating and applying attributes onto a new empty, subtype testing is part of modular implemenation 
    INITIAL: (TreeZip) transformers will be prioritized and supercede this transformer
    '''

    def test_bl_to_py(self,):
        raise NotImplementedError(self.__class__.__name__)
    def test_py_to_bl(self,):
        raise NotImplementedError(self.__class__.__name__)
