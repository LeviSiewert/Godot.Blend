# from pytest import fixture

from ..structure.standard_parser import gdparser 
from ..structure.values import *
from ..structure.references import *
from ..structure.core.primitives import Context

c = Context()
def _run(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)

def test_rid():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("rid", "RID()"), GdValueResourceID)) 