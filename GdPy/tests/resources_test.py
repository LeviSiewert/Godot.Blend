import pytest
from typing import Generator

from ..structure.resources import (
    ResourceTres,
    ResourceScene,
    ResourceImport,
)
from ..structure.values import GdValueSubResource, GdValuePackedStringArray
from ..structure.references import GdValueNodePath, GdValueSubResource, GdValueExtResource
from ..structure.sub_resources import SubResource, SubResourceCategory, SubResourceNode
from ..structure.property_collection import PropertyCollection

from ..structure.core.primitives import Context
from ..structure._standard_parser import construct_keyed_parser
gdparser = construct_keyed_parser("resource")

c = Context()
def _parse(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)
def _render(object):
    return gdparser.render(c,object)

@pytest.mark.dependency()
class TestResourceTres():
    def data(self,)->Generator[tuple[str,ResourceTres]]:
        txt = '''[gd_resource type="World3D" format=3 uid="uid://b52f332102m2l"]

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
        res = ResourceTres.new(type="World3D", format=3, uid="uid://b52f332102m2l")

        res.sub_resources.extend([
            SubResource.new(type="CameraAttributesPractical", id="CameraAttributesPractical_fssom"),
            SubResource.new(type="ProceduralSkyMaterial", id="ProceduralSkyMaterial_6okqy"),
            SubResource.new(type="Sky", id="Sky_b8yvd", properties=PropertyCollection(values = {
                "sky_material" : GdValueSubResource("ProceduralSkyMaterial_6okqy"),
            }.items())),
            SubResource.new(type="Environment", id="Environment_gatl5", properties=PropertyCollection(values = {
                "background_mode" : 2,
                "sky" : GdValueSubResource("Sky_b8yvd"),
                "ambient_light_source" : 3,
            }.items())),
            SubResource.new(type="Environment", id="Environment_c5o2k"),
        ])

        res.properties.extend({
            "environment" : GdValueSubResource("Environment_gatl5"),
            "fallback_environment" : GdValueSubResource("Environment_c5o2k"),
            "camera_attributes" : GdValueSubResource("CameraAttributesPractical_fssom"),
        }.items())

        yield (txt,res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val : ResourceTres = _parse("ext_resource",txt)
            assert (isinstance(val, ResourceTres))
            assert (res.type == val.type)
            assert (res.format == val.format)
            assert (res.uid == val.uid)
            assert (res.properties == val.properties)
            assert (res.ext_resources == val.ext_resources)
            assert (res.sub_resources == val.sub_resources)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))
    


@pytest.mark.dependency()
class TestResourceImport():
    def data(self,)->Generator[tuple[str,ResourceImport]]:
        txt = '''[remap]

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
nodes/root_script=null
mesh_library/use_node_names_as_mesh_names=false
array_mesh/deduplicate_surfaces=true
nodes/apply_root_scale=true
nodes/root_scale=1.0
nodes/import_as_skeleton_bones=false
nodes/use_name_suffixes=true
nodes/use_node_type_suffixes=true
meshes/ensure_tangents=true
meshes/generate_lods=true
meshes/create_shadow_meshes=true
meshes/light_baking=1
meshes/lightmap_texel_size=0.2
meshes/force_disable_compression=false
skins/use_named_skins=true
animation/import=true
animation/fps=30
animation/trimming=false
animation/remove_immutable_tracks=true
animation/import_rest_as_RESET=false
import_script/path=""
materials/extract=0
materials/extract_format=0
materials/extract_path=""
_subresources={}
gltf/naming_version=0
gltf/embedded_image_handling=1
gltf/texture_map_mode=1
'''
        res = ResourceImport.new()
        res.type = "PackedScene"  
        res.uid = "uid://cocfi2vsn5qt2"

        res.cat_resources.extend([
            SubResourceCategory.new(name = "remap", properties=PropertyCollection(values={
                "importer" : "scene",
                "importer_version" : 1,
                "type" : "PackedScene",
                "uid" : "uid://cocfi2vsn5qt2",
                "path" : "res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn",
            }.items())),
            SubResourceCategory.new(name = "deps", properties=PropertyCollection(values={
                "source_file" : "res://assets/blender.glb",
                "dest_files" : ["res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn"],
            }.items())),
            SubResourceCategory.new(name = "params", properties=PropertyCollection(values={
                "nodes/root_type":"",
                "nodes/root_name":"",
                "nodes/root_script":None,
                "mesh_library/use_node_names_as_mesh_names":False,
                "array_mesh/deduplicate_surfaces":True,
                "nodes/apply_root_scale":True,
                "nodes/root_scale":1.0,
                "nodes/import_as_skeleton_bones":False,
                "nodes/use_name_suffixes":True,
                "nodes/use_node_type_suffixes":True,
                "meshes/ensure_tangents":True,
                "meshes/generate_lods":True,
                "meshes/create_shadow_meshes":True,
                "meshes/light_baking":1,
                "meshes/lightmap_texel_size":0.2,
                "meshes/force_disable_compression":False,
                "skins/use_named_skins":True,
                "animation/import":True,
                "animation/fps":30,
                "animation/trimming":False,
                "animation/remove_immutable_tracks":True,
                "animation/import_rest_as_RESET":False,
                "import_script/path":"",
                "materials/extract":0,
                "materials/extract_format":0,
                "materials/extract_path":"",
                "_subresources":{},
                "gltf/naming_version":0,
                "gltf/embedded_image_handling":1,
                "gltf/texture_map_mode":1,
            }.items())),
        ])

        yield (txt,res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val : ResourceImport = _parse("ext_resource",txt)
            assert (isinstance(val, ResourceImport))
            assert (res.type == val.type)
            assert (res.uid == val.uid)
            assert (res.cat_resources == val.cat_resources)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))


class TestResourceScene():
    def data(self,)->Generator[tuple[str,ResourceScene]]:
        txt = '''[gd_scene format=3 uid="uid://c0irlon13iq4o"]

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
        res = ResourceScene.new(format=3, uid="uid://c0irlon13iq4o")
        res.sub_resources.extend([
            SubResource.new(type="Resource", id="Resource_1gj03", properties=PropertyCollection(values={
                "resource_local_to_scene" : True
            }.items())),
            SubResource.new(type="Resource", id="Resource_8dc4x", properties=PropertyCollection(values={
                "resource_local_to_scene" : True
            }.items())),
        ])

        res.node_resources.extend([
            SubResourceNode.new(name="A", type="Node", unique_id=653408050, node_paths=GdValuePackedStringArray("noderef"), properties=PropertyCollection(values={
                "script" : GdValueExtResource("1_8dc4x"),
                "resource" : GdValueSubResource("Resource_1gj03"),
                "noderef" : GdValueNodePath("B/D"),
            }.items())),
            SubResourceNode.new(name="B", type="Node", parent=".", unique_id=1524297946),
            SubResourceNode.new(name="D", type="Node", parent="B", unique_id=1174449336, node_paths=GdValuePackedStringArray("noderef"), properties=PropertyCollection(values={
                "script" : GdValueExtResource("1_8dc4x"),
                "resource" : GdValueSubResource("Resource_8dc4x"),
                "noderef" : GdValueNodePath("../../C/E"),
            }.items())),
            SubResourceNode.new(name="C", type="Node", parent=".", unique_id=452580425, properties=PropertyCollection(values={
                "unique_name_in_owner" : True,
            }.items())),
            SubResourceNode.new(name="E", type="Node", parent="C", unique_id=1972079933),
        ])

        nodes = res.node_resources
        A : SubResourceNode = nodes[653408050]
        B : SubResourceNode = nodes[1524297946]
        C : SubResourceNode = nodes[1174449336]
        D : SubResourceNode = nodes[452580425]
        E : SubResourceNode = nodes[1972079933]

        nodes.root = A
        A.add_child(B)
        B.add_child(D)
        A.add_child(C)
        C.add_child(E)
        
        A.properties["noderef"].value = D
        D.properties["noderef"].value = E

        yield (txt,res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val : ResourceScene = _parse("ext_resource",txt)
            assert (isinstance(val, ResourceScene))
            assert (res.type == val.type)
            assert (res.uid == val.uid)
            assert (res.properties == val.properties)
            assert (res.node_resources == val.node_resources)
            assert (res.edit_resources == val.edit_resources)
            assert (res.sub_resources == val.sub_resources)
            assert (res.ext_resources == val.ext_resources)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))
