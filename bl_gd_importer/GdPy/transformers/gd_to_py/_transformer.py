from ...core.transformer import Transformer, TransformerSet, Session
from typing import Iterable, Any, Type

from inspect import isclass

from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )


class GdToPy_Session(Session):
    def __init__(self, transformer_sets):
        self.preproc_hashes = {}
        super().__init__(transformer_sets)

    get_id = hash
    
class GdToPy_TransformerSet(TransformerSet): ...

class GdToPy_Transformer(Transformer):
    keys : Iterable[str] = tuple()
    def match(self, session:Session, node:LarkToken|LarkTree)->bool:
        if isinstance(node, LarkToken):
            return (str(node.type) in self.keys)
        if isinstance(node, LarkTree):
            return (str(node.data) in self.keys) 
        raise KeyError("Node not supported;", node)


class PyToGd_Session(Session):
    def get_id(self,node:Any):
        # from .values import Object, Dictionary, Array
        ''' provide a unique namespace for any object '''
        if isinstance(node, (str,int,float)):
            return str(node)
        elif h := getattr(node, "__hash__", None):
            return h()
        return id(node) + self.get_id_contributor_sum(node)

class PyToGd_TransformerSet(TransformerSet): ...

class PyToGd_Transformer(Transformer):
    types : Iterable[Type] = tuple()

    def __repr__(self,):
        return f"PyToGd_Transformer{self.types}"

    def match(self, session:Session, node:Any)->bool:
        for t in self.types:
            if isinstance(node, t):
                return True
        return False
        



