from .....core.structure import Resource, Node
from .....core.promises import SubResource, ExtResource
from .....files import FileTscn
from .....core.values import *

def make()->tuple[FileTscn, Resource, str]:
    src = '''
[gd_scene format=3 uid="uid://bvshg3b45tq5b"]

[ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_8vle4"]

[node name="blender" unique_id=1301180837 instance=ExtResource("1_8vle4")]

[node name="InheritedSceneChild" type="Node" parent="." index="0" unique_id=140602464]
'''
    res = Node.construct(
        uid = "uid://bvshg3b45tq5b",
        file = "res://assets/blender.glb.tscn",
        name = "blender",
        unique_id=1301180837,
        instance=ExtResource("1_8vle4"),
        _ext_resources = {
            "1_8vle4":{"uid":"uid://cocfi2vsn5qt2", "path":"res://assets/blender.glb"}
        },
        nodes = [
            Node.construct(
                name="InheritedSceneChild",
                type="Node",
                parent=".",
                index="0",
                unique_id=14060246,
            ),
        ],
    )
    file = FileTscn.construct(
        uid = "uid://bvshg3b45tq5b",
        file = "res://assets/blender.glb.tscn",
    )
    return file,res,src