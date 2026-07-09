import bpy 

from contextlib import contextmanager

from ..._utils import BlenderPytest

from ....core.structure import (
    GdScene as BlGdScene,           ## Mounted onto Collection! 
    GdNode as BlGdNode,             ## Mounted into Objects!
    SubResource as BlSubResource,
)

from .....GdPy.core.resources import(
    ExtResource as PyExtResource,
    ExtResourceRef as PyExtResourceRef,
    SubResource as PySubResource,
    SubResourceRef as PySubResourceRef,
)
from .....GdPy.core.nodes import(
    ResourceScene as PyResourceScene,
    Node as PyNode,
)

from ....transformers.gdpy import (
    bl_to_py_transformer,
    py_to_bl_transformer,
    BlToPyContext,
    PyToBlContext,
) 



class _BlenderConstructedTest(BlenderPytest):

    def py_to_bl_context(self,)->PyToBlContext:
        c = PyToBlContext()
        # c.collection.set(bpy.data.collections[0])
        return c

    def bl_to_py_context(self,)->BlToPyContext:
        c = BlToPyContext()
        # c.collection.set(bpy.data.collections[0])
        return c

    @contextmanager
    def temp_make(_, make_func):
        obj = bpy.data.objects.new("Node")
        make_func(obj)
        yield obj
        bpy.data.objects.remove(obj)
        
    @staticmethod
    def compare_bl_py(bl:bpy.types.Object, py:PyNode):
        raise NotImplementedError()

    @staticmethod
    def compare_round_trip(base:PyNode, res:PyNode):
        assert base == res

    def test_py_to_bl(self,):
        for py_subres, _ in self.data():
            
            c = self.py_to_bl_context()

            bl_subres = py_to_bl_transformer.transform_tree(c, py_subres)

            self.py_bl_compare(bl_subres, py_subres)

    def test_bl_to_py(self,):
        for _, make in self.data():
            with self.temp_make(make) as bl_subres:

                res = bl_to_py_transformer.transform_tree(BlToPyContext(), bl_subres)

                self.py_bl_compare(bl_subres, res)
    
    def test_round_trip(self,):
        for py_subres, _ in self.data():
            
            py_to_bl_transformer.transform_tree(self.py_to_bl_context(), py_subres)

            py_subres_result = bl_to_py_transformer.transform_tree(self.bl_to_py_context(), self.get_attr())

            self.py_round_trip_compare(py_subres == py_subres_result)

class Test_Node(_BlenderConstructedTest):
    ''' Test creation and export of individual new nodes with all gd attributes in contextual collection '''

    @contextmanager
    def temp_make(_, make_func):
        obj = bpy.data.objects.new("Node")
        make_func(obj)
        yield obj
        bpy.data.objects.remove(obj)
        bpy.data.orphans_purge()

    @staticmethod
    def compare_bl_py(bl:bpy.types.Object, py:PyNode):
        assert bl.name.split(".")[0] == py.name.split(".")[0] 

        assert bl.gd.name == py.name
        assert bl.gd.unique_id == py.unique_id
        assert bl.gd.type == py.type
        assert bl.gd.parent == py.parent
        assert bl.gd.instance == py.instance

        assert len(bl.gd.properties) == len(py.properties)
        assert sorted(list(bl.gd.properties.keys())) == sorted(list(py.properties.keys()))

    @staticmethod
    def compare_round_trip(base:PyNode, res:PyNode):
        assert base == res

    def data(self,):
        res = PyNode.construct(
            "Node",
            unique_id=999999999,
            type="",
            parent=None,
            instance=None,
            properties={}
        )
        @contextmanager
        def _make(obj : bpy.types.Object):
            obj.name = "Node.001"
            gd : BlGdNode = obj.gd
            gd.id = 999999999
            gd.type = ""
            # parent=None
            # gd.properties 
        yield res, _make


class Test_ResourceScene(_BlenderConstructedTest):
    ''' Test creation and export of individual new collections with all gd attributes in a contextual scene 
    Node structure also must be tested
    TODO: 
        - Instancing between scenes - collections (Requires project behavior)
        - Reference Culling behavior
    '''        

    @contextmanager
    def temp_make(_, make_func):
        col = bpy.data.collections.new("Node")
        make_func(col)
        yield col
        bpy.data.collections.remove(col)
        bpy.data.orphans_purge()

    def data(self,):        
        scene = PyResourceScene.construct("uid://abc",
            file = "res://abc",
            nodes=[
                PyNode.construct("Node")
            ],
            ext_resources=[],
            sub_resources=[],
        )
        def _make(col:bpy.types.Collection):
            gd : BlGdScene = col.gd
            gd.uid = "uid://abc"
            gd.file = "res://abc"
        yield scene, _make


        scene = PyResourceScene.construct("uid://abc",
            file = "res://abc",
            nodes=[
                PyNode.construct("NodeA",
                    properties = {
                        "ext_ref" : PyExtResourceRef("extres_id"),
                        "sub_ref" : PySubResourceRef("subres_id"),
                    },
                ),
            ],
            ext_resources=[
                PyExtResource(id="extres_id", uid="uid://xyz", path="res://xyz", type="Resource"),
            ],
            sub_resources=[
                PySubResource.construct("subres_id",
                    type = "SubResource",
                ),
            ],
        )
        def _make(col:bpy.types.Collection):
            gd : BlGdScene = col.gd
            gd.uid = "uid://abc"
            gd.file = "res://abc"
        yield scene, _make


        ## Use of explicit references decreases implicit behavioral deps
        node_a = PyNode.construct("NodeA")
        node_b = PyNode.construct("NodeB",
            parent = node_a,
        )
        node_c = PyNode.construct("NodeC",
            parent = node_a,
        )
        node_d = PyNode.construct("NodeD",
            parent = node_a,
        )
        node_e = PyNode.construct("NodeE",
            parent = node_d,
        )
        node_f = PyNode.construct("NodeF",
            parent = node_e,
        )

        scene = PyResourceScene.construct("uid://abc",
            file = "res://abc",
            nodes=(node_a, node_b, node_c, node_d, node_e, node_f),
            ext_resources=[],
            sub_resources=[],
        )

        def _make(col:bpy.types.Collection):
            gd : BlGdScene = col.gd
            gd.uid = "uid://abc"
            gd.file = "res://abc"
            
            node_a = bpy.data.objects.new("NodeA")
            node_b = bpy.data.objects.new("NodeB")
            node_c = bpy.data.objects.new("NodeC")
            node_d = bpy.data.objects.new("NodeD")
            node_e = bpy.data.objects.new("NodeE")
            node_f = bpy.data.objects.new("NodeF")
            
            node_b.parent(node_a)
            node_c.parent(node_a)
            node_d.parent(node_a)
            node_e.parent(node_d)
            node_f.parent(node_e)

            col.add_object(node_a)
            col.add_object(node_b)
            col.add_object(node_c)
            col.add_object(node_d)
            col.add_object(node_e)
            col.add_object(node_f)

        yield scene, _make