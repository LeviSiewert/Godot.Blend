from ..structure.core.file_db import FileDb
from ..structure.files import files
from pathlib import Path as _Path

_thisdir = _Path(__file__).parent.resolve()
_proj_root = _thisdir/"project"

def test_filedb_construction():
    file_db = FileDb(_proj_root, files)

    assert(file_db["res://project.godot"])
    assert(file_db["res://assets/icon.svg"])
    assert(file_db["res://assets/blender.blend"])
    assert(file_db["res://assets/blender.glb"])
    assert(file_db["res://assets/script.gd"])
    assert(file_db["res://assets/script_global.gd"])
    assert(file_db["res://assets/tscn.tscn"])

def test_filedb_population():
    file_db = FileDb(_proj_root, files)

def _assert_eq(file_db,a,b):
    _a = file_db[a]
    _b = file_db[b]
    assert(not (_a is None))
    assert(_a is _b)

def test_filedb_respath():
    file_db = FileDb(_proj_root, files)
    _assert_eq(file_db, "res://project.godot", _proj_root/"project.godot")
    _assert_eq(file_db, "res://assets/icon.svg", _proj_root/"assets/icon.svg")
    _assert_eq(file_db, "res://assets/blender.blend", _proj_root/"assets/blender.blend")
    _assert_eq(file_db, "res://assets/blender.glb", _proj_root/"assets/blender.glb")
    _assert_eq(file_db, "res://assets/script.gd", _proj_root/"assets/script.gd")
    _assert_eq(file_db, "res://assets/script_global.gd", _proj_root/"assets/script_global.gd")
    _assert_eq(file_db, "res://assets/tscn.tscn", _proj_root/"assets/tscn.tscn")

def test_filedb_uidpath_importdefined():
    file_db = FileDb(_proj_root, files)

    ## Import defined UIDs
    _assert_eq(file_db,"res://assets/icon.svg", "uid://n7opm812ptfd")
    _assert_eq(file_db,"res://assets/blender.blend", "uid://gt2mbfsmssh1")
    _assert_eq(file_db,"res://assets/blender.glb", "uid://cocfi2vsn5qt2")

def test_filedb_uidpath_uidfiledefined():
    file_db = FileDb(_proj_root, files)
    ## .uid defined UIDs
    _assert_eq(file_db,"res://assets/script.gd", "uid://cr1tpol7u62kd")
    _assert_eq(file_db,"res://assets/script_global.gd", "uid://4ixpsfd7ehyv")

def test_filedb_uidpath_intrensicdefined():
    file_db = FileDb(_proj_root, files)
    ## Self Defined UIDs
    _assert_eq(file_db,"res://assets/tscn.tscn", "uid://c0irlon13iq4o")