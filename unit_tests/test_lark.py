# from lark import Lark
# from lark.visitors import Transformer, v_args
# from pathlib import Path

# from structure_values import *
# from structure_resources import *

# from typing import Any

# cwd = Path.cwd()
# grammer = (cwd / "tscn.lark").read_text()
# file = (cwd / "test.tscn").read_text()

# parser = Lark(grammer, parser="earley")
# tree = parser.parse(file)

# print(tree.pretty())