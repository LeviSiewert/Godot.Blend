from .core import GdParser
from .resources import _all as all_resources
from .values import _all as all_values
from ..resources import grammer
gdparser = GdParser(grammer, all_resources|all_values)

