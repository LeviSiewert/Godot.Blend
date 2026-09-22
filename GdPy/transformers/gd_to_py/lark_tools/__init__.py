from pathlib import Path as _Path

_thisdir = _Path(__file__).parent.resolve()

grammer : str = (_thisdir / "godot.lark").read_text()

from lark import Lark

def make_parser(key:str="start")->Lark:
    return Lark(grammer, parser="lalr", start=key, propagate_positions=False, maybe_placeholders=True, cache=True)
    # return Lark(grammer, parser="lalr", start=key, propagate_positions=True, maybe_placeholders=True, cache=True)
    ## current (propigate_positions = True) for token.meta -> memo[id] generation, even if it slows things down a little 

parser = make_parser()