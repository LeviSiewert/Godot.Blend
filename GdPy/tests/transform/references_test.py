from ..structure.references import *

from ..structure.core.primitives import Context
from ..structure._standard_parser import construct_keyed_parser
gdparser = construct_keyed_parser("value")

c = Context()
def _parse(key:str, txt:str):
    return gdparser.parse(c,txt,start=key)
def _render(object):
    return gdparser.render(c,object)

class TestGdValueResourceID():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "rid"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", "RID()"), GdValueResourceID)) 
        assert(_parse("value", "RID()") == GdValueResourceID())
        assert(_parse("value", 'RID("")') == GdValueResourceID())
        assert(_parse("value", 'RID("ID")') == GdValueResourceID("ID"))
    def test_rendering(self,):
        assert("RID()" == _render(GdValueResourceID()))
        assert('RID("ID")' == _render(GdValueResourceID("ID")))

class TestGdValueExtResource():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "extresource"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", 'ExtResource()'), GdValueExtResource))
        assert(isinstance(_parse("value", 'ExtResource("")'), GdValueExtResource))
        assert(_parse("value", 'ExtResource()') == GdValueExtResource())
        assert(_parse("value", 'ExtResource("")') == GdValueExtResource())
        assert(_parse("value", 'ExtResource("ID")') == GdValueExtResource("ID"))
    def test_rendering(self,):
        assert('ExtResource()' == _render(GdValueExtResource()))
        assert('ExtResource("ID")' == _render(GdValueExtResource("ID")))
        

class TestGdValueNodePath():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "nodepath"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", 'NodePath()'), GdValueNodePath))
        assert(isinstance(_parse("value", 'NodePath("")'), GdValueNodePath))
        assert(_parse("value", 'NodePath()') == GdValueNodePath())
        assert(_parse("value", 'NodePath("")') == GdValueNodePath())
        assert(_parse("value", 'NodePath("ID")') == GdValueNodePath("ID"))
    def test_rendering(self,):
        assert('NodePath()' == _render(GdValueNodePath()))
        assert('NodePath("ID")' == _render(GdValueNodePath("ID")))

class TestGdValueSubResource():
    def test_in_matcher(self,):
        assert(gdparser._parser_transformer.matcher(None, "subresource"))
    def test_parsing(self,):
        assert(isinstance(_parse("value", 'SubResource()'), GdValueSubResource))
        assert(isinstance(_parse("value", 'SubResource("")'), GdValueSubResource))
        assert(isinstance(_parse("value", 'SubResource("ID")'), GdValueSubResource))
        assert(_parse("value", 'SubResource()') ==  GdValueSubResource())
        assert(_parse("value", 'SubResource("")') ==  GdValueSubResource())
        assert(_parse("value", 'SubResource("ID")') ==  GdValueSubResource("ID"))
    def test_rendering(self,):
        assert('SubResource()' ==  _render(GdValueSubResource()))
        assert('SubResource("ID")' ==  _render(GdValueSubResource("ID")))