from ..structure.values import *
from ..structure.sub_resources import *
from ..structure.generic import GdObject

from ..structure.references import GdValueNodePath, GdValueExtResource
from ..structure.core.primitives import Context
from ..structure._standard_parser import construct_keyed_parser
gdparser = construct_keyed_parser("sub_resource")

c = Context()
def _parse(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)
def _render(object):
    return gdparser.render(c,object)

# def test_err():
#     raise NotImplementedError("TODO: Test parsing & rendering")


from typing import Generator

## NOTE: test cases from godot's official tps-demo level.tscn !!

class TestSubResourceExt():
    def data(self,)->Generator[tuple[str,SubResourceExt]]:
        txt = '[ext_resource type="Script" uid="uid://ccxbls23ev7u3" path="res://level/level.gd" id="1"]'
        res = SubResourceExt()
        res.type = "Script"
        res.uid = "uid://ccxbls23ev7u3"
        res.path = "res://level/level.gd"
        res.id = "1"
        yield (txt, res)

        txt = '[ext_resource type="PackedScene" uid="uid://bpihm2o3g658" path="res://level/geometry/scenes/props.tscn" id="2"]'
        res = SubResourceExt()
        res.type = "PackedScene"
        res.uid = "uid://bpihm2o3g658"
        res.path = "res://level/geometry/scenes/props.tscn"
        res.id = "2"
        yield (txt, res)

        txt = '[ext_resource type="VoxelGIData" uid="uid://bw86lhn5p1ovp" path="res://level/geometry/giprobe_data.res" id="5"]'
        res = SubResourceExt()
        res.type="VoxelGIData" 
        res.uid="uid://bw86lhn5p1ovp" 
        res.path="res://level/geometry/giprobe_data.res" 
        res.id="5"
        yield (txt,res)

        txt = '[ext_resource type="AudioStream" uid="uid://vxxm8xm1fr6y" path="res://level/level_music.ogg" id="8"]'
        res = SubResourceExt()
        res.type="AudioStream" 
        res.uid="uid://vxxm8xm1fr6y" 
        res.path="res://level/level_music.ogg" 
        res.id="8"
        yield (txt,res)

        txt = '[ext_resource type="Script" uid="uid://6ec6m14rhsxi" path="res://level/debug.gd" id="9"]'
        res = SubResourceExt() 
        res.type="Script" 
        res.uid="uid://6ec6m14rhsxi" 
        res.path="res://level/debug.gd" 
        res.id="9"
        yield (txt,res)

        txt = '[ext_resource type="CompressedTexture3D" uid="uid://b2x2pkclq230n" path="res://level/level.GPUParticlesCollisionSDF3D_data.exr" id="11_mt3nw"]'
        res = SubResourceExt() 
        res.type="CompressedTexture3D" 
        res.uid="uid://b2x2pkclq230n" 
        res.path="res://level/level.GPUParticlesCollisionSDF3D_data.exr" 
        res.id="11_mt3nw"
        yield (txt, res)

        txt = '[ext_resource type="PackedScene" uid="uid://dln4kthc3tvfv" path="res://level/forklift/flying_forklift.tscn" id="12"]'
        res = SubResourceExt()
        res.type="PackedScene" 
        res.uid="uid://dln4kthc3tvfv" 
        res.path="res://level/forklift/flying_forklift.tscn" 
        res.id="12"
        yield (txt,res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val = _parse("ext_resource",txt)
            assert(isinstance(val, SubResourceExt))
            assert(res.type == val.type)
            assert(res.uid == val.uid)
            assert(res.path == val.path)
            assert(res.id == val.id)
            assert(res == val)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))
        
class TestSubResourceEdit():

    def data(self,)->Generator[tuple[str,SubResourceEdit]]:
        txt = '[editable path="FlyingForkliftModel2"]'
        res = SubResourceEdit()
        res.path = "FlyingForkliftModel2"
        yield (txt, res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val = _parse("edit_resource",txt)
            assert(res.path == val.path)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))

