from lark import Lark
from pathlib import Path

cwd = Path.cwd()
grammer = (cwd / "tscn.lark").read_text()
file = (cwd / "test.tscn").read_text()

parser = Lark(grammer, parser="earley")
tree = parser.parse(file)
print(tree.pretty())