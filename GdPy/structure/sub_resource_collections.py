from .core.primitives import MultiKeyCollection
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

    def _assign_unique_key(self, di, p_key, s_key, item):
        ## TODO: Replace with int w/ len 9
        setattr(item, p_key, s_key)

    def _generate_unique_key(self, di, p_key, s_key, item):
        n_key = s_key
        while n_key in di.keys():
            n_key = self._generate_unique_key(p_key,s_key,item)
        return n_key

class CollectionNodeRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = ("unique_id",)
    _get_default_key = "unique_id"
    @classmethod
    def lark_keys(cls):
        return ("node_resources",)
    
    def _generate_missing_secondary_key(self, p_key, item):
        r = 9
        return random.randint(10^(r-1), (10^r)-1)

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