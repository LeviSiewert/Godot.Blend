from __future__ import annotations
from ._test_utils import _StructureTest
from ...core.structure import (
    Properties,
    Project,
    ExtResource,
    File,
    Resource,
    GdSignal,
    Node,
)

from .values import PackedStringArray

from ...core.structure_promise import StructReference, RefType

from ...core.structure import Resource, ExtResource, Node
from ._test_utils import _StructureTest


class Test_Properties(_StructureTest):...

class Test_ExtResource(_StructureTest):...
class Test_GdSignal(_StructureTest):...


class Test_Resource():
    class Test_SubResource(_StructureTest):
        _type = Resource
        _parser_key = "sub_resource"
        def data(self, session):
            txt = '''
                [sub_resource type="Resource" id="a"]
            '''
            res = Resource(type="Resource", id = "a")
            yield txt, res ## Lonesome

            txt = '''
                [sub_resource type="Resource" id="a"]
                value = "Value"
            '''
            res = Resource(type="Resource", id = "a", properties={"value":"Value"})
            yield txt, res ## W/ Properties


    class Test_File(_StructureTest):
        _type = Resource
        _parser_key = "file_resource"
        def data(self, session):
            txt = ''' 
                [gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"] 
                [resource]
                val = "VAL"
            '''
            res = Resource(type="Resource", uid="b52f332102m2l", properties={"val":"VAL"})
            yield txt, res ## Simple!

            txt = '''
                [gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"]

                [sub_resource type="Resource" id="a"]

                [sub_resource type="Resource" id="b"]
                reference=SubResource("a")

                [sub_resource type="Resource" id="c"]
                reference=SubResource("b")

                [resource]
                reference=SubResource("c")
            '''
            res = Resource(type="Resource", uid="uid://b52f332102m2l", properties={
                "reference": Resource(type="Resource", id = "c", properties={
                    "reference": Resource(type="Resource", id = "b", properties={
                        "reference": Resource(type="Resource", id = "a")
                    })
                })
            }) 
            yield txt, res ## Tree!

            txt = """
                [gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"]

                [ext_resource type="Resource" uid="uid://cjkvk7qbv5oby" path="res://ext_res.tres" id="1_2f6dx"]

                [resource]
                reference = ExtResource("1_2f6dx")
            """
            extres = ExtResource(type="Resource", uid="uid://cjkvk7qbv5oby", path="res://ext_res.tres", id="1_2f6dx")
            res = Resource(
                uid = "b52f332102m2l",
                type = "Resource",
                ext_resources=[extres],
                properties={"reference":extres}
            )
            yield txt, res ## ExtResource!

            txt = """
                [gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"]

                [ext_resource type="Resource" uid="uid://cjkvk7qbv5oby" path="res://ext_res.tres" id="1_2f6dx"]

                [sub_resource type="Resource" id="a"]
                reference = ExtResource("1_2f6dx")

                [resource]
                reference=SubResource("a")
            """
            extres = ExtResource(type="Resource", uid="uid://cjkvk7qbv5oby", path="res://ext_res.tres", id="1_2f6dx")
            a = Resource(id="a", properties={"reference":extres})
            res = Resource(
                uid = "b52f332102m2l",
                type = "Resource",
                ext_resources=[extres],
                properties={"reference":a}
            )
            yield txt, res ## Nested Subresource!

    # class Test_SubResource_Indv_Complex(_StructureTest):
    #     _type = Node
    #     _parser_key = "node_resource"
    #     def data(self, session):

    #         txt = '''
    #         [sub_resource type="Resource" id="Resource_0ixfh"]
    #         resource_name = "A"
    #         script = ExtResource("2_8oio5")
    #         r = SubResource("Resource_88bq2")
    #         metadata/_custom_type_script = "uid://cjkvk7qbv5oby"
    #         '''

    #         res = 

