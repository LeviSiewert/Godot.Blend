import pytest

from ...core.structure import *
from ...core.values import *

@pytest.fixture
def std_project():
    ''' Standard complex scenes to construct and reference from '''
    file_a = FileLocal(path="res://assets/blender.glb", data=data_b)
    data_a = ResourceScene.construct(uid="uid://cocfi2vsn5qt2",
        sub_resources = [
            SubResource(type = "ArrayMesh", unique_id="ArrayMesh_3l6ra", properties = {
                "_surfaces" : [{
                    "aabb": AABB(-1, -1, -1, 2, 2, 2),
                    "format": 34896613377,
                    "index_count": 36,
                    "index_data": PackedByteArray("AAABAAIAAwACAAEAAAAEAAEAAwAFAAIABQAAAAIABgAEAAAABQAGAAAABwABAAQABwADAAEABgAHAAQABQADAAcABQAHAAYA"),
                    "name": "Material",
                    "primitive": 3,
                    "uv_scale": Vector4(0, 0, 0, 0),
                    "vertex_count": 8,
                    "vertex_data": PackedByteArray("/////wAAAAAAAP////8AAAAA//8AAAAAAAAAAP//AAD///////8AAAAAAAAAAAAA//8AAAAAAAD//wAA//8AAA==")
                }],
                "blend_shape_mode" : 0,
            }),
            SubResource(type = "ArrayMesh", unique_id="ArrayMesh_qt25b", properties = {
                "resource_name" : "blender_Cube",
                "_surfaces" : [{
                    "aabb": AABB(-1, -1, -1, 2, 2, 2),
                    "attribute_data": PackedByteArray("/5//f//f/z//3/9//5//P/9f/z//nwAA/5//P/9fAAD/X////5//v/+f////X/+//x//f/9f/z//X/9//x//P/9f/3//n/8//5//f/9f/z//X/+//5//f/+f/7//X/9/"),
                    "format": 34896613399,
                    "index_count": 36,
                    "index_data": PackedByteArray("AAABAAIAAAADAAEABAAFAAYABAAHAAUACAAJAAoACAALAAkADAANAA4ADAAPAA0AEAARABIAEAATABEAFAAVABYAFAAXABUA"),
                    "material": SubResourceRef("StandardMaterial3D_6cmw1"),
                    "name": "Material",
                    "primitive": 3,
                    "uv_scale": Vector4(0, 0, 0, 0),
                    "vertex_count": 24,
                    "vertex_data": PackedByteArray("/////wAA//8AAP///////wAA//8AAP///////////////wAA////vwAA//////+//////////78AAAAA////vwAAAAD//1TVAAD//wAAVNUAAP////9U1QAAAAAAAFTVAAAAAAAA/7///wAA////v///AAAAAP+/AAAAAP///7///wAAAABU1f///////1TV/////wAAVNX//wAA//9U1QAAAAAAAP///////wAA//8AAP//AAD/////AAAAAP///3//v/9//7//f/+//3//v/////////////////////9U1VTVVNVU1VTVVNVU1VTVAAD/fwAA/38AAP9/AAD/f6oqqiqqKqoqqiqqKqoqqir/v/+//7//v/+//7//v/+/")
                }],
                "blend_shape_mode" : 0,
                "shadow_mesh" : SubResourceRef("ArrayMesh_3l6ra"),
            }),
            
        ],
        nodes_resources = [
            Node(name="blender", unique_id=1301180838),
            Node(name="InheritedSceneChild", type="Node", parent=".", index="0", unique_id=140602465),
            Node(name="Cube", type="MeshInstance3D", parent=".", index="1", unique_id=140602468, properties = {
                "mesh":SubResourceRef("ArrayMesh_qt25o"),
            }),
        ]
    )

    file_b = FileLocal(path="res://assets/blender.glb.tscn", data=data_a )
    data_b = ResourceScene.construct(uid="uid://bvshg3b45tq5b", format=3,
        ext_references = [
            ExtReference(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_8vle4"),
            ],
        nodes_resources = [
            Node(name="blender", unique_id=1301180837, instance=ExtResourceRef("1_8vle4")),
            Node(name="InheritedSceneChild", type="Node", parent=".", index="0", unique_id=140602464),
        ]
    )

    data_c = ResourceScript(uid="uid://cr1tpol7u62kd")
    file_c = FileLocal(path="res://assets/script.gd", data=data_c)

    data_d = ResourceScene.construct(uid = "uid://ccmipxvllo1c0", format=4, 
        ext_references = [
            ExtReference(type="PackedScene", uid="uid://bvshg3b45tq5b", path="res://assets/blender.glb.tscn", id="1_0xe7n"),
            ExtReference(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_w5rjj"),
            ExtReference(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="3_7d4mc"),
        ],
        sub_resources = [
            SubResource(type="StandardMaterial3D", id="StandardMaterial3D_6cmw1", properties = {
                "resource_name" : "Material",
                "cull_mode" : 2,
                "albedo_color" : Color(0.9063318, 0.9063318, 0.9063318, 1),
                "roughness" : 0.5,
            }),
            SubResource(type="ArrayMesh", id="ArrayMesh_3l6rm", properties = {
                '_surfaces' : [{
                    "aabb": AABB(-1, -1, -1, 2, 2, 2),
                    "format": 34896613377,
                    "index_count": 36,
                    "index_data": PackedByteArray("AAABAAIAAwACAAEAAAAEAAEAAwAFAAIABQAAAAIABgAEAAAABQAGAAAABwABAAQABwADAAEABgAHAAQABQADAAcABQAHAAYA"),
                    "name": "Material",
                    "primitive": 3,
                    "uv_scale": Vector4(0, 0, 0, 0),
                    "vertex_count": 8,
                    "vertex_data": PackedByteArray("/////wAAAAAAAP////8AAAAA//8AAAAAAAAAAP//AAD///////8AAAAAAAAAAAAA//8AAAAAAAD//wAA//8AAA==")
                }],
                'blend_shape_mode' : 0,
            }),
            SubResource(type="ArrayMesh", id="ArrayMesh_qt25o", properties = {
                'resource_name' : "blender_Cube",
                '_surfaces' : [{
                    "aabb": AABB(-1, -1, -1, 2, 2, 2),
                    "attribute_data": PackedByteArray("/5//f//f/z//3/9//5//P/9f/z//nwAA/5//P/9fAAD/X////5//v/+f////X/+//x//f/9f/z//X/9//x//P/9f/3//n/8//5//f/9f/z//X/+//5//f/+f/7//X/9/"),
                    "format": 34896613399,
                    "index_count": 36,
                    "index_data": PackedByteArray("AAABAAIAAAADAAEABAAFAAYABAAHAAUACAAJAAoACAALAAkADAANAA4ADAAPAA0AEAARABIAEAATABEAFAAVABYAFAAXABUA"),
                    "material": SubResourceRef("StandardMaterial3D_6cmw1"),
                    "name": "Material",
                    "primitive": 3,
                    "uv_scale": Vector4(0, 0, 0, 0),
                    "vertex_count": 24,
                    "vertex_data": PackedByteArray("/////wAA//8AAP///////wAA//8AAP///////////////wAA////vwAA//////+//////////78AAAAA////vwAAAAD//1TVAAD//wAAVNUAAP////9U1QAAAAAAAFTVAAAAAAAA/7///wAA////v///AAAAAP+/AAAAAP///7///wAAAABU1f///////1TV/////wAAVNX//wAA//9U1QAAAAAAAP///////wAA//8AAP//AAD/////AAAAAP///3//v/9//7//f/+//3//v/////////////////////9U1VTVVNVU1VTVVNVU1VTVAAD/fwAA/38AAP9/AAD/f6oqqiqqKqoqqiqqKqoqqir/v/+//7//v/+//7//v/+/")
                    }],
                'blend_shape_mode' : 0,
                'shadow_mesh' : SubResourceRef("ArrayMesh_3l6rm"),
            }),
        ],
        node_resources = [
            Node(name="Complex", type="Node", unique_id=2079728927),
            Node(name="LocalNode", type="Node", parent=".", unique_id=531093875),
            Node(name="GlbInhherited", parent=".", unique_id=1301180837, instance=ExtResourceRef("1_0xe7n")),
            Node(name="GlbInhheritedEditable", parent=".", unique_id=370933497, instance=ExtResourceRef("1_0xe7n")),
            Node(name="GlbInhheritedEditableNewChild", type="Node", parent="GlbInhheritedEditable", unique_id=995826170),
            Node(name="GlbInheritedCubeDuplicated", type="MeshInstance3D", parent="GlbInhheritedEditable", unique_id=679109662, properties = {
                "mesh" : SubResource("ArrayMesh_qt25o"),
            }),
            Node(name="Glb", parent=".", unique_id=735050992, instance=ExtResourceRef("1_w5rjj")),
            Node(name="GlbEditable", parent=".", unique_id=1248585079, instance=ExtResourceRef("1_w5rjj")),
            Node(name="GlbEditableNewChild", type="Node", parent="GlbEditable", unique_id=1176021808),
            Node(name="GlbEditableAddScript", parent=".", unique_id=621548348, instance=ExtResourceRef("1_w5rjj")),
            Node(name="Cube", parent="GlbEditableAddScript", index="0", unique_id=895413058, node_paths=PackedStringArray("noderef"), properties = {
                "script" : ExtResourceRef("3_7d4mc"),
                "noderef" : NodePath(".."),
            }),
            Node(name="GlbEditableEditProp", parent=".", unique_id=726661338, instance=ExtResourceRef("1_w5rjj")),
            Node(name="Cube", parent="GlbEditableEditProp", index="0", unique_id=895413058, properties = {
                "transform" : Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 3, 0, 0),
            }),
        ],
        edit_flags = [
            EditFlag(path="GlbInhheritedEditable"),
            EditFlag(path="GlbEditable"),
            EditFlag(path="GlbEditableAddScript"),
            EditFlag(path="GlbEditableEditProp"),
        ],
    )

    file_d = FileLocal(
        path = "res://assets/complex.tscn",
        data = data_d
    )

    prj = Project.construct(
        files = (file_a, file_b, file_c, file_d),
        resources = (data_a, data_b, data_c, data_d),
    )

    return prj