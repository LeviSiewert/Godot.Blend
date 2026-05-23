from lark import Lark


from ..structure import GdType
from .. import fixtures
from .. import resources
from pprint import pprint
transformer = GdType.generate_transformer()()


def test_tranformer():
    pprint(dir(transformer))

def test_tscn():
    text = fixtures.get_test_tscn_file().read_text()
    parser = Lark(resources.grammer, maybe_placeholders=True)
    tree = transformer.transform(parser.parse(text))
    if tree is GdType:
        tree.print_tree()
    else:
        print(tree.pretty())

def test_tres():
    text = fixtures.get_test_tres_file().read_text()
    parser = Lark(resources.grammer,maybe_placeholders=True)
    tree = transformer.transform(parser.parse(text))
    if tree is GdType:
        tree.print_tree()
    else:
        print(tree.pretty())

def test_proj():
    text = fixtures.get_test_proj_file().read_text()
    parser = Lark(resources.grammer,maybe_placeholders=True)
    tree = transformer.transform(parser.parse(text))
    if tree is GdType:
        tree.print_tree()
    else:
        print(tree.pretty())


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