class Test_Node():
            

    class Test_Node_Indv(_StructureTest):
        _type = Node
        _parser_key = "node_resource"

        def data(self, session):
            txt = '''
                [node name="Node" type="Node" unique_id=1]
            '''
            res = Node(name="Node", type="Node", id = 1)
            yield txt, res ## Lonesome

            txt = '''
                [node name="Node" type="Node" parent="." unique_id=1]
                value = "Value"
            '''
            res = Node(name="Node", type="Node", id = 1, parent = ".", properties={"value":"Value"})
            yield txt, res ## W/ Properties

            txt = '''
                [node name="Node" type="Control" parent="." unique_id=1]
            '''
            res = Node(name="Node", type="Control", id = 1, parent = ".", properties={"value":"Value"})
            yield txt, res ## Typed

            txt = '''
                [node name="Node" type="Node" parent="." unique_id=1]
                script = ExtResource("ExtResourceID")
            '''
            res = Node(name="Node", type="Node", id = 1, parent = ".", properties={"script":StructReference(ref_type=RefType.EXT_RESOURCE, key="ExtResouurceID")})
            yield txt, res ## Typed & ExtResource 

            txt = '''
                [node name="Node" type="Node" parent="." unique_id=1, instance="InstanceID"]
            '''
            res = Node(name="Node", type="Node", id = 1, parent = ".", instance="InstanceID")
            yield txt, res ## Typed & ExtResource 


    class Test_Scene(_StructureTest):
        _type = Node
        _parser_key = "file_scene"

        def data(self, session):
            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
            '''
            res = Node(type="Node", name="A", id=1936822026, uid="uid://bi8mq3bc2koab", format=3)
            yield txt, res ## Root only

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638]

            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", format=3, children=[
                Node(Name="B", type="Node", id=805633638)
            ])
            yield txt, res ## Root + 1 level

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638]

                [node name="C" type="Node" parent="." unique_id=1360691913]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", format=3, children=[
                Node(Name="B", type="Node", id=805633638),
                Node(Name="C", type="Node", id=1360691913),
            ])
            yield txt, res ## Root + 1 level *2

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638]

                [node name="C" type="Node" parent="." unique_id=1360691913]

                [node name="D" type="Node" parent="C" unique_id=1360691913]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", format=3, children=[
                Node(Name="B", type="Node", id=805633638),
                Node(Name="C", type="Node", id=1360691913, children=[
                    Node(Name="D", type="Node", id=2075458515)
                ]),
            ])
            yield txt, res ## Root + 2 levels

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638]

                [node name="C" type="Node" parent="." unique_id=1360691913]

                [node name="D" type="Node" parent="C" unique_id=2075458515]

                [node name="E" type="Node" parent="C/D" unique_id=116493720]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", format=3, children=[
                Node(Name="B", type="Node", id=805633638),
                Node(Name="C", type="Node", id=1360691913, children=[
                    Node(Name="D", type="Node", id=2075458515, children=[
                        Node(Name="E", type="Node", id=116493720)
                    ]),
                ]),
            ])
            yield txt, res ## Root + 3 levels

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                prop = "A"
                
                [node name="B" type="Node" parent="." unique_id=805633638]
                prop = "B"

                [node name="C" type="Node" parent="." unique_id=1360691913]
                prop = "C"

                [node name="D" type="Node" parent="C" unique_id=2075458515]
                prop = "D"

                [node name="E" type="Node" parent="C/D" unique_id=116493720]
                prop = "E"
            '''
            res = Node(Name="A", properties={"prop":"A"}, type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", format=3, children=[
                Node(Name="B", properties={"prop":"B"}, type="Node", id=805633638),
                Node(Name="C", properties={"prop":"C"}, type="Node", id=1360691913, children=[
                    Node(Name="D", properties={"prop":"D"}, type="Node", id=2075458515, children=[
                        Node(Name="E", properties={"prop":"E"}, type="Node", id=116493720)
                    ]),
                ]),
            ])
            yield txt, res ## Root + 3 levels + Properties

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [ext_resource type="PackedScene" uid="uid" path="res" id="id"]
                
                [node name="A" type="Node" unique_id=1936822026]
                ref = ExtResource("id")
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab",
                ext_resources=[
                    ExtResource(id="id",file="res", uid="uid", type="PackedScene"),
               ],
                properties={
                    "ref":StructReference(ref_type=RefType.EXT_RESOURCE, key="id"),
                },
            )
            
            yield txt, res ## Root + Prop of Extres + ExtRes

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [ext_resource type="PackedScene" uid="uid" path="res" id="id"]
                
                [node name="A" type="Node" unique_id=1936822026, instance=ExtResource("id")]
                ref = ExtResource("id")
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", instance="id",
                ext_resources=[
                    ExtResource(id="id",file="res", uid="uid", type="PackedScene"),
               ],
                properties={
                    "ref":StructReference(ref_type=RefType.EXT_RESOURCE, key="id"),
                },
            )
            yield txt, res ## Root Instance w/ ExtResource


            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [ext_resource type="PackedScene" uid="uid" path="res" id="id"]
                
                [node name="A" type="Node" unique_id=1936822026, instance=ExtResource("id")]
                
                [editable path="."]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", instance="id", instance_editable=True,
                ext_resources=[
                    ExtResource(id="id",file="res", uid="uid", type="PackedScene"),
               ],
            )
            yield txt, res ## Root Instance editable w/ ExtResource


            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [ext_resource type="PackedScene" uid="uid" path="res" id="id"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638, instance=ExtResource("id")]

            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", children=[
                    Node(Name="C", properties={"prop":"C"}, type="Node", id=1360691913, instance="id"), 
            ],
                ext_resources=[
                    ExtResource(id="id",file="res", uid="uid", type="PackedScene"),
               ],
            )
            yield txt, res ## Nested Instance


            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [ext_resource type="PackedScene" uid="uid" path="res" id="id"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638, instance=ExtResource("id")]

                [editable path="B"]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", children=[
                    Node(Name="C", properties={"prop":"C"}, type="Node", id=1360691913, instance="id", instance_editable=True), 
            ],
                ext_resources=[
                    ExtResource(id="id",file="res", uid="uid", type="PackedScene"),
               ],
            )
            
            yield txt, res ## Nested Instance editable

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [connection signal="child_entered_tree" from="." to="." method="_on_child_entered_tree"]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", signals=[
                GdSignal(name="child_entered_tree", fr=".", to=".", method="_on_child_entered_tree")
            ])
            
            yield txt, res ## Basic signal

            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]

                [connection signal="child_entered_tree" from="." to="." method="_on_child_entered_tree" flags=23 unbinds=1 binds= [false, PackedStringArray("A")]]
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", signals=[
                GdSignal(name="child_entered_tree", fr=".", to=".", method="_on_child_entered_tree", flags=23, unbinds=1, binds= [False, PackedStringArray("A")])
            ])
            
            yield txt, res ## Complex Signal


            txt = '''
                [gd_scene format=3 uid="uid://bi8mq3bc2koab"]
                
                [node name="A" type="Node" unique_id=1936822026]
                
                [node name="B" type="Node" parent="." unique_id=805633638]

                [node name="C" type="Node" parent="." unique_id=1360691913]

                [node name="D" type="Node" parent="C" unique_id=1360691913]

                [connection signal="child_entered_tree" from="." to="B" method="_on_child_entered_tree"]

                [connection signal="child_entered_tree" from="B" to="C" method="_on_child_entered_tree"]
                
                [connection signal="child_entered_tree" from="B" to="." method="_on_child_entered_tree"]

                [connection signal="child_entered_tree" from="C" to="C" method="_on_child_entered_tree"]
                
                [connection signal="child_entered_tree" from="D" to="." method="_on_child_entered_tree"]
                
            '''
            res = Node(Name="A", type="Node", id=1936822026, uid="uid://bi8mq3bc2koab", format=3, children=[
                Node(Name="B", type="Node", id=805633638),
                Node(Name="C", type="Node", id=1360691913, children=[
                    Node(Name="D", type="Node", id=2075458515)
                ]),
            ],
            signals = [
                GdSignal(name="child_entered_tree", fr=".", to="B", method="_on_child_entered_tree"),
                GdSignal(name="child_entered_tree", fr="B", to="C", method="_on_child_entered_tree"),
                GdSignal(name="child_entered_tree", fr="B", to=".", method="_on_child_entered_tree"),
                GdSignal(name="child_entered_tree", fr="C", to="C", method="_on_child_entered_tree"),
                GdSignal(name="child_entered_tree", fr="D", to=".", method="_on_child_entered_tree"),   
            ],
            )
            yield txt, res ## Complex/many signals


        

