from __future__ import annotations

from .structure_promise import StructReference, RefType
from .structure import Context, Properties, Project, Resource, ExtResource, Node, NodePath, File
from .collection import Collection, CollectionKey

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


    def test_get_overlay_resolveref(self):
        ## TODO: Resolve reference through any means
        ...

    def test_get_overlay_resolveref_localize(self):
        ## TODO: two resources, ref 1 subresource, commit to another. Localize ref on get.
        ...

    def test_get_overlay_resolveref_localize_false(self):
        ## TODO: two resources, ref 1 subresource, commit to another. Don't localize ref on get.
        ...


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


    class Test_SubResource:

        def test_normalized_inclusion(self):
            r = Resource(uid="id")
            sr = Resource()
            r.properties["a"] = sr
            r.normalize()
            assert sr in r.sub_resources
            assert sr.context._extends is r.context

        def test_normalized_inclusion_nested(self):
            r = Resource(uid="id")
            sr1 = Resource()
            sr2 = Resource()
            r.properties["a"] = sr1
            sr1.properties["a"] = sr2
            r.normalize()
            assert sr1 in r.sub_resources
            assert sr2 in r.sub_resources
            assert sr1.context._extends is r.context
            assert sr2.context._extends is r.context
            
    class Test_ExtResource:
        
        def test_normalized_conversion(self):
            r1 = Resource("uid_a")
            r2 = Resource("uid_b")
            r1.properties["a"] = r2

            r1.normalize()

            assert len(r1.ext_resources) == 1
            assert tuple(r1.ext_resources.values())[0]._resource.sref is r2
        
        def test_normalized_conversion_nested(self):
            r1 = Resource("uid_a")
            r2 = Resource("uid_b")
            r3 = Resource("uid_b")
            r1.properties["a"] = r2
            r2.properties["a"] = r3

            r1.normalize()

            assert len(r1.ext_resources) == 1
            assert tuple(r1.ext_resources.values())[0]._resource.sref is r2
            assert len(r2.ext_resources) == 1
            assert tuple(r2.ext_resources.values())[0]._resource.sref is r3






class Test_File:...

class Test_Project:...

class Test_Structure_Normalize:...