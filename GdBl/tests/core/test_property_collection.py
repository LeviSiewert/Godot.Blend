import bpy

from .._utils import BlenderPytestAttr
from ...core.property_collection import (
    GdPrimitive,
    GdVector,
    GdReference,
    GdDictionary,
    GdArray,
    GdPropertyCollection,
)

class Test_GdPrimitive(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type = GdPrimitive)
    def test(self,):
        raise NotImplementedError()

class Test_GdVector(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type = GdVector)
    def test(self,):
        raise NotImplementedError()

class Test_GdReference(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type = GdReference)
    def test(self,):
        raise NotImplementedError()

class Test_GdDictionary(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type = GdDictionary)
    def test(self,):
        raise NotImplementedError()

class Test_GdArray(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type = GdArray)
    def test(self,):
        raise NotImplementedError()

class Test_GdPropertyCollection(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type = GdPropertyCollection)
    def test(self,):
        raise NotImplementedError()


