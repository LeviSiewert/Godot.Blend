from .core import GdParser
from .values import _all as all_values
from .resources import _all as all_res
from .sub_resources import _all as all_subres
from .sub_resource_collections import _all as all_rescol
from .references import _all as all_referencers
from ..resources import grammer
gdparser = GdParser(grammer, (*all_res,*all_subres,*all_rescol,*all_values,*all_referencers))
