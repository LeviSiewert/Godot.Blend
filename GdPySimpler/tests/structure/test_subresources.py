from ...core.structure import ExtResource, ExtResourceRef
from ...core.subresources import *
from ...core.values import StringName, Array

class Test_Subresources():
    
    def test_basic_construction(self,):
        res = ResourceTres.construct(
            type = "World3D",
            format = 3,
            uid = "uid://b52f332102m2l",
            sub_resources = [
                SubResource.construct(
                    type="CameraAttributesPractical",
                    id="CameraAttributesPractical_fssom",
                ),
                SubResource.construct(
                    type="ProceduralSkyMaterial",
                    id="ProceduralSkyMaterial_6okqy",
                ),
                SubResource.construct(
                    type="Sky",
                    id="Sky_b8yvd",
                    properties={
                        "sky_material" : SubResourceRef("ProceduralSkyMaterial_6okqy"),
                    },
                ),
                SubResource.construct(
                    type="Environment",
                    id="Environment_gatl5",
                    properties={
                        "background_mode" : 2,
                        "sky" : SubResourceRef("Sky_b8yvd"),
                        "ambient_light_source" : 3,
                    },
                ),
                SubResource.construct(
                    type="Environment",
                    id="Environment_c5o2k",
                ),
            ],
            properties = {
                "environment" : SubResourceRef("Environment_gatl5"),
                "fallback_environment" : SubResourceRef("Environment_c5o2k"),
                "camera_attributes" : SubResourceRef("CameraAttributesPractical_fssom"),
            },
        )

        subres_a = res.sub_resources["CameraAttributesPractical_fssom"]
        assert subres_a.context.resource is res

    def test_extres_construction(self,):
        res = ResourceTres.construct(
            type = "Resource",
            script_class = "ClassDataDB",
            format = 3,
            uid = "uid://bgjki6uwnqh4q",
            sub_resources = {
                SubResource.construct(
                    type = "Resource",
                    id = "Resource_30man",
                    properties = {
                        "script" : ExtResourceRef("1_dek6i"),
                        "name" : StringName("AbstractPolygon2DEditor"),
                        "c_extends" : StringName("HBoxContainer"),
                    }
                )
            },
            ext_resources = {
                ExtResource(type="Script", uid="uid://dm8s8hmdwmdmn", path="res://tools/godot/class_exporter/class_data.gd", id="1_dek6i"),
                ExtResource(type="Script", uid="uid://fhlcms4fuqsy", path="res://tools/godot/class_exporter/property_data.gd", id="2_tjbr4"),
                ExtResource(type="Script", uid="uid://7xijk5okvw5n", path="res://tools/godot/class_exporter/signal_data.gd", id="3_ivqqm"),
                ExtResource(type="Script", uid="uid://bxnpcowvvtuqw", path="res://tools/godot/class_exporter/class_db.gd", id="4_rwa21"),

            },
            properties = {
                "script" : ExtResourceRef("4_rwa21"),
                "classes" : Array(SubResourceRef("Resource_30man"), types=ExtResourceRef("1_dek6i")),
            }
        )

        ext_res_a = res.ext_resources["uid://dm8s8hmdwmdmn"]
        assert ext_res_a.context.resources is res
        