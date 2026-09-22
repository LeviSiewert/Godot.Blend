from ._transformer import GdToPyModule, PyToGdModule, GdToPyRuleset, PyToGdRuleset

from ._test_utils import _StructureTest
from ...core.defininitions import GdDefValueTyping


class Test_GdDefValueTyping(_StructureTest):
    _parser_key = "type_anno"
    def data(self):
        yield "[String,String]", GdDefValueTyping("String", "String")