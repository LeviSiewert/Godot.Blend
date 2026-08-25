from ._transformer import (
    GdToPyTransformer,
    GdToPyRulesset,
    GdToPyModule,
    GdToPyContext,

    PyToGdTransformer,
    PyToGdRulesset,
    PyToGdModule,
    PyToGdContext
)

from . import values

gd_to_py = GdToPyTransformer("GdToPy", *[
    *values.GdToPyRulesset,
])

py_to_gd = PyToGdTransformer("PyToGd", *[
    *values.PyToGdRulesset,
])