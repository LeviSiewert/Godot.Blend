from pathlib import Path as _Path

_thisdir = _Path(__file__).parent.resolve()

grammar : str = (_thisdir / "godot.lark").read_text()

from lark import Lark
from . import grammar

def make_parser(key:str="start")->Lark:
    # TODO: Figure out if I can "stream" through a secondary tranformer or customization on lark
    # Would improve memory performance a lot 
    return Lark(grammar, start=key, maybe_placeholders=True) #, parser='lalr')
