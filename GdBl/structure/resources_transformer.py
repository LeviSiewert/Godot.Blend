from .core.tranformer_base import BlToPy, BlToPyRuleset
from .core.tranformer_base import PyToBl, PyToBlRuleset

py_to_bl_ruleset = BlToPyRuleset(__file__,tuple())
bl_to_py_ruleset = PyToBlRuleset(__file__,tuple())