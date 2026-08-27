from __future__ import annotations


from typing import Self

from .structure_promise import StructReference, RefType
from .structure import Context, Properties, Project, Resource, ExtResource, Node, NodePath, File, Collection, CollectionKey, CollectionOverlayMode
# from .collection import Collection, CollectionKey

from contextvars import ContextVar

class Test_Properties:
    def test_construction(self):
        p = Properties({"a":"a"},context=Context())
        assert p.data == {"a":"a"}

    def test_obj_to_ref(self):
        p = Properties(context=Context())
        res = Resource()
        p["ref"] = res
        ref = p.get("ref", resolve_reference=False)
        assert isinstance(ref, StructReference)
        assert ref.ref_type is RefType.DEFER
        assert ref.sref is res

    def test_ref_to_ref(self):
        p = Properties(context=Context())
        r = StructReference(key="", ref_type=RefType.RID)
        p["ref"] = r
        ref = p.get("ref", resolve_reference=False) 
        assert ref is r

    def test_overlay_extrensics(self):
        p0 = Properties({"a":"A0", "c":"C0"},context=Context())
        p1 = Properties({"a":"A1", "b":"B1"},context=Context())
        p1.set_overlay(p0)

        assert p1.overlay is p0 
        assert tuple(p1.keys(use_overlay=False)) == tuple({"a":"A1", "b":"B1"}.keys())
        assert tuple(p1.keys(use_overlay=True))  == tuple({"a":"A1", "b":"B1", "c":"C0"}.keys())

        assert tuple(p1.values(use_overlay=False)) == tuple({"a":"A1", "b":"B1"}.values())
        assert tuple(p1.values(use_overlay=True))  == tuple({"a":"A1", "b":"B1", "c":"C0"}.values())

        assert dict(p1.items(use_overlay=False)) == {"a":"A1", "b":"B1"}
        assert dict(p1.items(use_overlay=True))  == {"a":"A1", "b":"B1", "c":"C0"}

    def test_overlay_set_dif(self):
        p0 = Properties({"a":"A0", "c":"C0"},context=Context())
        p1 = Properties({"a":"A1", "b":"B1"},context=Context())

        res = p1.set_overlay(p0)

        expected = {
            "added" : {"c":"C0"},
            "removed" : {},
            "updated" : {},
        }

        assert res == expected
        assert p1 == {"a":"A1", "b":"B1", "c":"C0"}

    def test_overlay_set_change(self):
        p0_a = Properties({"a":"A0_a", "c":"C0_a", "e":"E0_a"},context=Context())
        p0_b = Properties({"a":"A0_b", "c":"C0_b", "d":"D0_b"},context=Context())
        p1 = Properties({"a":"A1", "b":"B1"},context=Context())
        p1.set_overlay(p0_a)

        result = p1.set_overlay(p0_b)
        
        expected = {
            "added" : {"d":"D0_b"},
            "removed" : {"e":"E0_a"},
            "updated" : {"c":("C0_a", "C0_b")},
        }

        assert result == expected 
        assert p1 == {"a":"A1", "b":"B1", "c":"C0_b", "d":"D0_b"} 

    def test_overlay_set_none(self):
        p0 = Properties({"a":"A0", "c":"C0"},context=Context())
        p1 = Properties({"a":"A1", "b":"B1"},context=Context())
        p1.set_overlay(p0)

        result = p1.set_overlay(None)

        expected = {
            "added" : {} ,
            "removed" : {"c":"C0"} ,
            "updated" : {},
        }

        assert result == expected
        assert p1 == {"a":"A1", "b":"B1"}
    

    def test_get_overlay_local(self):
        p0 = Properties({"a":"A0", "c":"C0"},context=Context())
        p1 = Properties({"a":"A1", "b":"B1"},context=Context())
        p2 = Properties({"a":"A2"},context=Context())
        p1.set_overlay(p0)
        p2.set_overlay(p1)

        assert p1.get("c", use_overlay=True, default=None) == "C0"
        assert p1.get("c", use_overlay=False, default=None) is None

        assert p1.get("a", use_overlay=True, default=None) == "A1"
        assert p1.get("a", use_overlay=False, default=None) == "A1"

        assert p2.get("a", use_overlay=True, default=None) == "A2"
        assert p2.get("b", use_overlay=True, default=None) == "B1"
        assert p2.get("c", use_overlay=True, default=None) == "C0"

        assert p2.get("a", use_overlay=False, default=None) == "A2"
        assert p2.get("b", use_overlay=False, default=None) is None
        assert p2.get("c", use_overlay=False, default=None) is None


class Test_ExtResource:
    def test_construction_string(self):
        extres = ExtResource(id="extres_id", file="file_id", resource="resource_id" )

        assert extres.id.key == "extres_id"

        assert isinstance(extres.resource, StructReference)
        assert extres.resource.key == "resource_id"

        assert isinstance(extres.file, StructReference)
        assert extres.file.key == "file_id"

    def test_construction_reference(self):
        resource = Resource()
        file = File(path="filepath.py")
        extres = ExtResource(id="extres_id", file=file, resource=resource )

        assert extres.id.key == "extres_id"

        assert isinstance(extres._resource, StructReference)
        assert extres.resource is resource

        assert isinstance(extres._file, StructReference)
        assert extres.file is file
    

