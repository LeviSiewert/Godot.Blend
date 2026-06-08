# from pytest import fixture

from ..structure.standard_parser import gdparser 
from ..structure.values import *
from ..structure.references import *
from ..structure.core.primitives import Context

c = Context()
def _run(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)

def test_GdValueResourceID():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", "RID()"), GdValueResourceID)) 
def test_GdValueExtResource():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", 'ExtResource("")'), GdValueExtResource))
def test_GdValueNodePath():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", 'NodePath(".")'), GdValueNodePath))
def test_GdValueSubResource():
    assert(hasattr(gdparser._transformer,"rid"))
    assert(isinstance(_run("value", "SubResource()"), GdValueSubResource))