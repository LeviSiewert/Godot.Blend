from ... import *
from ...structure.files import FileClassDefinition, files
# from ..core.files import files
from ...resources import cls_def
from pathlib import Path as _Path
# import pytest

_thisdir = _Path(__file__).parent.resolve()

def test_project_setup():
    root = _thisdir/"project"
    
    file_db = FileDb(root, files)
    class_db = ClassDb()
    project = GdProject(root, file_db, class_db)

    def_file = project.file_db.get_file("res://.PyGd/class_definitions.tres", null_ok=True)
    if def_file == None:
        def_file = FileClassDefinition("", cls_def)
    project.class_db.set_src_file(def_file)
    with project.context() as c:
        project.class_db.load_fr_src_file(c)