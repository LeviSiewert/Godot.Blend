from __future__ import annotations
from ...core.transformer import Session, TransformerSet, Transformer
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer
from typing import Iterable

from . import (
    values,
    promises
)

def make_gd_to_py[TS:GdToPy_TransformerSet[GdToPy_Transformer]](insert:Iterable[TS]=tuple())->Session[GdToPy_TransformerSet[GdToPy_Transformer]|TS]:
    return Session([
        values.gd_to_py,
        promises.gd_to_py,
        *insert
    ])

def make_py_to_gd[TS:PyToGd_TransformerSet[PyToGd_Transformer]](insert:Iterable[TS]=tuple())->Session[PyToGd_TransformerSet[GdToPy_Transformer]|TS]:
    return Session([
        values.py_to_gd,
        promises.py_to_gd,
        *insert
    ])

