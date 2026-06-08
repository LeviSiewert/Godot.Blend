from .core import GdParser
from .values import _all as all_values
from .resources import _all as all_resources
from .references import _all as all_referencers
from ..resources import grammer
gdparser = GdParser(grammer, (*all_resources,*all_values,*all_referencers))
