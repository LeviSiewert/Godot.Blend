
from pathlib import Path as _Path

# from ..structure.resources import GdResourceFileImport, GdSubresourseCategory, GdResourceFileScene, GdSubResourceNode
# from ..structure.files import FileGodotProject, FileTscn, FileTres
# from ..structure.values import *

from ..structure.core import PropertyCollection, Context
from ..structure.resources import GdResourceFileImport, GdResourceFileScene, GdResourceFileTres
from ..structure.sub_resource_collections import CollectionExtRes, CollectionEditRes, CollectionNodeRes, CollectionNodeRes, CollectionCatRes
from ..structure.sub_resources import SubResource, SubResourceCategory, SubResourceEdit, SubResourceExt, SubResourceNode 
from ..structure.files import FileGodotProject


from ..structure.values import GdValuePackedStringArray

_projdir = _Path(__file__).parent.resolve() / "project"

def project_resource_expected()->GdResourceFileImport:
    res = GdResourceFileImport()
    res._configuration_version = 5

    res.cat_resources.extend([
        SubResourceCategory.new(_name = "application", properties = PropertyCollection({
            "config/name":"New Game Project",
            "config/features":GdValuePackedStringArray(("4.7", "Forward Plus")),
            "config/icon":"res://icon.svg",
        }.items())),
        SubResourceCategory.new(_name = "display", properties = PropertyCollection({
            "window/stretch/mode":"canvas_items",
            "window/stretch/aspect":"expand",
        }.items())),
        SubResourceCategory.new(_name = "physics", properties = PropertyCollection({
            "3d/physics_engine":"Jolt Physics",
        }.items())),
        SubResourceCategory.new(_name = "rendering", properties = PropertyCollection({
            "rendering_device/driver.windows":"d3d12",
        }.items())),
    ])

def test_project_resource():
    c = Context()
    exp = project_resource_expected()
    file = FileGodotProject(_projdir/"project.godot")
    file.load(c)

    res : GdResourceFileImport = file.data
    
    assert (res._configuration_version == exp._configuration_version)
    assert(res.categories["application"] == exp.categories["application"])
    assert(res.categories["display"] == exp.categories["display"])
    assert(res.categories["physics"] == exp.categories["physics"])
    assert(res.categories["rendering"] == exp.categories["rendering"])

# def get_exp_project_resource()->GdResourceFileImport:
#     res = GdResourceFileImport()
#     res.header_props.extend(
#         {"configuration_version" : 5}.items()
#         )
#     res.categories.extend([
#         GdSubresourseCategory("application",
#             PropertyCollection({
#                 "config/name":"New Game Project",
#                 "config/features":GdValuePackedStringArray(("4.7", "Forward Plus")),
#                 "config/icon":"res://icon.svg",
#             }.items())),
#         GdSubresourseCategory("display",
#             PropertyCollection({
#                 "window/stretch/mode":"canvas_items",
#                 "window/stretch/aspect":"expand",
#             }.items())),
#         GdSubresourseCategory("physics",
#             PropertyCollection({
#                 "3d/physics_engine":"Jolt Physics",
#             }.items())),
#         GdSubresourseCategory("rendering",
#             PropertyCollection({
#                 "rendering_device/driver.windows":"d3d12",
#             }.items())),
#     ])
#     return res

# def test_project_resource():
#     c = Context()
#     exp = get_exp_project_resource()
#     file = FileGodotProject(_projdir/"project.godot")
#     file.load(c)
#     res : GdResourceFileImport = file.data
#     res.categories["application"] == exp.categories["application"]
#     res.categories["display"] == exp.categories["display"]
#     res.categories["physics"] == exp.categories["physics"]
#     res.categories["rendering"] == exp.categories["rendering"]
#     # assert(file.data == expected) 

#     application : GdSubresourseCategory = res.categories["application"]
#     assert(application.properties["config/name"] == "New Game Project")
#     assert(application.properties["config/features"] == GdValuePackedStringArray(("4.7", "Forward Plus")))
    
#     rendering : GdSubresourseCategory = res.categories["rendering"]
#     assert(rendering.properties["rendering_device/driver.windows"] == "d3d12")


# def get_exp_tscn()->GdResourceFileScene:
#     res = GdResourceFileScene()
#     res.
#     GdSubResourceNode
#     return res
# def test_tscn():
#     c = Context()
#     exp = get_exp_tscn()
#     file = FileTscn(_projdir/"assets"/"tscn.tscn")
#     file.load(c)

    