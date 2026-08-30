from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule, PyToGdContext

from lark import (
    Tree as LarkTree,
    Token as LarkToken, 
)

_inf = float("inf")
_inf_neg = -float("inf")

class GdToPy_Terminals(GdToPyModule):
    _keys = ("BOOL", "NULL", "INF", "INF_NEG", "STRING", "NUMBER", "FLOAT", "WORD", None)
    def transform(self, c, node):
        if node is None:
            return None
        assert(isinstance(node, LarkToken))
        key = c.key.get()
        match key:
            case "BOOL":
                if node == "true": 
                    return True
                return False
            case "INF":
                return float("inf")
            case "INF_NEG":
                return -float("inf")
            case "STRING":
                return str(node).strip('"')
            case "NUMBER":
                return int(node)
            case "FLOAT":
                return float(node)
            case "WORD":
                return str(node)
            case "NULL":
                return None
            case _:
                raise Exception("Could not match type of node", node.type)

class PyToGd_Terminals(PyToGdModule):
    _keys = (bool,float,int,str,None)
    def transform(self, c:PyToGdContext, node):
        if isinstance(node, float):
            if node == _inf:
                return "inf"
            elif node == _inf_neg:
                return "-inf"
            return c.rendering.render_float(node)
            # return 
        if isinstance(node, bool):
            if node:
                return "true"
            return "false"
        if isinstance(node, str):
            return f'"{node}"'
        if isinstance(node, int):
            return str(node)
        if node is None:
            return "null"
        raise KeyError()

class GdToPy_Simple(GdToPyModule):
    ''' Thin objects that should still be paired with current parser
    May will be implied in refactor suppporting lalr(1) + treeless.
    '''
    _keys = ("pair", "value", "property", "resource_header", "resource_body",  "packed_2", "packed_2i", "packed_3", "packed_3i", "packed_4", "packed_4i", "packed_6", "packed_9", "packed_12")
    def transform(self, c, node):
        yield node.children
        assert(isinstance(node, LarkTree))
        key = c.key.get()
        match key:
            case "pair":
                return c.children.get()
            case "value":
                return c.children.get()[0]
            case "type_anno":
                return c.children.get()
            case "type":
                return c.children.get()[0] ## expected: Str|None
            case "property":
                return c.children.get()
            case "resource_header":
                return c.children.get()[0] ## expected: PropertiesCollection
            case "resource_body":
                return c.children.get()[0] ## expected: PropertiesCollection
        if key.startswith("packed"):
            return c.children.get()
        raise Exception("Could not match type of tree", node.type)

class PyToGd_Simple(PyToGdModule):
    ''' Atm this is not used due to behavior not needing it '''


gd_to_py_ruleset = GdToPyRuleset("STD_Terminals", *[
    GdToPy_Terminals,
    GdToPy_Simple,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Terminals", *[
    PyToGd_Terminals,
    PyToGd_Simple,

])