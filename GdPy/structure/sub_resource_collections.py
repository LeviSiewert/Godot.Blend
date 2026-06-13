from .core.primitives import MultiKeyCollection
from .sub_resources import *
from .core import GdType


from typing import Any


class _CollectionSubResource[T:_SubResource](GdType, MultiKeyCollection): #type:ignore
    @classmethod
    def parse_lark(cls, key, tscn, *children:T):
        self = cls()
        self.extend(children)
        return self

class CollectionNodeRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = tuple("id",)
    @classmethod
    def lark_keys(cls):
        return ("node_resources",)

class CollectionExtRes[T:SubResourceExt](_CollectionSubResource):
    _unique_keys = tuple("uid", "id")
    @classmethod
    def lark_keys(cls):
        return ("ext_resources",)

class CollectionEditRes[T:SubResourceEdit](_CollectionSubResource):
    _unique_keys = tuple()
    @classmethod
    def lark_keys(cls):
        return ("edit_resources",)

class CollectionSubRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = tuple("unique_id",)
    @classmethod
    def lark_keys(cls):
        return ("sub_resources",)

class CollectionCatRes[T:SubResourceNode](_CollectionSubResource):
    _unique_keys = tuple("name",)
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