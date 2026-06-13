
from pathlib import Path as _Path

from ..structure.core import PropertyCollection, Context
from ..structure.resources import GdResourceFileImport, GdSubresourseCategory, GdResourceFileScene, GdSubResourceNode
from ..structure.files import FileGodotProject, FileTscn, FileTres
from ..structure.values import *

_projdir = _Path(__file__).parent.resolve() / "project"

def get_exp_project_resource()->GdResourceFileImport:
    res = GdResourceFileImport()
    res.header_props.extend(
        {"configuration_version" : 5}.items()
        )
    res.categories.extend([
        GdSubresourseCategory("application",
            PropertyCollection({
                "config/name":"New Game Project",
                "config/features":GdValuePackedStringArray(("4.7", "Forward Plus")),
                "config/icon":"res://icon.svg",
            }.items())),
        GdSubresourseCategory("display",
            PropertyCollection({
                "window/stretch/mode":"canvas_items",
                "window/stretch/aspect":"expand",
            }.items())),
        GdSubresourseCategory("physics",
            PropertyCollection({
                "3d/physics_engine":"Jolt Physics",
            }.items())),
        GdSubresourseCategory("rendering",
            PropertyCollection({
                "rendering_device/driver.windows":"d3d12",
            }.items())),
    ])
    return res

def test_project_resource():
    c = Context()
    exp = get_exp_project_resource()
    file = FileGodotProject(_projdir/"project.godot")
    file.load(c)
    res : GdResourceFileImport = file.data
    res.categories["application"] == exp.categories["application"]
    res.categories["display"] == exp.categories["display"]
    res.categories["physics"] == exp.categories["physics"]
    res.categories["rendering"] == exp.categories["rendering"]
    # assert(file.data == expected) 

    application : GdSubresourseCategory = res.categories["application"]
    assert(application.properties["config/name"] == "New Game Project")
    assert(application.properties["config/features"] == GdValuePackedStringArray(("4.7", "Forward Plus")))
    
    rendering : GdSubresourseCategory = res.categories["rendering"]
    assert(rendering.properties["rendering_device/driver.windows"] == "d3d12")


def get_exp_tscn()->GdResourceFileScene:
    res = GdResourceFileScene()
    
    GdSubResourceNode
    return res
def test_tscn():
    c = Context()
    exp = get_exp_tscn()
    file = FileTscn(_projdir/"assets"/"tscn.tscn")
    file.load(c)

    