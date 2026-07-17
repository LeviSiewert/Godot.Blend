from .....core.structure import Project, Resource, Node
from .....files import FileBinary, FileConfig
from .....resources import ResourceBinary, Config, Section
from .....core.values import *

def make()->tuple[FileBinary, ResourceBinary, bin]:
    '''FUTURE: importing tscn as GLB! for now I'm treating it as a binary. ''' 
    ''' For images and other binaries; files must be converted with the settings file for in memory rep.
    That is beyond the scope of this project for the time being, thus all binary file reps are as below: 
    '''

    src = ...

    res = ResourceBinary.construct(
        file = "res://assets/blender.glb",
        uid = "uid://cocfi2vsn5qt2",
    )
    
    file = FileBinary.construct(
        path = "res://assets/blender.glb",
        uid = "uid://cocfi2vsn5qt2",
    )

    return file, res, src

def make_import()->tuple[FileConfig,Config,str]:
    src = '''
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
    res = Config.construct(
        path="res://assets/blender.glb.import",
        subresources = [
            Section.construct("remap",
                properties={
                    "importer":"scene",
                    "importer_version":1,
                    "type":"PackedScene",
                    "uid":"uid://cocfi2vsn5qt2",
                    "path":"res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn",
                },
            ),
            Section.construct("deps",
                properties = {
                    "source_file":"res://assets/blender.glb",
                    "dest_files":Array("res://.godot/imported/blender.glb-920034d6e5ec1c2d509d6589b3fcbbe0.scn"),
                },
            ),
            Section.construct("params",
                properties = {
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
                },
            ),
        ],
    )
    file = FileConfig.construct(
        path="res://assets/blender.glb.import",
    )
    return file,res,src