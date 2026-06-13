from .core.primitives import Context, MultiKeyCollection
from .sub_resources import *
from .core import GdType
import random
import string

from typing import Any


class _CollectionSubResource[T:_SubResource](GdType, MultiKeyCollection): #type:ignore
    @classmethod
    def parse_lark(cls, key, tscn, *children:T):
        self = cls()
        self.extend(children)
        return self

    def _assign_unique_key(self, p_key, s_key, item):
        setattr(item, p_key, s_key)

    def _generate_unique_key(self, di, p_key, s_key, item):
        n_key = s_key
        if n_key in (ks:=di.keys()):
            i = 0
            while n_key in ks:
                i = i+1
                n_key = self._generate_missing_secondary_key(p_key,item)
                if n_key is None:
                    raise Exception("Generated key cannot be None!")
                if i > 50:
                    raise Exception("Unique key not generating in scope!", tuple(di.keys()), n_key)
                if not (n_key in ks):
                    break

        return n_key
    
    def get_struct_children(self,)->tuple[GdType]:
        return tuple(self._items)

class CollectionNodeRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = ("unique_id",)
    _get_default_key = "unique_id"
    
    root : T = None

    @classmethod
    def lark_keys(cls):
        return ("node_resources",)
    
    def _generate_missing_secondary_key(self, p_key, item):
        return random.randint(1, 10000000)
    
    def build_tree(self, c:Context)->list[T]:
        """ Build tree from Node.parent namespace 
        return items that failed to attach to the tree correctly and were placed at the root 
        """
        ## TODO: Secondary trees imported & attached
        ## FEATURE_SET: Tree matcher 

        t_namespace = {}
        root : T = None
        hanging = []

        for n in self._items:
            if n.parent is None:
                assert(root is None)
                root = n
                t_namespace["."] = n
                continue
            if n.parent == ".":
                path = n.name
            else:
                path = f"{n.parent}/{n.name}"
            
            assert(not (path in t_namespace.keys()))
            t_namespace[path] = n
        
        if root is None:
            raise LookupError("Could not determine root!")
        
        self.root = root

        for n in self._items:
            if n.parent is None:
                assert(n is root)
                continue
            if n.parent in t_namespace.keys():
                t_namespace[n.parent].add_child(n)
            else:
                n.name = f"{n.parent}/{n.name}"
                root.add_child(n)
                hanging.append(n)

        return hanging
        

class CollectionExtRes[T:SubResourceExt](_CollectionSubResource):
    _unique_keys = ("uid", "id")
    _get_default_key = "id"
    
    @classmethod
    def lark_keys(cls):
        return ("ext_resources",)

    def _generate_missing_secondary_key(self, p_key, item):
        if p_key == "id":
            return "Resource_" + "".join(random.choice(string.ascii_letters, string.digits) for i in range(5))
        elif p_key == "uid":
            return None ## This key is descriptive! 
        else:
            raise KeyError("")
        
    def _key_matcher(self, key):
        if isinstance(key, str):
            if key.startswith("uid://"):
                return ("uid",key)
            else:
                return ("id", key)
        return super()._key_matcher(key)


class CollectionEditRes[T:SubResourceEdit](_CollectionSubResource):
    _unique_keys = tuple()
    @classmethod
    def lark_keys(cls):
        return ("edit_resources",)

class CollectionSubRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = ("id",)
    _get_default_key = "id"
    @classmethod
    def lark_keys(cls):
        return ("sub_resources",)

    def _generate_missing_secondary_key(self, p_key, item):
        return "Resource_" + "".join(random.choice(string.ascii_letters, string.digits) for i in range(5))


class CollectionCatRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = ("name",)
    @classmethod
    def lark_keys(cls):
        return ("cat_resources",)

_all = (
    CollectionNodeRes,
    CollectionExtRes,
    CollectionEditRes,
    CollectionSubRes,
    CollectionCatRes,
)