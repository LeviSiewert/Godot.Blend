from fsspec.implementations.memory import MemoryFileSystem

from ...core.structure import Project, File, Resource
from ...files import file_types


def test_construct():
    fs = MemoryFileSystem()
    Project(fs,file_types, search = False)

def test_construct_w_resources():
    pass

def test_file_changeloc():
    raise NotImplementedError()

def test_file_duplicate():
    raise NotImplementedError()

def test_resource_duplicate():
    raise NotImplementedError()

def test_embedd_subresource():
    raise NotImplementedError()

def test_unembedd_subresource():
    raise NotImplementedError()


def test_search():
    fs = MemoryFileSystem()
    Project(fs,file_types)
    raise NotImplementedError()

def test_projectfile_cached_uid():
    raise NotImplementedError()

def test_tres_cached_uid():
    raise NotImplementedError()

def test_tscn_cached_uid():
    raise NotImplementedError()

def test_import_cached_uid():
    raise NotImplementedError()


def test_projectfile_roundtrip():
    raise NotImplementedError()

def test_tres_roundtrip():
    raise NotImplementedError()

def test_tscn_roundtrip():
    raise NotImplementedError()

def test_import_roundtrip():
    raise NotImplementedError()


def test_tres_deps_load():
    raise NotImplementedError()

def test_tscn_deps_load():
    raise NotImplementedError()


def test_tres_modify_deps():
    raise NotImplementedError()

def test_tscn_modify_deps():
    raise NotImplementedError()

def test_tscn_structure_change():
    raise NotImplementedError()


def test_tscn_instance():
    raise NotImplementedError()

def test_tscn_instance_failload():
    raise NotImplementedError()


def test_tscn_instance_editable():
    raise NotImplementedError()

def test_tscn_instance_editable_failload():
    raise NotImplementedError()