class TestSubResource():
    '''Clarification: generic subresource'''

    def data(self,)->Generator[tuple[str,SubResource]]:
        txt = ''' 
[sub_resource type="BoxShape3D" id="1"]
size = Vector3(8.85286, 6.2089, 11.0664)'''
        res = SubResource()
        res.type = "BoxShape3D"
        res.id = "1"
        res.properties["size"] = GdValueVector3([8.85286, 6.2089, 11.0664]) 
        yield (txt, res) 

        txt = '''[sub_resource type="Animation" id="2"]
resource_name = "mawaru"
length = 30.0
loop_mode = 1
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath(".:rotation_degrees")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {
"times": PackedFloat32Array(0, 30),
"transitions": PackedFloat32Array(1, 1),
"update": 0,
"values": [Vector3(0, 0, 0), Vector3(0, -360, 0)]
}
'''
        res = SubResource()
        res.type="Animation"
        res.id="2"

        res.properties["resource_name"] = "mawaru"
        res.properties["length"] = 30.0
        res.properties["loop_mode"] = 1
        res.properties["tracks/0/type"] = "value"
        res.properties["tracks/0/imported"] = False
        res.properties["tracks/0/enabled"] = True
        res.properties["tracks/0/path"] = GdValueNodePath(".:rotation_degrees")
        res.properties["tracks/0/interp"] = 1
        res.properties["tracks/0/loop_wrap"] = True
        res.properties["tracks/0/keys"] = GdValueDictionary({
            "times": GdValuePackedFloat32Array([0, 30]),
            "transitions": GdValuePackedFloat32Array([1, 1]),
            "update": 0,
            "values": [GdValueVector3([0, 0, 0]), GdValueVector3([0, -360, 0])]
        }.items())

        yield (txt, res) 

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val = _parse("sub_resource",txt)
            assert(isinstance(val,SubResource))
            assert(res.type == val.type)
            assert(res.id == val.id)
            assert(res.properties == val.properties)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))

class TestSubResourceNode():

    def data(self,)->Generator[tuple[str,SubResourceNode]]:
        txt = '''[node name="Level" type="Node3D"]
script = ExtResource("1")
'''     
        res = SubResourceNode()
        res.name = "Level"
        res.type = "Node3D"
        res.is_root = True
        res.properties["script"] = GdValueExtResource("1")
        yield(txt, res)

        txt = '''[node name="SpawnedNodes" type="Node3D" parent="."]'''
        res = SubResourceNode()
        res.name = "SpawnedNodes"
        res.type = "Node3D"
        res.parent = "."
        yield (txt, res)

        txt = '''[node name="RobotSpawnpoints" type="Node3D" parent="."] '''
        res = SubResourceNode()
        res.name="RobotSpawnpoints" 
        res.type="Node3D" 
        res.parent="."
        yield (txt, res)

        txt = '''[node name="Marker3D1" type="Marker3D" parent="RobotSpawnpoints"]
transform = Transform3D(0.843905, 0, -0.536493, 0, 1, 0, 0.536493, 0, 0.843905, 71.5907, -6.05686, 46.2736)
'''
        res = SubResourceNode()
        res.name="Marker3D1"
        res.type="Marker3D"
        res.parent="RobotSpawnpoints"
        res.properties["transform"] = GdValueTransform3D([0.843905, 0, -0.536493, 0, 1, 0, 0.536493, 0, 0.843905, 71.5907, -6.05686, 46.2736])
        yield (txt, res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val = _parse("node_resource",txt)
            assert(isinstance(val,SubResourceNode))
            assert(val.name == res.name)
            assert(val.type == res.type)
            assert(val.parent == res.parent)
            # assert(val.is_root == res.is_root)
            assert(res.properties == val.properties)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))


