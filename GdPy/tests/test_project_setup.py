from .. import *
from ..structure.files import files
# from ..core.files import files
from ..resources import cls_def
from pathlib import Path as _Path
# import pytest

_thisdir = _Path(__file__).parent.resolve()

def test_project_setup():
    root = _thisdir/"project"
    
    file_db = FileDb(root, files)
    class_db = ClassDb()
    project = GdProject(root, file_db, class_db)

    def_file = project.file_db.get("res://.PyGd/class_definitions.tres", FileClassDefinition("", cls_def))
    with project.context() as c:
        def_file.load(c)
    project.class_db.set_file(def_file)