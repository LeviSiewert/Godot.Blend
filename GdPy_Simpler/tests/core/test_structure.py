import pytest

from fsspec import AbstractFileSystem

from ...core.structure import Project, File, Resource, ResourceRef, FileRef

class Test_File():

    def test_construction(self):
        file = File.construct(
            "res://abc.txt",
            cached_uid="uid://abc",
            resource=None,
            properties={},
        )
        assert file.meta_properties.context.file == file

        assert file.filepath.key == "res://abc.txt"
        assert file.resource.key == "uid://abc"

# @pytest.mark.dependency(name="Test_Resource", depends=["test_signals.py::Test_Signals", "test_gdtype.py::Test_GdType"] )
class Test_Resource():
    
    def test_construction(self):
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
            },
        )

        # assert res.properties.context.resource == res
        assert res.properties.context.subresource == res

        assert res.uid.key == "uid://abc"
        assert res.file.key == "res://abc.txt"
        assert res.file.get() is None

        assert res.properties["a"] == "a"

    def test_subresource_tracking_construction(self):
        raise NotImplementedError()
    
    def test_subresource_tracking_implicit(self):
        subres = Resource.construct(
            properties={
                "a":"a",
            },
        )
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
                "b": subres, 
            },
        )

        assert subres in res.subresources
        assert subres.id
        

    def test_construction_overlay_direct(self):
        overlay_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":"c",
            },
            overlay=overlay_res,
        )

        assert res.properties.overlay is overlay_res.properties

        assert overlay_res.properties["a"] == "a"
        assert overlay_res.properties["b"] == "b"

        assert res.properties["a"] == "a"
        assert res.properties["b"] == "c"
        assert res.properties["c"] == "c"

    def test_construction_instance_direct(self):
        ''' Test direct instance construction'''

        inst_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        inst_file = File.construct(
            "res://inst_src.txt",
            resource=inst_res,
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":"c",
            },
            instance=inst_file,
            _instance_direct=True,
        )

        assert res.overlay == inst_res

        assert inst_res.properties["a"] == "a"
        assert inst_res.properties["b"] == "b"

        assert res.properties["a"] == "a"
        assert res.properties["b"] == "c"
        assert res.properties["c"] == "c"

    def test_construction_instance_delayed(self,):
        ''' Construct resources, attach to project and fullfill at that time '''
        inst_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        inst_file = File.construct(
            "res://inst_src.txt",
            resource=inst_res,
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":"c",
            },
            instance=inst_file,
        )
        assert res.instance.key == inst_file.filepath.key
        assert res.instance.get() == None

        prj = Project.construct(
            file_system = None,
            file_types = [],
            files = [
                inst_file
            ],
            resources = [
                inst_res,
                res,
            ]

        )

        assert res.overlay == inst_res

        assert inst_res.properties["a"] == "a"
        assert inst_res.properties["b"] == "b"

        assert res.properties["a"] == "a"
        assert res.properties["b"] == "c"
        assert res.properties["c"] == "c"


#     def test_instance(self):
#         raise NotImplementedError()

#     def test_instance_editability(self):
#         raise NotImplementedError()

#     def test_overlay(self):
#         raise NotImplementedError()

#     def test_overlay_properties(self):
#         raise NotImplementedError()

#     def test_overlay_editability(self):
#         raise NotImplementedError()

#     def test_overlay_thin_recognition(self):
#         raise NotImplementedError()
    
#     def test_gdtype_defaults(self):
#         raise NotImplementedError()

#     def test_gdtype_verification(self):
#         raise NotImplementedError()


# @pytest.mark.dependency(name="Test_Project", depends=["test_signals.py::Test_Signals", "test_context.py::Test_Context", "test_collection.py::Test_Collection", "Test_Resource", "Test_File"] )
# class Test_Project():

#     def test_construction(self):
#         raise NotImplementedError()

#     def test_construction_file_resource_refs(self):
#         raise NotImplementedError()

#     def test_fs_root(self):
#         raise NotImplementedError()

#     def test_fs_search(self):
#         raise NotImplementedError()

#     def test_fs_search(self):
#         raise NotImplementedError()

#     def test_fs_search_match(self):
#         raise NotImplementedError()

#     def test_fs_events(self):
#         raise NotImplementedError()

#     def test_fs_dif_update(self):
#         raise NotImplementedError()
