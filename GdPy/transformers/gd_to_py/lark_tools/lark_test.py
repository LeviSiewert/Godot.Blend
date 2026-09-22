
from lark import Lark

from pathlib import Path as Path
_thisdir = Path(__file__).parent.resolve()
grammer : str = (_thisdir / "godot.lark").read_text()

def test_construction():
    parser = Lark(grammer, parser="lalr", propagate_positions=False, maybe_placeholders=True, cache=True)

# def test_printsubset():
#     parser = Lark(grammer, parser="lalr", start="start", propagate_positions=False, maybe_placeholders=True, cache=True)
#     base = '[gd_resource]'
#     raise Exception(parser.parse(base))