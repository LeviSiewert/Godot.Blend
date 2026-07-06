from ._utils import _StructureTest
from ....core.subresources import ResourceTres, SubResource, SubResourceRef
from ....core.structure import ExtResource, ExtResourceRef
from ....core.values import NodePath, PackedStringArray, Color, Array, PackedByteArray, Dictionary, AABB, PackedByteArray, Vector4, StringName

class Test_SubResources(_StructureTest):
    _type = SubResource
    _parser_key = "sub_resource"
    
    def data(self,):
        yield from self.data_simple()
        yield from self.data_complex()

    def data_simple(self,):
        txt = '''
        [sub_resource type="CameraAttributesPractical" id="CameraAttributesPractical_fssom"]
        '''
        res = SubResource.construct(
            type="CameraAttributesPractical",
            id="CameraAttributesPractical_fssom",
        )
        yield txt, res

        txt = '''
        [sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_6okqy"]
        
        '''
        res = SubResource.construct(
            type="ProceduralSkyMaterial",
            id="ProceduralSkyMaterial_6okqy",
        )
        yield txt, res

        txt = '''
        [sub_resource type="Sky" id="Sky_b8yvd"]
        sky_material = SubResource("ProceduralSkyMaterial_6okqy")
        '''
        res = SubResource.construct(
            type="Sky",
            id="Sky_b8yvd",
            properties={
                "sky_material" : SubResourceRef("ProceduralSkyMaterial_6okqy"),
            },
        )
        yield txt, res

        txt = '''
        [sub_resource type="Environment" id="Environment_gatl5"]
        background_mode = 2
        sky = SubResource("Sky_b8yvd")
        ambient_light_source = 3
        '''
        res = SubResource.construct(
            type="Environment",
            id="Environment_gatl5",
            properties={
                "background_mode" : 2,
                "sky" : SubResourceRef("Sky_b8yvd"),
                "ambient_light_source" : 3,
            },
        )
        yield txt, res

        txt = '''
        [sub_resource type="Environment" id="Environment_c5o2k"]
        '''
        res = SubResource.construct(
            type="Environment",
            id="Environment_c5o2k",
        )
        yield txt, res


    def data_complex(self,):
        
        txt = """ 
        [sub_resource type="StandardMaterial3D" id="StandardMaterial3D_6cmw1"]
        resource_name = "Material"
        cull_mode = 2
        albedo_color = Color(0.906332, 0.906332, 0.906332, 1)
        roughness = 0.5
        """

        ## TODO: Issue here w/ float percision in rendering (0.9063318 => 0.906332) 

        res = SubResource.construct(
            type="StandardMaterial3D", 
            id="StandardMaterial3D_6cmw1",
            properties = {
                "resource_name" : "Material",
                "cull_mode" : 2,
                "albedo_color" : Color(0.906332, 0.906332, 0.906332, 1),
                "roughness" : 0.5,
            },
        )
        yield txt,res
        txt = """ 
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
        """
        res = SubResource.construct(
            type="ArrayMesh", 
            id="ArrayMesh_3l6rm",
            properties = {
                "_surfaces" : Array(Dictionary({
                    "aabb": AABB(-1, -1, -1, 2, 2, 2),
                    "format": 34896613377,
                    "index_count": 36,
                    "index_data": PackedByteArray("AAABAAIAAwACAAEAAAAEAAEAAwAFAAIABQAAAAIABgAEAAAABQAGAAAABwABAAQABwADAAEABgAHAAQABQADAAcABQAHAAYA"),
                    "name": "Material",
                    "primitive": 3,
                    "uv_scale": Vector4(0, 0, 0, 0),
                    "vertex_count": 8,
                    "vertex_data": PackedByteArray("/////wAAAAAAAP////8AAAAA//8AAAAAAAAAAP//AAD///////8AAAAAAAAAAAAA//8AAAAAAAD//wAA//8AAA==")
                    })),
                "blend_shape_mode" : 0,
            },
        )
        yield txt,res
        txt = """
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
        """
        res = SubResource.construct(
            type="ArrayMesh",
            id="ArrayMesh_qt25o",
            properties = {
                "resource_name" : "blender_Cube",
                "_surfaces" : Array(Dictionary({
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
                    })),
                "blend_shape_mode" : 0,
                "shadow_mesh" : SubResource("ArrayMesh_3l6rm"),
            },
        )
        yield txt,res


class Test_Resources(_StructureTest):
    _type = ResourceTres
    _parser_key = "file_resource"

    def data(self,):
        yield from self.data_simple()
        yield from self.data_complex()

            
    def data_simple(self,):
        txt = """ [gd_resource type="World3D" format=3 uid="uid://b52f332102m2l"] """
        res = ResourceTres(type="World3D", format=3, uid="uid://b52f332102m2l")
        yield txt, res
        
        txt = """ [gd_resource type="World3D" format=3 uid="uid://b52f332102m2l"]
        [resource]
        environment = SubResource("Environment_gatl5")
        fallback_environment = SubResource("Environment_c5o2k")
        camera_attributes = SubResource("CameraAttributesPractical_fssom")
        """
        res = ResourceTres.construct(
            type="World3D", 
            format=3, 
            uid="uid://b52f332102m2l",
            properties={
                "environment" : SubResourceRef("Environment_gatl5"),
                "fallback_environment" : SubResourceRef("Environment_c5o2k"),
                "camera_attributes" : SubResourceRef("CameraAttributesPractical_fssom"),
            },
        )
        yield txt, res

    def data_complex(self,):
        txt = """ [gd_resource type="World3D" format=3 uid="uid://b52f332102m2l"]

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
        """

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

        yield txt, res

        txt = """[gd_resource type="Resource" script_class="ClassDataDB" format=3 uid="uid://bgjki6uwnqh4q"]

        [ext_resource type="Script" uid="uid://dm8s8hmdwmdmn" path="res://tools/godot/class_exporter/class_data.gd" id="1_dek6i"]
        [ext_resource type="Script" uid="uid://fhlcms4fuqsy" path="res://tools/godot/class_exporter/property_data.gd" id="2_tjbr4"]
        [ext_resource type="Script" uid="uid://7xijk5okvw5n" path="res://tools/godot/class_exporter/signal_data.gd" id="3_ivqqm"]
        [ext_resource type="Script" uid="uid://bxnpcowvvtuqw" path="res://tools/godot/class_exporter/class_db.gd" id="4_rwa21"]

        [sub_resource type="Resource" id="Resource_30man"]
        script = ExtResource("1_dek6i")
        name = &"AbstractPolygon2DEditor"
        c_extends = &"HBoxContainer"

        [resource]
        script = ExtResource("4_rwa21")
        classes = Array[ExtResource("1_dek6i")]([SubResource("Resource_30man")])
        """        

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