from .....core.structure import Resource, Node
from .....core.promises import SubResource, ExtResource
from .....files import FileTscn
from .....core.values import *

def make()->tuple[FileTscn, Resource, str]:
    src = '''
[gd_scene format=3 uid="uid://c0irlon13iq4o"]

[ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="1_8dc4x"]

[sub_resource type="Resource" id="Resource_1gj03"]
resource_local_to_scene = true

[sub_resource type="Resource" id="Resource_8dc4x"]
resource_local_to_scene = true

[node name="A" type="Node" unique_id=653408050 node_paths=PackedStringArray("noderef")]
script = ExtResource("1_8dc4x")
resource = SubResource("Resource_1gj03")
noderef = NodePath("B/D")

[node name="B" type="Node" parent="." unique_id=1524297946]

[node name="D" type="Node" parent="B" unique_id=1174449336 node_paths=PackedStringArray("noderef")]
script = ExtResource("1_8dc4x")
resource = SubResource("Resource_8dc4x")
noderef = NodePath("../../C/E")

[node name="C" type="Node" parent="." unique_id=452580425]
unique_name_in_owner = true

[node name="E" type="Node" parent="C" unique_id=1972079933]
''' 
    res = Node.construct(
        uid = "uid://c0irlon13iq4o",
        file = "res://assets/tscn.tscn",
        name="A",
        type="Node",
        id=653408050,
        properties={
            "script" : ExtResource("1_8dc4x"),
            "resource" : SubResource("Resource_1gj03"),
            "noderef" : NodePath("B/D"),
        },
        nodes=[
            Node.construct(
                name="B",
                type="Node",
                id=1524297946,
                parent=".",
                properties={
                }),
            Node.construct(
                name="D",
                type="Node",
                id=1174449336,
                parent="B",
                properties={
                    "script" : ExtResource("1_8dc4x"),
                    "resource" : SubResource("Resource_8dc4x"),
                    "noderef" : NodePath("../../C/E"),
                }),
            Node.construct(
                name="C",
                type="Node",
                id=452580425,
                parent=".",
                properties={
                    "unique_name_in_owner" : True,
                }),
            Node.construct(
                name="E",
                type="Node",
                id=1972079933,
                parent="C",
                properties={
                }),
        ],
        subresources=[
            Resource.construct(
                type="Resource", 
                id="Resource_1gj03",
                properties={
                    "resource_local_to_scene":True
                },
            ),
            Resource.construct(
                type="Resource", 
                id="Resource_8dc4x",
                properties={
                    "resource_local_to_scene":True
                },
            ),
        ],
        _ext_resources = {
            "1_8dc4x":{
                "uid":"uid://cr1tpol7u62kd", 
                "path":"res://assets/script.gd"
            }
        },
    )
    file = FileTscn.construct(
        path = "res://assets/tscn.tscn", 
        uid="uid://c0irlon13iq4o",
    )
    return file, res, src