class Test_Options():
    class Test_Category(_StructureTest):
        _type = Category
        _parser_key = "category" 
        def data(self, session):
            txt = '''
                [deps]
                name="A"

            '''
            res = Category(name="deps", properties = {"name":"A"})
            yield txt, res

    class Test_File(_StructureTest):
        _type = FileOptions 
        _parser_key = "file_options" 
        def data(self, session):
            txt = '''
                property="A"

                [A]
                name="A"

                [B]
                name="B"
            '''
            res = FileOptions(
                properties = {
                    "property":"A"
                },
                categories = [
                        Category(name="A", properties = {"name":"A"}),
                        Category(name="B", properties = {"name":"B"}),
                ],
            )
            yield txt, res

        
class Test_Import():
    class Test_File(_StructureTest):
        _type = ImportOptions
        _parser_key = "file_import"
        def data(self,sesson):
            txt = '''
                [remap]

                importer="scene"
                importer_version=1
                type="PackedScene"
                uid="uid://cocfi2vsn5qt2"
                path="res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn"

                [deps]

                source_file="res://assets/blender.glb"
                dest_files=["res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn"]

                [params]

                nodes/root_type=""
                nodes/root_name=""
            '''
            res = ImportOptions(
                importer="scene",
                importer_version=1,
                type="PackedScene",
                uid="uid://cocfi2vsn5qt2",
                path="res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn",
                source_file="res://assets/blender.glb",
                dest_files=["res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn"],
                properties = {
                    "nodes/root_type":"",
                    "nodes/root_name":"",
                },
            )

            yield txt, res


# class Test_Project(_StructureTest):...
# class Test_File(_StructureTest):...