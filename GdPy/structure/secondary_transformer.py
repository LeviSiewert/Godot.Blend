from .core import GdType
from typing import Callable, Any, Iterable
from abc import ABC, abstractmethod
from copy import copy 

class SecondaryTransfomer[I:Any,T:Any](ABC):
    def transform_each(self, iter:Iterable, *args, **kwargs)->list:
        res = []
        for x in iter:
            res.append(self.transform(iter, *args, **kwargs))
        return res

    def __default__(self, val:GdType, children:dict[str,tuple[Any]], *args, **kwargs)->GdType:
        res = copy(val)
        res.set_struct_children(children)
        return res

    def transform(self, root:I|GdType, *args, **kwargs)->T:
        new_children : dict[str, tuple[Any]] = {}
        for k,v in root.get_struct_children():
            res = []
            for x in v:
                res.append(self.transform(x))
            new_children[k] = res
        res = self.matcher(root)(root, children = new_children, *args, **kwargs)
        return res
    
    @abstractmethod
    def matcher(self, item:GdType)->Callable:
        return self.__default__