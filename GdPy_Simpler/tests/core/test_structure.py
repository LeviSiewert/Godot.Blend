import pytest

from fsspec import AbstractFileSystem

from ...core.structure import Project, File, Resource, ResourceRef, FileRef

@pytest.mark.dependency(name="Test_File", depends=["test_signals.py::Test_Signals"] )
class Test_File():

    def test_contstruction(self):
        raise NotImplementedError()


@pytest.mark.dependency(name="Test_Resource", depends=["test_signals.py::Test_Signals", "test_gdtype.py::Test_GdType"] )
class Test_Resource():
    
    def test_contstruction(self):
        raise NotImplementedError()

    def test_instance(self):
        raise NotImplementedError()

    def test_instance_editability(self):
        raise NotImplementedError()

    def test_overlay(self):
        raise NotImplementedError()

    def test_overlay_properties(self):
        raise NotImplementedError()

    def test_overlay_editability(self):
        raise NotImplementedError()

    def test_overlay_thin_recognition(self):
        raise NotImplementedError()
    
    def test_gdtype_defaults(self):
        raise NotImplementedError()

    def test_gdtype_verification(self):
        raise NotImplementedError()


@pytest.mark.dependency(name="Test_Project", depends=["test_signals.py::Test_Signals", "test_context.py::Test_Context", "test_collection.py::Test_Collection", "Test_Resource", "Test_File"] )
class Test_Project():

    def test_construction(self):
        raise NotImplementedError()

    def test_construction_file_resource_refs(self):
        raise NotImplementedError()

    def test_fs_root(self):
        raise NotImplementedError()

    def test_fs_search(self):
        raise NotImplementedError()

    def test_fs_search(self):
        raise NotImplementedError()

    def test_fs_search_match(self):
        raise NotImplementedError()

    def test_fs_events(self):
        raise NotImplementedError()

    def test_fs_dif_update(self):
        raise NotImplementedError()
