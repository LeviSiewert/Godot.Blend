from .. import *
from .. import resources as res 
from pathlib import Path as _Path
# import pytest

_thisdir = _Path(__file__).parent.resolve()

def test_project_setup():
    root = _thisdir/"project"
    
    file_db = FileDb(root)
    class_db = ClassDb()
    project = GdProject(root, file_db, class_db)

    def_file = project.file_db.get("res://.PyGd/class_definitions.tres", FileClassDefinition("", res.cls_def))
    def_file.load()
    project.class_db.set_file(def_file)