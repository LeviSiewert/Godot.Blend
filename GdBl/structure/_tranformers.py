from ...GdPy.structure.core.transformer_v2 import Transformer

# from .values import bl_to_py_ruleset as bl_to_py_values_ruleset
# from .sub_resources import bl_to_py_ruleset as bl_to_py_subres_ruleset
# from .sub_resource_collections import bl_to_py_ruleset as bl_to_py_subrescol_ruleset
# from .resources import bl_to_py_ruleset as bl_to_py_res_ruleset
# from .references import bl_to_py_ruleset as bl_to_py_ref_ruleset

# from .values import py_to_bl_ruleset as py_to_bl_values_ruleset
# from .sub_resources import py_to_bl_ruleset as py_to_bl_subres_ruleset
# from .sub_resource_collections import py_to_bl_ruleset as py_to_bl_subrescol_ruleset
# from .resources import py_to_bl_ruleset as py_to_bl_res_ruleset
# from .references import py_to_bl_ruleset as py_to_bl_ref_ruleset

BlToPyTransformer = Transformer((
    # bl_to_py_values_ruleset,
    # bl_to_py_subres_ruleset,
    # bl_to_py_subrescol_ruleset,
    # bl_to_py_res_ruleset,
    # bl_to_py_ref_ruleset,    
))

PyToBlTransformer = Transformer((
    # py_to_bl_values_ruleset,
    # py_to_bl_subres_ruleset,
    # py_to_bl_subrescol_ruleset,
    # py_to_bl_res_ruleset,
    # py_to_bl_ref_ruleset,
))