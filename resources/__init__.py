from pathlib import Path

# cwd = Path.cwd()
thisdir = Path(__file__).parent.resolve()
grammer = (thisdir / "tscn.lark").read_text()