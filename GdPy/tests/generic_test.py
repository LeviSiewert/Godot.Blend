from ..structure.generic import GdObject

from ..structure.core.primitives import Context
from ..structure._standard_parser import construct_keyed_parser
gdparser = construct_keyed_parser("value")

c = Context()
def _parse(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)
def _render(object):
    return gdparser.render(c,object)

class TestGdObject():
    def test_in_matcher(self, ):
        assert(gdparser._parser_transformer.matcher(None,  "object" ))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "Object(type)"), GdObject))
        assert(_parse("value","Object(type)") == GdObject("type"))
        assert(_parse("value",'Object(type, "key":"value")') == GdObject("type", **{"key":"value"}))
        val = _parse("value",'Object(type, "key":"value")')
        assert(val.properties["key"] == "value")
    def test_rendering(self,):
        assert("Object(type)") == _render(GdObject("type"))
        assert('Object(type, "key":"value")' == _render(GdObject("type", **{"key":"value"})))