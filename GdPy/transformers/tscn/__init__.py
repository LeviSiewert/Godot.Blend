from ._transformer import GdToPyTransformer, PyToGdTransformer, GdToPyContext, PyToGdContext
from ._parser import make_parser, file_parser
from lark import Lark

from . import (
    structure,
    values,
    terminals_and_simple,
    subresources,
    nodes,
)

gd_to_py_transformer = GdToPyTransformer(
    structure.gd_to_py_ruleset,
    values.gd_to_py_ruleset,
    terminals_and_simple.gd_to_py_ruleset,
    subresources.gd_to_py_ruleset,
    nodes.gd_to_py_ruleset,
    identifier="Standard",
)

py_to_gd_transformer = PyToGdTransformer(
    structure.py_to_gd_ruleset,
    values.py_to_gd_ruleset,
    terminals_and_simple.py_to_gd_ruleset,
    subresources.py_to_gd_ruleset,
    nodes.py_to_gd_ruleset,
    identifier="Standard",
)