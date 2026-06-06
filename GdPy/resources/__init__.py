from pathlib import Path as _Path

_thisdir = _Path(__file__).parent.resolve()

grammer : str = (_thisdir / "godot.lark").read_text()
cls_def : _Path = _thisdir / "class_definitions.tres" 