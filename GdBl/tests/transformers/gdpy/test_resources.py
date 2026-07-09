import bpy
from ..._utils import BlenderPytestAttr
from typing import Generator,Any,Callable

from ....transformers.gdpy import (
    bl_to_py_transformer,
    py_to_bl_transformer,
    BlToPyContext,
    PyToBlContext,
) 

from ....core.structure import (
    SubResource as BlSubResource,
    ExtResource as BlExtResource,
    GdResource as BlGdResource,
)

from .....GdPy.core.resources import(
    SubResource as PySubResource,
    ExtResource as PyExtResource,
    ResourceTres as PyResourceTres,
    SubResourceRef as PySubResourceRef,
)

from contextlib import contextmanager

def str_eq_none(a,b):
    if a is None:
        a = ""
    if b is None:
        b = ""
    return a == b

class _StructureTest(BlenderPytestAttr):    
    # def test_py_to_bl(self,):
    #     bl_subres : BlSubResource = self.get_attr()
    #     for py_subres,_ in self.data():
    #         with self.temp_attr():
    #             c = self.py_to_bl_context()

    #             py_to_bl_transformer.transform_tree(c, py_subres)

    #             self.py_bl_compare(bl_subres, py_subres)

    # def test_bl_to_py(self,):
    #     bl_subres : BlSubResource = self.get_attr()
    #     for _, make in self.data():
    #         with self.temp_attr():
    #             make(bl_subres)

    #             res : PySubResource = bl_to_py_transformer.transform_tree(BlToPyContext(), self.get_attr())

    #             self.py_bl_compare(bl_subres, res)
    
    def test_round_trip(self,):
        for py_subres, _ in self.data():
            with self.temp_attr():
                py_to_bl_transformer.transform_tree(self.py_to_bl_context(), py_subres)

                py_subres_result = bl_to_py_transformer.transform_tree(self.bl_to_py_context(), self.get_attr())

                self.py_round_trip_compare(py_subres, py_subres_result)

    @classmethod
    def py_round_trip_compare(cls, base, result):
        ''' Compare absolute locals, extrensics of subs. Reduces test surface area '''
        assert base == result

    @classmethod
    def py_bl_compare(cls, bl, py):
        ''' Compare absolute locals, extrensics of subs. Reduces test surface area '''
        raise NotImplementedError()
    
    def py_to_bl_context(self,)->PyToBlContext:
        c = PyToBlContext()
        c.existing_object.set(self.get_attr())
        return c

    def bl_to_py_context(self,)->BlToPyContext:
        return BlToPyContext()

    def data(self,)->Generator[Any,Callable]:
        raise NotImplementedError

class Test_SubResource(_StructureTest):
    property_type = bpy.props.PointerProperty(type = BlSubResource)

    @contextmanager
    def temp_attr(self,):
        yield
        attr : BlSubResource = self.get_attr()
        attr.name = ""
        attr.type = ""
        attr.script_type = ""
        attr.properties.clear()


    @classmethod
    def py_bl_compare(cls, bl, py):
        assert bl.name == py.id
        assert bl.type == py.type
        assert bl.script_type == py.script_type
        assert len(bl.properties) == len(py.properties)
        assert list(bl.properties.keys()) == list(py.properties.keys())

    @classmethod
    def py_round_trip_compare(cls, base:PySubResource, result:PySubResource):
        assert len(base.properties) == len(result.properties)
        assert list(base.properties.keys()) == list(result.properties.keys())
        base.properties.clear()
        result.properties.clear()
        assert base == result

    def data(self,)->Generator[Any,Callable]:
        res = PySubResource.construct(
            type="CameraAttributesPractical",
            id="CameraAttributesPractical_fssom",
        )
        def _make(bl:BlSubResource):
            bl.name = "CameraAttributesPractical_fssom" 
            bl.type = "CameraAttributesPractical"
        yield res,_make

        res = PySubResource.construct(
            type="ProceduralSkyMaterial",
            id="ProceduralSkyMaterial_6okqy",
        )
        def _make(bl:BlSubResource):
            bl.name = "ProceduralSkyMaterial_6okqy" 
            bl.type = "ProceduralSkyMaterial"
        yield res,_make
        

        res = PySubResource.construct(
            type="Sky",
            id="Sky_b8yvd",
            properties={
                "sky_material" : PySubResourceRef("ProceduralSkyMaterial_6okqy"),
            },
        )
        def _make(bl):
            bl.type="Sky",
            bl.name="Sky_b8yvd",

            ## Standin properties, reduces dependencies 
            bl.properties["sky_material"] = None 
        yield res,_make
            

        res = PySubResource.construct(
            type="Environment",
            id="Environment_gatl5",
            properties={
                "background_mode" : 2,
                "sky" : PySubResourceRef("Sky_b8yvd"),
                "ambient_light_source" : 3,
            },
        )
        def _make(bl):
            bl.type="Environment",
            bl.name="Environment_gatl5",
            ## Standin properties, reduces dependencies 
            bl.properties["background_mode"] = None 
            bl.properties["sky"] = None 
            bl.properties["ambient_light_source"] = None 
        yield res,_make

        res = PySubResource.construct(
            type="Environment",
            id="Environment_c5o2k",
        )
        def _make(bl):
            bl.type="Environment",
            bl.name="Environment_c5o2k",
        yield res,_make


