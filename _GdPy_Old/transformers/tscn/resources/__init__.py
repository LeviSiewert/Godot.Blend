from pathlib import Path as _Path

_thisdir = _Path(__file__).parent.resolve()

grammar : str = (_thisdir / "godot.lark").read_text()