
from pathlib import Path as _Path

# from ..structure.resources import GdResourceImport, GdSubresourseCategory, GdResourceScene, GdSubResourceNode
# from ..structure.files import FileGodotProject, FileTscn, FileTres
# from ..structure.values import *

from ...structure.core import PropertyCollection, Context
from ...structure.resources import GdResourceImport, GdResourceScene, GdResourceTres
from ...structure.sub_resource_collections import CollectionExtRes, CollectionEditRes, CollectionNodeRes, CollectionNodeRes, CollectionCatRes
from ...structure.sub_resources import SubResource, SubResourceCategory, SubResourceEdit, SubResourceExt, SubResourceNode 
from ...structure.files import FileGodotProject, FileTscn
from ...structure.references import GdValueExtResource, GdValueSubResource, GdValueNodePath

from ...structure.values import GdValuePackedStringArray

_projdir = _Path(__file__).parent.resolve() / "project"

def project_resource_expected()->GdResourceImport:
    res = GdResourceImport()
    res.config_version = 5

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

    res : GdResourceImport = file.data
    assert (res.config_version == exp.config_version)
    assert(res.cat_resources["application"] == exp.cat_resources["application"])
    assert(res.cat_resources["display"] == exp.cat_resources["display"])
    assert(res.cat_resources["physics"] == exp.cat_resources["physics"])
    assert(res.cat_resources["rendering"] == exp.cat_resources["rendering"])

def get_exp_tscn()->GdResourceScene:
    c = Context()
    res = GdResourceScene()
    res.format = 3
    res.uid = "uid://c0irlon13iq4o"
    
    res.node_resources.extend((
            SubResourceNode.new(name="A", type="Node", parent=None, unique_id=653408050, node_paths=GdValuePackedStringArray(("noderef",)), properties = PropertyCollection({
                "script" : GdValueExtResource("1_8dc4x"),
                "resource" : GdValueSubResource("Resource_1gj03"),
                "noderef" : GdValueNodePath("B/D"),
            }.items())),
            SubResourceNode.new(name="D", type="Node", parent="B", unique_id=1174449336, node_paths=GdValuePackedStringArray(("noderef",)), properties = PropertyCollection({
                "script" : GdValueExtResource("1_8dc4x"),
                "resource" : GdValueSubResource("Resource_8dc4x"),
                "noderef" : GdValueNodePath("../../C/E"),
            }.items())),
            SubResourceNode.new(name="C", type="Node", parent=".", unique_id=452580425, properties = PropertyCollection({
                "unique_name_in_owner" : True
            }.items())),
            SubResourceNode.new(name="B", type="Node", parent=".", unique_id=1524297946),
            SubResourceNode.new(name="E", type="Node", parent="C", unique_id=1972079933),
    ))
    
    res.sub_resources.extend((
        SubResource.new(id="Resource_1gj03", type="Resource", properties=PropertyCollection({
            "resource_local_to_scene" : True
        }.items())),
        SubResource.new(id="Resource_8dc4x", type="Resource", properties=PropertyCollection({
            "resource_local_to_scene" : True
        }.items())),
    ))
    
    res.ext_resources.extend((
        SubResourceExt.new(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="1_8dc4x"),
    ))
    
    res.node_resources.build_tree(c)
    
    return res

def test_tscn():
    c = Context()
    exp = get_exp_tscn()
    file = FileTscn(_projdir/"assets"/"tscn.tscn")
    file.load(c)
    res : GdResourceScene = file.data
    res.node_resources.build_tree(c)

    assert(res.format == exp.format)
    assert(res.uid == exp.uid)

    assert(res.node_resources[653408050])
    assert(res.node_resources[1524297946])
    assert(res.node_resources[1174449336])
    assert(res.node_resources[452580425])
    assert(res.node_resources[1972079933])

    def _compare(a, b):
        assert(a.name == b.name)
        assert(a.type == b.type)
        assert(a.properties.items == b.properties.items)
        assert(len(a._children) == len(b._children))

    _compare(res.node_resources[653408050], exp.node_resources[653408050])
    _compare(res.node_resources[1524297946], exp.node_resources[1524297946])
    _compare(res.node_resources[1174449336], exp.node_resources[1174449336])
    _compare(res.node_resources[452580425], exp.node_resources[452580425])
    _compare(res.node_resources[1972079933], exp.node_resources[1972079933])