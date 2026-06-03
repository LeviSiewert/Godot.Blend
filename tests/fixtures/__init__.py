from pathlib import Path

thisdir = Path(__file__).parent.resolve()

class tscn:
    props  : Path = thisdir / "props/test.tscn"
    test_a : Path = thisdir / "scene/test_a.tscn"
    test_b : Path = thisdir / "scene/test_b.tscn"

class imports:
    svg : Path = thisdir / "import/icon.svg.import"
    
class tres:
    pass

class project:
    pass