from __future__ import annotations

from .transformer import Transformer, TransformerRuleset, TransformerModule, Context

class _TContext(Context):
    ...

class _Node():
    id : str
    name : str
    children : list[_Node]
    def __init__(self, id:str, name:str, children:list[_Node]=tuple()):
        self.id = id
        self.name = name
        self.children = list(children)
    def __hash__(self):
        return hash(self.id) + hash(tuple(self.children))

    def traverse(self):
        for x in self.children:
            yield from x.traverse()
        yield self

class Test_Transformer():
    def test_basic(self):
        class Module(TransformerModule):
            _keys = (_Node,)
            def transform(self, c, node:_Node):
                yield node.children.__iter__()
                n_children = c.children.get()
                n_node = _Node(node.id, node.name+"_1", n_children)
                return n_node
            
        a0 = _Node(1,"a",
            children = [
                _Node(2,"b"),
                _Node(3,"c"),
                _Node(4,"d",[
                    _Node(5,"e"),
                    _Node(6,"f"),
                ]),
            ]
        )
        
        trs = TransformerRuleset("ruleset_id", *[Module])
        t = Transformer("transfomer_id", *[trs])
        a1 = t.transform_tree(_TContext(), a0)

        assert hash(a1) == hash(a0)
        assert a1.name == (a0.name + "_1")