class TestSubResourceCategory():
    def data(self,)->Generator[tuple[str,SubResourceNode]]:
        txt = '''[animation]

compatibility/default_parent_skeleton_in_mesh_instance_3d=true
'''

        txt = '''[application]

config/name="Godot Third-Person Shooter Demo"
config/description="Godot Third Person Shooter with high quality assets and lighting"
run/main_scene="res://main/main.tscn"
config/features=PackedStringArray("4.7")
config/icon="res://icon.png"
'''
        res = SubResourceCategory()
        res.name = "application"
        res.properties["config/name"] = "Godot Third-Person Shooter Demo"
        res.properties["config/description"] = "Godot Third Person Shooter with high quality assets and lighting"
        res.properties["run/main_scene"] = "res://main/main.tscn"
        res.properties["config/features"] = GdValuePackedStringArray("4.7")
        res.properties["config/icon"] = "res://icon.png"
        yield (txt, res)

        txt = '''[autoload]

Settings="*res://menu/settings.gd"
'''
        res = SubResourceCategory()
        res.name = "autoload"
        res.properties["Settings"] = "*res://menu/settings.gd"
        yield (txt, res)

        txt = '''[display]

window/size/viewport_width=1920
window/size/viewport_height=1080
window/stretch/mode="canvas_items"
window/stretch/aspect="expand"
window/size/fullscreen=true
''' 
        res = SubResourceCategory()
        res.name = "display"
        res.properties["window/size/viewport_width"]=1920
        res.properties["window/size/viewport_height"]=1080
        res.properties["window/stretch/mode"]="canvas_items"
        res.properties["window/stretch/aspect"]="expand"
        res.properties["window/size/fullscreen"]=True
        yield (txt, res)

        txt = '''[editor]

import/use_multiple_threads=false
'''
        res = SubResourceCategory()
        res.name = "editor"
        res.properties["import/use_multiple_threads"] = False
        yield (txt, res)

        txt = '''[filesystem]

import/blender/enabled=false
'''
        res = SubResourceCategory()
        res.name = "filesystem"
        res.properties["import/blender/enabled"] = False
        yield (txt, res)

        txt = '''[input]

ui_accept={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194309,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194310,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"location":0,"echo":false,"script":null)
, Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":false,"script":null)
]
}
'''
        res = SubResourceCategory()
        res.name = "input"
        res.properties["ui_accept"] = GdValueDictionary({
            "deadzone": 0.5,
            "events" : GdValueArray([
                GdObject('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":4194309,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":False,"script":None}),
                GdObject('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":4194310,"physical_keycode":0,"key_label":0,"unicode":0,"location":0,"echo":False,"script":None}),
                GdObject('InputEventKey',**{"resource_local_to_scene":False,"resource_name":"","device":0,"window_id":0,"alt_pressed":False,"shift_pressed":False,"ctrl_pressed":False,"meta_pressed":False,"pressed":False,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"location":0,"echo":False,"script":None}),
                GdObject('InputEventJoypadButton',**{"resource_local_to_scene":False,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":False,"script":None})
            ])
        }.items())
        yield (txt, res)

    def test_gd_to_py(self,):
        for txt, res in self.data():
            val = _parse("cat_resource",txt)
            assert(isinstance(val,SubResourceCategory))
            assert(val.name == res.name)
            assert(res.properties == val.properties)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))


class TestResourceContainer():
    '''Clarification: all properties not sorted under a SubResource-like '''
    def data(self,)->Generator[tuple[str,ResourceContainer]]:
        #From a project.godot
        txt = '''[resource]
bus/0/volume_db = -10.0
bus/1/name = &"Outside"
bus/1/solo = false
bus/1/mute = false
'''
        res = ResourceContainer()
        # res.properties["config_version"] = 5
        
        res.properties['bus/0/volume_db'] = -10.0
        res.properties['bus/1/name'] = GdValueStringName("Outside")
        res.properties['bus/1/solo'] = False
        res.properties['bus/1/mute'] = False
        yield (txt, res)
        
    def test_gd_to_py(self,):
        for txt, res in self.data():
            val = _parse("prim_resource",txt)
            assert(isinstance(val, ResourceContainer))
            assert(res.properties == val.properties)

    def test_py_to_gd(self,):
        for txt, res in self.data():
            val = _render(res)
            assert(txt.replace(" ","").strip("\n") == val.replace(" ","").strip("\n"))
# class TestGdValueResourceID():
#     def test_in_matcher(self,):
#         assert(gdparser._parser_transformer.matcher(None, "rid"))
#     def test_parsing(self,):
#         assert(isinstance(_parse("value", "RID()"), GdValueResourceID)) 
#         assert(_parse("value", "RID()") == GdValueResourceID())
#         assert(_parse("value", 'RID("")') == GdValueResourceID())
#         assert(_parse("value", 'RID("ID")') == GdValueResourceID("ID"))
#     def test_rendering(self,):
#         assert("RID()" == _render(GdValueResourceID()))
#         assert('RID("ID")' == _render(GdValueResourceID("ID")))
