from .core import GdType
from typing import Callable, Any
from abc import ABC, abstractmethod
from copy import copy 

class SecondaryTransfomer[I:Any,T:Any](ABC):
    def __default__(self, val:GdType)->GdType:
        return val

    def transform(self, root:I|GdType, split_tree:bool=True)->T:
        for k,v in root.get_struct_children():
            res = []
            for x in v:
                res.append(self.transform(x, split_tree))
            root.set_struct_children(k,res)
        res = self.matcher(root)(root)
        if (res is root) and split_tree:
            res = copy(root)
        return res
    
    @abstractmethod
    def matcher(self, item:GdType)->Callable:
        pass