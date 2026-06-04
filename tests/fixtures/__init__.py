from pathlib import Path
from ...PyGd.structure import *

thisdir = Path(__file__).parent.resolve()

class tscn:
    props  : Path = thisdir / "props/test.tscn"
    test_a : Path = thisdir / "scene/test_a.tscn"
    test_b : Path = thisdir / "scene/test_b.tscn"

class tscn_res:
    props : GdFile
    test_a : GdFile
    test_b : GdFile

class imports:
    svg : Path = thisdir / "import/icon.svg.import"
    
class tres:
    pass

class project:
    pass