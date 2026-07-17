from ....core.structure import Project, Resource, Node
from ....files import FileText, FileTscn, FileConfig
from ....resources import Config, Section
from ....core.values import *

def make()->tuple[FileConfig,Resource,str]:
    src = '''; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="New Game Project"
config/features=PackedStringArray("4.7", "Forward Plus")
config/icon="res://icon.svg"

[display]

window/stretch/mode="canvas_items"
window/stretch/aspect="expand"

[physics]

3d/physics_engine="Jolt Physics"

[rendering]

rendering_device/driver.windows="d3d12"
'''

    res = Config.construct(
        file = "res://project.godot",
        properties = {
            "config_version":5,
        },
        subresources = [
            Section.construct("application",
                properties={
                    "config/name":"New Game Project",
                    "config/features":PackedStringArray("4.7", "Forward Plus"),
                    "config/icon":"res://icon.svg",
                },
            ),
            Section.construct("display",
                properties={
                    "window/stretch/mode":"canvas_items",
                    "window/stretch/aspect":"expand",
                },
            ),
            Section.construct("physics",
                properties={
                    "3d/physics_engine":"Jolt Physics",
                },
            ),
            Section.construct("rendering",
                properties={
                    "rendering_device/driver.windows":"d3d12"
                },
            ),
        ],
    ) 

    file = FileConfig.construct(
        filepath = "",
    )