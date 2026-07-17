from .....core.structure import Project, Resource, Node
from .....files import FileBinary, FileConfig
from .....resources import ResourceBinary, Config, Section
from .....core.values import *

def make()->tuple[FileBinary, ResourceBinary, bin]:
    ''' For images and other binaries; files must be converted with the settings file for in memory rep.
    That is beyond the scope of this project for the time being, thus all binary file reps are as below: 
    '''

    src = ...

    res = ResourceBinary.construct(
        file = "res://assets/icon.svg",
        uid = "uid://n7opm812ptfd",
    )
    
    file = FileBinary.construct(
        path = "res://assets/icon.svg",
        uid = "uid://n7opm812ptfd",
    )

    return file, res, src

def make_import()->tuple[FileConfig, Config, str]:
    src = '''
[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://n7opm812ptfd"
path="res://.godot/imported/icon.svg-56083ea2a1f1a4f1e49773bdc6d7826c.ctex"
metadata={
"vram_texture": false
}

[deps]

source_file="res://assets/icon.svg"
dest_files=["res://.godot/imported/icon.svg-56083ea2a1f1a4f1e49773bdc6d7826c.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
svg/scale=1.0
editor/scale_with_editor_scale=false
editor/convert_colors_with_editor_theme=false
'''
    res = Config.construct(
        file = "res://assets/icon.svg.import",
        subresources = [
            Section.construct("remap",
                properties = {
                    "importer":"texture",
                    "type":"CompressedTexture2D",
                    "uid":"uid://n7opm812ptfd",
                    "path":"res://.godot/imported/icon.svg-56083ea2a1f1a4f1e49773bdc6d7826c.ctex",
                    "metadata":{
                        "vram_texture": False,
                    },
                },
            ),
            Section.construct("deps",
                properties = {
                    "source_file":"res://assets/icon.svg",
                    "dest_files":Array("res://.godot/imported/icon.svg-56083ea2a1f1a4f1e49773bdc6d7826c.ctex"),
                },
            ),
            Section.construct("params",
                properties = {
                    "compress/mode": 0,
                    "compress/high_quality": False,
                    "compress/lossy_quality": 0.7,
                    "compress/uastc_level": 0,
                    "compress/rdo_quality_loss": 0.0,
                    "compress/hdr_compression": 1,
                    "compress/normal_map": 0,
                    "compress/channel_pack": 0,
                    "mipmaps/generate": False,
                    "mipmaps/limit":-1,
                    "roughness/mode": 0,
                    "roughness/src_normal": "",
                    "process/channel_remap/red": 0,
                    "process/channel_remap/green": 1,
                    "process/channel_remap/blue": 2,
                    "process/channel_remap/alpha": 3,
                    "process/fix_alpha_border": True,
                    "process/premult_alpha": False,
                    "process/normal_map_invert_y": False,
                    "process/hdr_as_srgb": False,
                    "process/hdr_clamp_exposure": False,
                    "process/size_limit": 0,
                    "detect_3d/compress_to": 1,
                    "svg/scale": 1.0,
                    "editor/scale_with_editor_scale": False,
                    "editor/convert_colors_with_editor_theme": False,
                }
            )
        ]
    )
    file = FileConfig.construct(
        path = "res://assets/icon.svg.import",
    )
    return file, res, src
