from .core import GdParser

from ..resources import grammer
from .values_transformer import gd_to_py_ruleset as gd_to_py_values_ruleset
from .sub_resources_transformer import gd_to_py_ruleset as gd_to_py_subres_ruleset
from .sub_resource_collections_transformer import gd_to_py_ruleset as gd_to_py_subrescol_ruleset
from .resources_transformer import gd_to_py_ruleset as gd_to_py_res_ruleset
from .references_transformer import gd_to_py_ruleset as gd_to_py_ref_ruleset
from .generic_transformer import gd_to_py_ruleset as gd_to_py_gen_ruleset

from .values_transformer import py_to_gd_ruleset as py_to_gd_values_ruleset
from .sub_resources_transformer import py_to_gd_ruleset as py_to_gd_subres_ruleset
from .sub_resource_collections_transformer import py_to_gd_ruleset as py_to_gd_subrescol_ruleset
from .resources_transformer import py_to_gd_ruleset as py_to_gd_res_ruleset
from .references_transformer import py_to_gd_ruleset as py_to_gd_ref_ruleset
from .generic_transformer import py_to_gd_ruleset as py_to_gd_gen_ruleset

def construct_keyed_parser(start:str):
    ''' Test utility function, for constructing a gdparser with a different key '''
    return GdParser(grammer, 
    parser_rulesets=(
        gd_to_py_values_ruleset, 
        gd_to_py_subres_ruleset,
        gd_to_py_subrescol_ruleset,
        gd_to_py_res_ruleset,
        gd_to_py_ref_ruleset,
        gd_to_py_gen_ruleset,
    ),
    render_rulesets=(
        py_to_gd_values_ruleset,
        py_to_gd_subres_ruleset,
        py_to_gd_subrescol_ruleset,
        py_to_gd_res_ruleset,
        py_to_gd_ref_ruleset,
        py_to_gd_gen_ruleset,
    ),
    start = start,
    )

gdparser = construct_keyed_parser("start")