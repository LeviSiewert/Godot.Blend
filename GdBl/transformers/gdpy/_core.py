from __future__ import annotations
from typing import Iterable

from ._transformer import (
    GdToBl_Session,
    GdToBl_Transformer,
    GdToBl_TransformerSet,
    GdToBl_TransformerOptions,
    BlToGd_Session,
    BlToGd_Transformer,
    BlToGd_TransformerSet,
    BlToGd_TransformerOptions,
)

from . import (
    values,
    promises,
    defintions,
    structure,
    properties,
)

def make_gd_to_py[TS:BlToGd_TransformerSet[BlToGd_Transformer]](insert:Iterable[TS]=tuple())->Session[BlToGd_TransformerSet[BlToGd_Transformer]|TS]:
    return BlToGd_Session([
        *insert
    ])

def make_py_to_gd[TS:GdToBl_TransformerSet[GdToBl_Transformer]](insert:Iterable[TS]=tuple())->Session[GdToBl_TransformerSet[BlToGd_Transformer]|TS]:
    return GdToBl_Session([
        *insert
    ])

