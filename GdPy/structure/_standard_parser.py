from .core import GdParser

from ..resources import grammer
from .values_transformer import gd_to_py_ruleset as values_ruleset
from .sub_resources_transformer import gd_to_py_ruleset as subres_ruleset
from .sub_resource_collections_transformer import gd_to_py_ruleset as subrescol_ruleset
# from .resources_transformer import gd_to_py_ruleset as res_ruleset
# from .references_transformer import gd_to_py_ruleset as ref_ruleset

gdparser = GdParser(grammer, (
    values_ruleset, 
    subres_ruleset,
    subrescol_ruleset,
    # res_ruleset,
    # ref_ruleset,
    ))
