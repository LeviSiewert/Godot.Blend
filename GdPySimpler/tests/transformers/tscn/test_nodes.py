from ._utils import _StructureTest

from ....core.nodes import ResourceScene, Node, EditFlag, SignalNotation
from ....core.subresources import SubResource, SubResourceRef
from ....core.structure import ExtResource, ExtResourceRef
from ....core.values import NodePath, PackedStringArray, Color, Array, PackedByteArray, Dictionary, AABB, PackedByteArray, Vector4

class Test_EditFlag(_StructureTest):
    _type = EditFlag
    _parser_key = "edit_flag"
    def data(self,):
        txt = ''' [editable path="GlbInhheritedEditable"] '''
        res = EditFlag("GlbInhheritedEditable")
        yield txt, res
        
        txt = ''' [editable path="GlbEditable"] '''
        res = EditFlag("GlbEditable")
        yield txt, res
        
        txt = ''' [editable path="GlbEditableAddScript"] '''
        res = EditFlag("GlbEditableAddScript")
        yield txt, res
        
        txt = ''' [editable path="GlbEditableEditProp"] ''' 
        res = EditFlag("GlbEditableEditProp")
        yield txt, res

class Test_ExtResource(_StructureTest):
    _parser_key = "ext_resource"
    _type = ExtResource
    
    def data(self):
        txt = '''[ext_resource type="PackedScene" uid="uid://bvshg3b45tq5b" path="res://assets/blender.glb.tscn" id="1_0xe7n"] '''
        res = ExtResource(type="PackedScene", uid="uid://bvshg3b45tq5b", path="res://assets/blender.glb.tscn", id="1_0xe7n")
        yield txt, res

        txt = '''[ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_w5rjj"] '''
        res = ExtResource(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_w5rjj")
        yield txt, res
        
        txt = '''[ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="3_7d4mc"] '''
        res = ExtResource(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="3_7d4mc")
        yield txt, res

class Test_SignalNotation(_StructureTest):
    _type = SignalNotation
    _parser_key = "signal"
    def data(self,):
        
        txt = '''[connection signal="body_entered" from="." to="." method="_on_door_body_entered"]'''     
        res = SignalNotation(signal="body_entered", fr=".", to=".", method="_on_door_body_entered")
        yield txt, res

        txt = '''[connection signal="body_exited" from="." to="." method="_on_door_body_exited"]'''
        res = SignalNotation(signal="body_exited", fr=".", to=".", method="_on_door_body_exited")
        yield txt, res

class Test_Node(_StructureTest):
    def data(self,):

        txt = '''[node name="Complex" type="Node" unique_id=2079728927]
        '''
        res = Node.construct(name="Complex", type="Node", unique_id=2079728927)
        yield txt,res

        txt = '''[node name="LocalNode" type="Node" parent="." unique_id=531093875]
        '''
        res = Node.construct(
            name="LocalNode", 
            type="Node", 
            parent=".", 
            unique_id=531093875
        )
        yield txt,res

        txt = '''[node name="GlbInhherited" parent="." unique_id=1301180837 instance=ExtResource("1_0xe7n")]
        '''
        res = Node.construct(
            name="GlbInhherited",
            parent=".",
            unique_id=1301180837,
            instance=ExtResourceRef("1_0xe7n"),
        )
        yield txt,res

        txt = '''[node name="GlbInhheritedEditable" parent="." unique_id=370933497 instance=ExtResource("1_0xe7n")]
        '''
        res = Node.construct(
            name="GlbInhheritedEditable" ,
            parent="." ,
            unique_id=370933497 ,
            instance=ExtResourceRef("1_0xe7n"),
        )
        yield txt,res

        txt = '''[node name="GlbInhheritedEditableNewChild" type="Node" parent="GlbInhheritedEditable" unique_id=995826170]
        '''
        res = Node.construct(
            name="GlbInhheritedEditableNewChild",
            type="Node",
            parent="GlbInhheritedEditable",
            unique_id=995826170,
        )
        yield txt,res

        txt = '''[node name="GlbInheritedCubeDuplicated" type="MeshInstance3D" parent="GlbInhheritedEditable" unique_id=679109662]
        mesh = SubResource("ArrayMesh_qt25o")
        '''
        res = Node.construct(
            name="GlbInheritedCubeDuplicated" ,
            type="MeshInstance3D" ,
            parent="GlbInhheritedEditable" ,
            unique_id=679109662,
            properties = {
                "mesh" : SubResourceRef("ArrayMesh_qt25o"),
            },
        )
        yield txt,res

        txt = '''[node name="Glb" parent="." unique_id=735050992 instance=ExtResource("1_w5rjj")]
        '''
        res = Node.construct(
            name="Glb",
            parent=".",
            unique_id=735050992,
            instance=ExtResourceRef("1_w5rjj"),
        )
        yield txt,res

        txt = '''[node name="GlbEditable" parent="." unique_id=1248585079 instance=ExtResource("1_w5rjj")]
        '''
        res = Node.construct(
            name="GlbEditable",
            parent=".",
            unique_id=1248585079,
            instance=ExtResourceRef("1_w5rjj"),
        )
        yield txt,res

        txt = '''[node name="GlbEditableNewChild" type="Node" parent="GlbEditable" unique_id=1176021808]
        '''
        res = Node.construct(
            name="GlbEditableNewChild",
            type="Node",
            parent="GlbEditable",
            unique_id=1176021808,
        )
        yield txt,res

        txt = '''[node name="GlbEditableAddScript" parent="." unique_id=621548348 instance=ExtResource("1_w5rjj")]
        '''
        res = Node.construct(
            name="GlbEditableAddScript",
            parent=".",
            unique_id=621548348,
            instance=ExtResourceRef("1_w5rjj"),
        )
        yield txt,res

        txt = '''[node name="Cube" parent="GlbEditableAddScript" index="0" unique_id=895413058 node_paths=PackedStringArray("noderef")]
        script = ExtResource("3_7d4mc")
        noderef = NodePath("..")
        '''
        res = Node.construct(
            name="Cube",
            parent="GlbEditableAddScript",
            index="0",
            unique_id=895413058,
            node_paths=PackedStringArray("noderef"),
            properties = {
                "script" : ExtResourceRef("3_7d4mc"),
                "noderef" : NodePath(".."),
            },
        )
        yield txt,res

        txt = '''[node name="GlbEditableEditProp" parent="." unique_id=726661338 instance=ExtResource("1_w5rjj")]
        '''
        res = Node.construct(
            name="GlbEditableEditProp",
            parent=".", 
            unique_id=726661338, 
            instance=ExtResourceRef("1_w5rjj"),
        )
        yield txt,res

        txt = '''[node name="Cube" parent="GlbEditableEditProp" index="0" unique_id=895413058]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 3, 0, 0)
        '''
        res = Node.construct(
            name="Cube" ,
            parent="GlbEditableEditProp" ,
            index="0" ,
            unique_id=895413058,
        )
        yield txt,res


class Test_ResourceScene(_StructureTest):
    def data(self,):
        yield from self.data_simple()
        yield from self.data_complex()
    
    def data_simple():
        
        pass

    def data_complex(self,):
        txt = """[gd_scene format=3 uid="uid://bvshg3b45tq5b"]

        [ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_8vle4"]
        
        [node name="blender" unique_id=1301180837 instance=ExtResource("1_8vle4")]
        
        [node name="InheritedSceneChild" type="Node" parent="." index="0" unique_id=140602464]
        """

        res = ResourceScene.construct(
            format=3,
            uid="uid://bvshg3b45tq5b",
            ext_resources=[
                ExtResource(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_8vle4"),
            ],
            nodes = [

                Node.construct(
                    name="blender",
                    unique_id=1301180837 ,
                    instance=ExtResourceRef("1_8vle4"),
                ),
                Node.construct(
                    name="InheritedSceneChild" ,
                    type="Node" ,
                    parent="." ,
                    index="0" ,
                    unique_id=140602464,
                ),
            ],
        )
        yield txt,res

        txt = """
        [gd_scene format=4 uid="uid://ccmipxvllo1c0"]

        [ext_resource type="PackedScene" uid="uid://bvshg3b45tq5b" path="res://assets/blender.glb.tscn" id="1_0xe7n"]
        [ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_w5rjj"]
        [ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="3_7d4mc"]

        [sub_resource type="StandardMaterial3D" id="StandardMaterial3D_6cmw1"]
        resource_name = "Material"
        cull_mode = 2
        albedo_color = Color(0.9063318, 0.9063318, 0.9063318, 1)
        roughness = 0.5

        [sub_resource type="ArrayMesh" id="ArrayMesh_3l6rm"]
        _surfaces = [{
        "aabb": AABB(-1, -1, -1, 2, 2, 2),
        "format": 34896613377,
        "index_count": 36,
        "index_data": PackedByteArray("AAABAAIAAwACAAEAAAAEAAEAAwAFAAIABQAAAAIABgAEAAAABQAGAAAABwABAAQABwADAAEABgAHAAQABQADAAcABQAHAAYA"),
        "name": "Material",
        "primitive": 3,
        "uv_scale": Vector4(0, 0, 0, 0),
        "vertex_count": 8,
        "vertex_data": PackedByteArray("/////wAAAAAAAP////8AAAAA//8AAAAAAAAAAP//AAD///////8AAAAAAAAAAAAA//8AAAAAAAD//wAA//8AAA==")
        }]
        blend_shape_mode = 0

        [sub_resource type="ArrayMesh" id="ArrayMesh_qt25o"]
        resource_name = "blender_Cube"
        _surfaces = [{
        "aabb": AABB(-1, -1, -1, 2, 2, 2),
        "attribute_data": PackedByteArray("/5//f//f/z//3/9//5//P/9f/z//nwAA/5//P/9fAAD/X////5//v/+f////X/+//x//f/9f/z//X/9//x//P/9f/3//n/8//5//f/9f/z//X/+//5//f/+f/7//X/9/"),
        "format": 34896613399,
        "index_count": 36,
        "index_data": PackedByteArray("AAABAAIAAAADAAEABAAFAAYABAAHAAUACAAJAAoACAALAAkADAANAA4ADAAPAA0AEAARABIAEAATABEAFAAVABYAFAAXABUA"),
        "material": SubResource("StandardMaterial3D_6cmw1"),
        "name": "Material",
        "primitive": 3,
        "uv_scale": Vector4(0, 0, 0, 0),
        "vertex_count": 24,
        "vertex_data": PackedByteArray("/////wAA//8AAP///////wAA//8AAP///////////////wAA////vwAA//////+//////////78AAAAA////vwAAAAD//1TVAAD//wAAVNUAAP////9U1QAAAAAAAFTVAAAAAAAA/7///wAA////v///AAAAAP+/AAAAAP///7///wAAAABU1f///////1TV/////wAAVNX//wAA//9U1QAAAAAAAP///////wAA//8AAP//AAD/////AAAAAP///3//v/9//7//f/+//3//v/////////////////////9U1VTVVNVU1VTVVNVU1VTVAAD/fwAA/38AAP9/AAD/f6oqqiqqKqoqqiqqKqoqqir/v/+//7//v/+//7//v/+/")
        }]
        blend_shape_mode = 0
        shadow_mesh = SubResource("ArrayMesh_3l6rm")

        [node name="Complex" type="Node" unique_id=2079728927]

        [node name="LocalNode" type="Node" parent="." unique_id=531093875]

        [node name="GlbInhherited" parent="." unique_id=1301180837 instance=ExtResource("1_0xe7n")]

        [node name="GlbInhheritedEditable" parent="." unique_id=370933497 instance=ExtResource("1_0xe7n")]

        [node name="GlbInhheritedEditableNewChild" type="Node" parent="GlbInhheritedEditable" unique_id=995826170]

        [node name="GlbInheritedCubeDuplicated" type="MeshInstance3D" parent="GlbInhheritedEditable" unique_id=679109662]
        mesh = SubResource("ArrayMesh_qt25o")

        [node name="Glb" parent="." unique_id=735050992 instance=ExtResource("1_w5rjj")]

        [node name="GlbEditable" parent="." unique_id=1248585079 instance=ExtResource("1_w5rjj")]

        [node name="GlbEditableNewChild" type="Node" parent="GlbEditable" unique_id=1176021808]

        [node name="GlbEditableAddScript" parent="." unique_id=621548348 instance=ExtResource("1_w5rjj")]

        [node name="Cube" parent="GlbEditableAddScript" index="0" unique_id=895413058 node_paths=PackedStringArray("noderef")]
        script = ExtResource("3_7d4mc")
        noderef = NodePath("..")

        [node name="GlbEditableEditProp" parent="." unique_id=726661338 instance=ExtResource("1_w5rjj")]

        [node name="Cube" parent="GlbEditableEditProp" index="0" unique_id=895413058]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 3, 0, 0)

        [editable path="GlbInhheritedEditable"]
        [editable path="GlbEditable"]
        [editable path="GlbEditableAddScript"]
        [editable path="GlbEditableEditProp"]
        """

        res = ResourceScene.construct(
            format=4, 
            uid="uid://ccmipxvllo1c0",
            ext_resources = [
                ExtResource(type="PackedScene", uid="uid://bvshg3b45tq5b", path="res://assets/blender.glb.tscn", id="1_0xe7n"),
                ExtResource(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_w5rjj"),
                ExtResource(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="3_7d4mc"),
            ], 
            sub_resources = [
                SubResource.construct(
                    type="StandardMaterial3D", 
                    id="StandardMaterial3D_6cmw1",
                    properties = {
                        "resource_name" : "Material",
                        "cull_mode" : 2,
                        "albedo_color" : Color(0.9063318, 0.9063318, 0.9063318, 1),
                        "roughness" : 0.5,
                    },
                ),
                SubResource.construct(
                    type="ArrayMesh", 
                    id="ArrayMesh_3l6rm",
                    properties = {
                        "_surfaces" : Array({
                            "aabb": AABB(-1, -1, -1, 2, 2, 2),
                            "format": 34896613377,
                            "index_count": 36,
                            "index_data": PackedByteArray("AAABAAIAAwACAAEAAAAEAAEAAwAFAAIABQAAAAIABgAEAAAABQAGAAAABwABAAQABwADAAEABgAHAAQABQADAAcABQAHAAYA"),
                            "name": "Material",
                            "primitive": 3,
                            "uv_scale": Vector4(0, 0, 0, 0),
                            "vertex_count": 8,
                            "vertex_data": PackedByteArray("/////wAAAAAAAP////8AAAAA//8AAAAAAAAAAP//AAD///////8AAAAAAAAAAAAA//8AAAAAAAD//wAA//8AAA==")
                            }),
                        "blend_shape_mode" : 0,
                    },
                ),
                SubResource.construct(
                    type="ArrayMesh",
                    id="ArrayMesh_qt25o",
                    properties = {
                        "resource_name" : "blender_Cube",
                        "_surfaces" : Array({
                            "aabb": AABB(-1, -1, -1, 2, 2, 2),
                            "attribute_data": PackedByteArray("/5//f//f/z//3/9//5//P/9f/z//nwAA/5//P/9fAAD/X////5//v/+f////X/+//x//f/9f/z//X/9//x//P/9f/3//n/8//5//f/9f/z//X/+//5//f/+f/7//X/9/"),
                            "format": 34896613399,
                            "index_count": 36,
                            "index_data": PackedByteArray("AAABAAIAAAADAAEABAAFAAYABAAHAAUACAAJAAoACAALAAkADAANAA4ADAAPAA0AEAARABIAEAATABEAFAAVABYAFAAXABUA"),
                            "material": SubResource("StandardMaterial3D_6cmw1"),
                            "name": "Material",
                            "primitive": 3,
                            "uv_scale": Vector4(0, 0, 0, 0),
                            "vertex_count": 24,
                            "vertex_data": PackedByteArray("/////wAA//8AAP///////wAA//8AAP///////////////wAA////vwAA//////+//////////78AAAAA////vwAAAAD//1TVAAD//wAAVNUAAP////9U1QAAAAAAAFTVAAAAAAAA/7///wAA////v///AAAAAP+/AAAAAP///7///wAAAABU1f///////1TV/////wAAVNX//wAA//9U1QAAAAAAAP///////wAA//8AAP//AAD/////AAAAAP///3//v/9//7//f/+//3//v/////////////////////9U1VTVVNVU1VTVVNVU1VTVAAD/fwAA/38AAP9/AAD/f6oqqiqqKqoqqiqqKqoqqir/v/+//7//v/+//7//v/+/")
                            }),
                        "blend_shape_mode" : 0,
                        "shadow_mesh" : SubResource("ArrayMesh_3l6rm"),
                    },
                ),
            ],

            nodes = [
                Node.construct(
                    name="Complex", 
                    type="Node", 
                    unique_id=2079728927
                ),
                Node.construct(
                    name="LocalNode", 
                    type="Node", 
                    parent=".", 
                    unique_id=531093875
                ),
                Node.construct(
                    name="GlbInhherited",
                    parent=".",
                    unique_id=1301180837,
                    instance=ExtResourceRef("1_0xe7n"),
                ),
                Node.construct(
                    name="GlbInhheritedEditable" ,
                    parent="." ,
                    unique_id=370933497 ,
                    instance=ExtResourceRef("1_0xe7n"),
                ),
                Node.construct(
                    name="GlbInhheritedEditableNewChild",
                    type="Node",
                    parent="GlbInhheritedEditable",
                    unique_id=995826170,
                ),
                Node.construct(
                    name="GlbInheritedCubeDuplicated" ,
                    type="MeshInstance3D" ,
                    parent="GlbInhheritedEditable" ,
                    unique_id=679109662,
                    properties = {
                        "mesh" : SubResourceRef("ArrayMesh_qt25o"),
                    },
                ),
                Node.construct(
                    name="Glb",
                    parent=".",
                    unique_id=735050992,
                    instance=ExtResourceRef("1_w5rjj"),
                ),
                Node.construct(
                    name="GlbEditable",
                    parent=".",
                    unique_id=1248585079,
                    instance=ExtResourceRef("1_w5rjj"),
                ),
                Node.construct(
                    name="GlbEditableNewChild",
                    type="Node",
                    parent="GlbEditable",
                    unique_id=1176021808,
                ),
                Node.construct(
                    name="GlbEditableAddScript",
                    parent=".",
                    unique_id=621548348,
                    instance=ExtResourceRef("1_w5rjj"),
                ),
                Node.construct(
                    name="Cube",
                    parent="GlbEditableAddScript",
                    index="0",
                    unique_id=895413058,
                    node_paths=PackedStringArray("noderef"),
                    properties = {
                        "script" : ExtResourceRef("3_7d4mc"),
                        "noderef" : NodePath(".."),
                    },
                ),
                Node.construct(
                    name="GlbEditableEditProp",
                    parent=".", 
                    unique_id=726661338, 
                    instance=ExtResourceRef("1_w5rjj"),
                ),
                Node.construct(
                    name="Cube" ,
                    parent="GlbEditableEditProp" ,
                    index="0" ,
                    unique_id=895413058,
                ), 
            ],

            edit_flags = [
                EditFlag(path="GlbInhheritedEditable"),
                EditFlag(path="GlbEditable"),
                EditFlag(path="GlbEditableAddScript"),
                EditFlag(path="GlbEditableEditProp"),
            ],
        )
        yield txt,res