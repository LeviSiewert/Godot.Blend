from .....core.structure import Resource
from .....core.promises import SubResource, ExtResource
from .....files import FileTres
from .....core.values import *

def make()->tuple[FileTres, Resource, str]:
    src = '''
[gd_resource type="World3D" format=3 uid="uid://b52f332102m2l"]

[sub_resource type="CameraAttributesPractical" id="CameraAttributesPractical_fssom"]

[sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_6okqy"]

[sub_resource type="Sky" id="Sky_b8yvd"]
sky_material = SubResource("ProceduralSkyMaterial_6okqy")

[sub_resource type="Environment" id="Environment_gatl5"]
background_mode = 2
sky = SubResource("Sky_b8yvd")
ambient_light_source = 3

[sub_resource type="Environment" id="Environment_c5o2k"]

[resource]
environment = SubResource("Environment_gatl5")
fallback_environment = SubResource("Environment_c5o2k")
camera_attributes = SubResource("CameraAttributesPractical_fssom")
'''
    res = Resource.construct(
        uid="uid://b52f332102m2l",
        file="res://assets/test_a.tres",
        type = "World3D",
        properties={
            "environment" : SubResource("Environment_gatl5"),
            "fallback_environment" : SubResource("Environment_c5o2k"),
            "camera_attributes" : SubResource("CameraAttributesPractical_fssom"),
        },
        subresources=[
            Resource.construct(
                id="CameraAttributesPractical_fssom",
                type="CameraAttributesPractical",
            ),
            Resource.construct(
                id="ProceduralSkyMaterial_6okqy",
                type="ProceduralSkyMaterial",
            ),
            Resource.construct(
                id="Sky_b8yvd",
                type="Sky",
                properties={
                    "sky_material" : SubResource("ProceduralSkyMaterial_6okqy"),
                },
            ),
            Resource.construct(
                id = "Environment_gatl5",
                type = "Environment",
                properties={
                    "background_mode" : 2,
                    "sky" : SubResource("Sky_b8yvd"),
                    "ambient_light_source" : 3,
                },
            ),
            Resource.construct(
                id="Environment_c5o2k",
                type="Environment",
            ),
        ]
    )
    file = FileTres.construct(
        uid="uid://b52f332102m2l",
        file="res://assets/test_a.tres"
    )
    return file, res, src