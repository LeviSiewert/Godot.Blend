from ._transformer import (
    GdToPyTransformer,
    GdToPyRuleset,
    GdToPyModule,
    GdToPyContext,

    PyToGdTransformer,
    PyToGdRuleset,
    PyToGdModule,
    PyToGdContext
)

from . import structure, values, terminals_and_simple, definitions, structure_promise

gd_to_py = GdToPyTransformer("GdToPy", *[
    values.gd_to_py_ruleset,
    terminals_and_simple.gd_to_py_ruleset,
    structure.gd_to_py_ruleset, 
    definitions.gd_to_py_ruleset,
    structure_promise.gd_to_py_ruleset,
])

py_to_gd = PyToGdTransformer("PyToGd", *[
    values.py_to_gd_ruleset,
    terminals_and_simple.py_to_gd_ruleset,
    structure.py_to_gd_ruleset, 
    definitions.py_to_gd_ruleset,
    structure_promise.py_to_gd_ruleset,
])