from ..structure import *
from pathlib import Path

def get_fixture_gd_definition()->str:
    return Path(__file__).parent / "fixture_gd_type_definition.json"

