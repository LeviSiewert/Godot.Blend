from ...core.transformer import Transformer, TransformerSet, Session
from typing import Iterable, Any, Type

from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )


GdToPy_Session = Session

GdToPy_TransformerSet = TransformerSet

class GdToPy_Transformer(Transformer):
    keys : Iterable[str] = tuple()

    def match(self, session:Session, node:LarkToken|LarkTree)->bool:
        if isinstance(node, LarkToken):
            return (str(node.type) in self.keys)
        if isinstance(node, LarkTree):
            return (str(node.data) in self.keys) 
        raise KeyError("Node not supported;", node)


PyToGd_Session = Session

PyToGd_TransformerSet = TransformerSet

class PyToGd_Transformer(Transformer):
    types : Iterable[Type]

    def __repr__(self,):
        return f"PyToGd_Transformer{self.types}"

    def match(self, session:Session, node:Any)->bool:
        for t in self.types:
            if isinstance(node, t):
                return True
        return False



