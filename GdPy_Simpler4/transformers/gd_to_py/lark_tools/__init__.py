from pathlib import Path as _Path

_thisdir = _Path(__file__).parent.resolve()

grammer : str = (_thisdir / "godot.lark").read_text()

from lark import Lark

def make_parser(key:str="start")->Lark:
    return Lark(grammer, parser="lalr", start=key, propagate_positions=False, maybe_placeholders=True)
    # return Lark(grammer, parser="earley", propagate_positions=False, maybe_placeholders=True)
    # return Lark(grammer, propagate_positions=False, maybe_placeholders=True)

parser = make_parser()