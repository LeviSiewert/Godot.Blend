
from .core import Transformer
from . import files
from . import resources
from . import sub_resources
from . import properties
from . import values

transformer = Transformer(defaults = (*files._all, *resources._all, *sub_resources._all, *properties._all, *values._all))