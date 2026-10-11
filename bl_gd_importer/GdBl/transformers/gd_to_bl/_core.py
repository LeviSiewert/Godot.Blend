import bpy
from typing import Iterable

from ._transformers import GdToBlSession, BlToGdSession, GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet

def make_gd_to_bl(extras : Iterable[GdToBlTransformerSet]): 
    return GdToBlSession([
        *extras
    ]) #TODO: Stub

def make_bl_to_gd(extras : Iterable[BlToGdTransformerSet]):
    return BlToGdSession([
        *extras
    ]) #TODO: Stub