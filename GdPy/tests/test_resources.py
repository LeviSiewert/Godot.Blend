
from pathlib import Path as _Path

# from ..structure.resources import GdResourceFileImport, GdSubresourseCategory, GdResourceFileScene, GdSubResourceNode
# from ..structure.files import FileGodotProject, FileTscn, FileTres
# from ..structure.values import *

from ..structure.core import PropertyCollection, Context
from ..structure.resources import GdResourceFileImport, GdResourceFileScene, GdResourceFileTres
from ..structure.sub_resource_collections import CollectionExtRes, CollectionEditRes, CollectionNodeRes, CollectionNodeRes, CollectionCatRes
from ..structure.sub_resources import SubResource, SubResourceCategory, SubResourceEdit, SubResourceExt, SubResourceNode 
from ..structure.files import FileGodotProject, FileTscn
from ..structure.references import GdValueExtResource, GdValueSubResource, GdValueNodePath

from ..structure.values import GdValuePackedStringArray

_projdir = _Path(__file__).parent.resolve() / "project"

def project_resource_expected()->GdResourceFileImport:
    res = GdResourceFileImport()
    res.configuration_version = 5

    res.cat_resources.extend([
        SubResourceCategory.new(name = "application", properties = PropertyCollection({
            "config/name":"New Game Project",
            "config/features":GdValuePackedStringArray(("4.7", "Forward Plus")),
            "config/icon":"res://icon.svg",
        }.items())),
        SubResourceCategory.new(name = "display", properties = PropertyCollection({
            "window/stretch/mode":"canvas_items",
            "window/stretch/aspect":"expand",
        }.items())),
        SubResourceCategory.new(name = "physics", properties = PropertyCollection({
            "3d/physics_engine":"Jolt Physics",
        }.items())),
        SubResourceCategory.new(name = "rendering", properties = PropertyCollection({
            "rendering_device/driver.windows":"d3d12",
        }.items())),
    ])
    return res

def test_project_resource():
    c = Context()
    exp = project_resource_expected()
    file = FileGodotProject(_projdir/"project.godot")
    file.load(c)

    res : GdResourceFileImport = file.data
    assert (res.config_version == exp.config_version)
    assert(res.categories["application"] == exp.categories["application"])
    assert(res.categories["display"] == exp.categories["display"])
    assert(res.categories["physics"] == exp.categories["physics"])
    assert(res.categories["rendering"] == exp.categories["rendering"])

def get_exp_tscn()->GdResourceFileScene:
    c = Context()
    res = GdResourceFileScene()
    res.format = 3
    res.uid = "uid://c0irlon13iq4o"
    
    res.node_resources.extend((
            SubResourceNode(name="A", type="None", parent=None, unique_id=653408050, node_paths=GdValuePackedStringArray(("noderef",)), properties = PropertyCollection({
                "script" : GdValueExtResource("1_8dc4x"),
                "resource" : GdValueSubResource("Resource_1gj03"),
                "noderef" : GdValueNodePath("B/D"),
            }.items())),
            SubResourceNode(name="D", type="None", parent="B", unique_id=1174449336, node_paths=GdValuePackedStringArray(("noderef",)), properties = PropertyCollection({
                "script" : GdValueExtResource("1_8dc4x"),
                "resource" : GdValueSubResource("Resource_8dc4x"),
                "noderef" : GdValueNodePath("../../C/E"),
            }.items())),
            SubResourceNode(name="C", type="None", parent=".", unique_id=452580425, properties = PropertyCollection({
                "unique_name_in_owner" : True
            }.items())),
            SubResourceNode(name="B", type="None", parent=".", unique_id=1524297946),
            SubResourceNode(name="E", type="None", parent="C", unique_id=1972079933),
    ))
    
    res.sub_resources.extend((
        SubResource(id="Resource_1gj03", type="Resource", properties=PropertyCollection({
            "resource_local_to_scene" : True
        }.items())),
        SubResource(id="Resource_8dc4x", type="Resource", properties=PropertyCollection({
            "resource_local_to_scene" : True
        }.items())),
    ))
    
    res.ext_resources.extend((
        SubResourceExt(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="1_8dc4x"),
    ))
    
    res.node_resources.build_tree(c)
    
    return res

def test_tscn():
    c = Context()
    exp = get_exp_tscn()
    file = FileTscn(_projdir/"assets"/"tscn.tscn")
    file.load(c)
    res : GdResourceFileScene = file.data

    assert(res.format == exp.format)
    assert(res.uid == exp.uid)

    assert(res.node_resources[653408050])
    assert(res.node_resources[1524297946])
    assert(res.node_resources[1174449336])
    assert(res.node_resources[452580425])
    assert(res.node_resources[1972079933])

    assert(res.node_resources[653408050] == exp.node_resources[653408050])
    assert(res.node_resources[1524297946] == exp.node_resources[1524297946])
    assert(res.node_resources[1174449336] == exp.node_resources[1174449336])
    assert(res.node_resources[452580425] == exp.node_resources[452580425])
    assert(res.node_resources[1972079933] == exp.node_resources[1972079933])