class Test_Resource:
    def test_construction(self):
        Resource()

    def test_construction_subres(self):
        res = Resource(id="some_id")
        assert res.is_subresource()
        assert res.uid.key is None
        assert res.file is None

    def test_construction_file(self):
        res = Resource(uid="some_uid", file="file")
        assert not res.is_subresource()
        assert not (res.file is None)

    def test_construction_file_sref(self):
        file = File(path = "path")
        res = Resource(uid ="some_uid", file=file)
        assert not res.is_subresource()
        assert not (res.file is None)

    def test_overlay(self):
        R0 = Resource(id="some_id", properties={"a":"A0", "b":"B0", "c":"C0"})
        R1 = Resource(id="some_id", instance=R0, properties={"a":"A1", "c":"C1"})

        assert R1.overlay is R0
        assert R1.properties.overlay is R0.properties
        assert R1.properties["a"] == "A1"
        assert R1.properties["b"] == "B0"

        R1.set_overlay(None)
        assert R1.overlay is None
        assert R1.properties.overlay is None

    def test_overlay_signals(self):
        R0 = Resource(id="some_id")
        R1 = Resource(id="some_id")

        c = ContextVar("")
        R1.overlay_updated.connect(lambda x: c.set(x))

        R1.set_overlay(R0)
        assert c.get() is R0

        R1.set_overlay(None)
        assert c.get() is None

    def test_construct_resource_structure(self):
        R0 = Resource(uid="R0")
        Sr0 = Resource(id="Sr0")
        Sr1 = Resource(id="Sr1", properties = {"ref":Sr0, "ref2":R0})
        R1 = Resource(uid="R1", sub_resources = [Sr0,Sr1], properties={"a":Sr0, "b":Sr1}, ext_resources=[R0])

        assert len(R1.sub_resources) == 2

        assert Sr0 in R1.sub_resources
        assert Sr0.id == "R0"

        assert Sr1 in R1.sub_resources
        assert Sr1.id == "Sr1"

        assert len(R1.ext_resources) == 1
        assert isinstance(R1.ext_resources[0], ExtResource).resource is R0
        assert R1.ext_resources[0].resource is R0

class Test_Node:

    def test_construction_subres(self):
        N0 = Node("N0",id="some_id")
        assert N0.is_subresource()
        assert N0.uid.key is None
        assert N0.file is None

    def test_construction_file(self):
        N0 = Node("N0",uid="some_uid", file="file")
        assert not N0.is_subresource()
        assert not (N0.file is None)

    def test_construction_file_sref(self):
        file = File(path = "path")
        N0 = Node("N0",uid ="some_uid", file=file)
        assert not N0.is_subresource()
        assert not (N0.file is None)
        

    def test_construct_overlay(self):
        N0 = Node("N0", properties={"a":"A0", "b":"B0", "c":"C0"})
        N1 = Node("N1", instance=N0, properties={"a":"A1", "c":"C1"})

        assert N1.overlay is N0
        assert N1.properties.overlay is N0.properties
        assert N1.properties["a"] == "A1"
        assert N1.properties["b"] == "B0"

        N1.set_overlay(None)
        assert N1.overlay is None
        assert N1.properties.overlay is None

    def test_overlay_signals(self):
        N0 = Resource("N0")
        N0 = Resource("N0")

        c = ContextVar("")
        N0.overlay_updated.connect(lambda x: c.set(x))

        N0.set_overlay(N0)
        assert c.get() is N0

        N0.set_overlay(None)
        assert c.get() is None

    def test_construct_structure(self):
        N0 = Node("N0",
            properties = {
                "a" : "A0",
                "b" : "B0",
            },
            children = [
                Node("N1"),
                Node("N2"),
                Node("N3",
                    children = [
                        Node("N1",
                        ),
                    ],
                ),
            ],
        )

        assert len(N0.children) == 3


    def test_construct_instance_load(self):
        N0 = Node("N0", properties = {"a":"A0", "c":"C0"})
        N1 = Node("N1", properties = {"a":"A1", "b":"B1"}, instance = N0, setup_overlay=True)
        assert N1.overlay is N0

    def test_construct_instance_load_complex(self):
        N0 = Node("N0", 
            properties = {"a":"A0", "c":"C0"},
            children = [
                Node("A", 
                    properties = {"i_am":"A0"},
                ),
                Node("B", 
                    properties = {"i_am":"B0"},
                ),
                Node("C", 
                    properties = {"i_am":"C0"},
                    children = [
                        Node("D"),
                        Node("E"),
                    ],
                ),
            ],
        )

        N1 = Node("N1", 
            properties = {"a":"A1", "b":"B1"}, 
            instance = N0, 
            setup_overlay=True,
            children = [
                Node("A", 
                    properties = {"i_am":"A1"},
                ),
                Node("B", 
                    properties = {"i_am":"B1"},
                ),
                Node("C", 
                    properties = {"i_am":"C1"},
                    children = [
                        Node("D"), ## Matched
                        # Node("E") ## Created thin
                        Node("F"), ## Added
                    ],
                ),
            ],
        )

        assert N1.overlay is N0

        A0 = N0.children["A"]
        B0 = N0.children["B"]
        C0 = N0.children["C"]
        D0 = C0.children["D"]
        E0 = C0.children["E"]
        F0 = C0.children.get("F", default=None)

        A1 = N1.children["A"] ## Should match
        B1 = N1.children["B"] ## Should match
        C1 = N1.children["C"] ## Should match
        D1 = C1.children["D"] ## Should match (Nested)
        E1 = C1.children.get("E", default=None) ## Added thin-overlay
        F1 = C1.children["F"] ## Local, alread present

        assert A1.overlay is A0
        assert B1.overlay is B0
        assert C1.overlay is C0

        assert len(C1.children) == 3

        assert D1.overlay is D0
        assert E1.overlay is E0
        assert F1.overlay is F0

        N1.set_overlay(None, keep_thin=False)

        assert A1.overlay is None
        assert B1.overlay is None
        assert C1.overlay is None

        assert len(C1.children) == 2

        assert D1.overlay is None
        assert E1.overlay is None
        assert F1.overlay is None

        assert not E1 in C1.children

    # def test_construct_instance_load_complex_localize_reference():
    #     pass