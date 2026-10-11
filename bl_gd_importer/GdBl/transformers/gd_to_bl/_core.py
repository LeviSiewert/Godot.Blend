import bpy
from typing import Iterable

from ._transformers import GdToBlSession, BlToGdSession, GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet

from . import nodes

def make_gd_to_bl(extras : Iterable[GdToBlTransformerSet]): 
    return GdToBlSession([
        nodes.gd_to_bl,
        *extras,
    ])

def make_bl_to_gd(extras : Iterable[BlToGdTransformerSet]):
    return BlToGdSession([
        nodes.bl_to_gd,
        *extras,
    ])