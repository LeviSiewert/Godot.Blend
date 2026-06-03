import pytest

from lark import Lark
from ...PyGd.structure import *
from ...tests.fixtures import tscn
from ...PyGd.resources import grammer


transformer = GdType.generate_transformer()

def test_basic_parse():
    transformer
    pass