''' This test is to see if "streamed" parsing with LALR is in some way compatible with the (Transformer-Generator) methodology
This MAY not be strictly possible, but at-oppertunity leaf conversion through defered until middle-indexed may be??? 

Test is done with simple nested...

Result:
As far as I can tell, it would not be that much more effecient, as each non-terminal node will produce a generator instead of a value.
I may be wrong, but it's also a difficult problem to test simply atm.

In the future I may return to test further, using an interface to start conversion treeless, return the original node (essentially forwarding the children tree/tokens), then re-quiery the session via yield TRANFORM w/a
However that re-query partially defeats the *point* and any effeciencies will probably be overshadowed by the ineffeciency of searching the session.

'''

from ....core.transformer import Transformer, TransformerSet, Session, TRANSFORM_CHILDREN, STEP
from lark import (Lark, 
    Tree as LarkTree, 
    Token as LarkToken
)
from typing import Iterable

## grammer from https://lark-parser.readthedocs.io/en/latest/json_tutorial.html
grammer = r"""
    ?value: dict
          | list
          | _string
          | _number
          | "true"             -> true
          | "false"            -> false
          | "null"             -> null

    list : "[" [value ("," value)*]* "]"

    dict : "{" [pair ("," pair)*]* "}"
    pair : _string ":" value

    _string : ESCAPED_STRING
    _number : SIGNED_NUMBER
    
    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""

from json import dumps

base_truth = {
    "A" : {},
    "B" : {
        "B2" : {
            "B3" : None,
        },
    },
    "C" : 0,
    "D" : 0.0,
    "E" : "String",
    "F" : False,
    "G" : True,
    "H" : [],
    "I" : [
        {
            "B3" : None,
        },
        0,
        0.0,
        "String",
        False,
        True,
        [],
    ],
 }
base_truth_json = dumps(base_truth)


class Utils:
    ''' Quick n Dirty transformer '''

    class _Transformer(Transformer):
        keys : Iterable[str] = tuple()
        def match(self, session, node):
            if isinstance(node, LarkToken):
                return (str(node.type) in self.keys)
            if isinstance(node, LarkTree):
                return (str(node.data) in self.keys)
            return False

    class _list(_Transformer):
        keys = ["list"]
        def transform(self, session, node):
            res = yield TRANSFORM_CHILDREN(node.children)
            return list(res)
    class _dict(_Transformer):
        keys = ["dict"]
        def transform(self, session, node):
            res = yield TRANSFORM_CHILDREN(node.children)
            return dict(res)
    class _pair(_Transformer):
        keys = ["pair"]
        def transform(self, session, node):
            res = yield TRANSFORM_CHILDREN(node.children)
            return (res[0], res[1])

    class _str(_Transformer):
        keys = ["ESCAPED_STRING"]
        def transform(self, session, node:LarkTree):
            return str(node.value).strip('"')
    class _number(_Transformer):
        keys = ["SIGNED_NUMBER"]
        def transform(self, session, node:LarkTree):
            return float(node.value)
    class _bool(_Transformer):
        keys = ["true","false"]
        def transform(self, session, node:LarkTree):
            return node.data == "true"
    class _null(_Transformer):
        keys = ["null"]
        def transform(self, session, node):
            return None

    @classmethod
    def make_session(cls):
        return Session([TransformerSet("JSON", [ cls._list, cls._dict, cls._pair, cls._str, cls._number, cls._bool, cls._null ])])

def test_basic_treefull():
    tree = Lark(grammer, start='value', parser='lalr').parse(base_truth_json)
    session = Utils.make_session()
    result = session.transform(tree)
    assert result == base_truth

# def test_basic_treeless():
#     session = make_session()
#     class transformer_interface():
#         def __getattribute__ (self, name):
#             if not name.startswith("__"):
#                 raise Exception(name)
#             return session.name

#     result = Lark(grammer, start='value', parser='lalr', transformer = transformer_interface()).parse(base_truth_json)
#     assert result == base_truth



# parser_treefull = Lark(grammer, start='value', parser='lalr')
# # parser_treeless = Lark(grammer, start='value', parser='lalr', transformer=TreeToJson())
