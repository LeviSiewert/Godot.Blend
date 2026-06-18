from ...structure.values import *
from ...structure.sub_resources import *

from ...structure.core.primitives import Context
from ...structure._standard_parser import construct_keyed_parser
gdparser = construct_keyed_parser("sub_resource")

c = Context()
def _parse(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)
def _render(object):
    return gdparser.render(c,object)

def test_err():
    raise NotImplementedError("TODO: Test parsing & rendering")

# class TestGdValueResourceID():
#     def test_in_matcher(self,):
#         assert(gdparser._parser_transformer.matcher(None, "rid"))
#     def test_parsing(self,):
#         assert(isinstance(_parse("value", "RID()"), GdValueResourceID)) 
#         assert(_parse("value", "RID()") == GdValueResourceID())
#         assert(_parse("value", 'RID("")') == GdValueResourceID())
#         assert(_parse("value", 'RID("ID")') == GdValueResourceID("ID"))
#     def test_rendering(self,):
#         assert("RID()" == _render(GdValueResourceID()))
#         assert('RID("ID")' == _render(GdValueResourceID("ID")))