class Test_ExtResources(_StructureTest):
    property_type = bpy.props.PointerProperty(type = BlExtResource)
        
    @contextmanager
    def temp_attr(self,):
        yield
        attr : BlExtResource = self.get_attr()
        attr.name = ""
        attr.uid = ""
        attr.path = ""
        attr.type = ""

    def data(self,):
        res = PyExtResource(id="extres_id", uid="uid://xyz", path="res://xyz", type="Resource")
        def _make(bl:BlExtResource):
            bl.name="extres_id"
            bl.uid="uid://xyz"
            bl.path="res://xyz" 
            bl.type="Resource"
        yield res, _make

    
class Test_Resources(_StructureTest):
    property_type = bpy.props.PointerProperty(type = BlGdResource)

    @contextmanager
    def temp_attr(self,):
        yield
        attr : BlGdResource = self.get_attr()
        attr.ext_resources.clear()
        attr.sub_resources.clear()
        attr.properties.clear()
        attr.name = ""
        attr.type = ""
        attr.script_class = ""

    @classmethod
    def py_bl_compare(cls, bl, py):
        assert str_eq_none(bl.name, py.uid.get())
        assert str_eq_none(bl.file, py.file.addr)
        assert str_eq_none(bl.type, py.type)
        assert str_eq_none(bl.script_class, py.script_class)
        assert bl.format == py.format
        assert len(bl.properties) == len(py.properties)
        assert len(bl.ext_resources) == len(py.ext_resources)
        assert len(bl.sub_resources) == len(py.sub_resources)

    @classmethod
    def py_round_trip_compare(cls, base:PySubResource, result:PySubResource):
        assert len(base.properties) == len(result.properties)
        assert list(base.properties.keys()) == list(result.properties.keys())
        base.properties.clear()
        result.properties.clear()

        assert len(base.ext_resources) == len(result.ext_resources)
        # assert list(base.ext_resources.keys()) == list(result.ext_resources.keys())
        base.ext_resources.clear()
        result.ext_resources.clear()

        assert len(base.sub_resources) == len(result.sub_resources)
        # assert list(base.sub_resources.keys()) == list(result.sub_resources.keys())
        base.sub_resources.clear()
        result.sub_resources.clear()

        assert base == result


    def data(self,)->Generator[Any,Callable]:
        res = PyResourceTres.construct(
            uid="uid://abc",
            file="res://abc",
            type="TestType",
            format=3,
            script_class=None,
            properties={},
            ext_resources=[],
            sub_resources=[],
        )
        def _make(bl:BlGdResource):
            bl.file = "res://abc"
            bl.name = "uid://abc"
            bl.type = "TestType"
            bl.format = 3
            bl.script_class = ""
        yield res,_make
        
        res = PyResourceTres.construct(
            uid="uid://abc",
            file="res://abc",
            type="TestType",
            format=3,
            script_class="SOMETYPE",
            properties={
                "Property" : "Value"
            },
            ext_resources=[
                PyExtResource(id="extres_id", uid="uid://xyz", path="res://xyz", type="Resource"),
            ],
            sub_resources=[
                PySubResource.construct("subres_id"),
            ],
        )
        def _make(bl:BlGdResource):
            bl.file = "res://abc"
            bl.name = "uid://abc"
            bl.type = "TestType"
            bl.format = 3
            bl.script_class = ""
            bl.properties["Property"] = "Value"
            
            ext_res = bl.ext_resources.add()
            ext_res.name = "extres_id"
            ... #TODO

            sub_res = bl.sub_resources.add()
            sub_res.name = "subres_id"
            ... #TODO
        yield res,_make

