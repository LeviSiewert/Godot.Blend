from .core.primitives import Collection
from .sub_resources import *
from .core import GdType

class _CollectionSubResource[T:_SubResource](GdType, Collection): #type:ignore
    @classmethod
    def parse_lark(cls, key, tscn, *children:T):
        self = cls()
        self.extend(children)
        return self
    
    def get_struct_children(self):
        return self.__iter__()

class CollectionNodeRes[T:SubResourceNode](GdType, _CollectionSubResource):
    @classmethod
    def lark_keys(cls):
        return ("node_resources",)

class CollectionExtRes[T:SubResourceExt](GdType, _CollectionSubResource):
    @classmethod
    def lark_keys(cls):
        return ("ext_resources",)

class CollectionEditRes[T:SubResourceEdit](GdType, _CollectionSubResource):
    @classmethod
    def lark_keys(cls):
        return ("edit_resources",)

class CollectionSubRes[T:SubResourceNode](GdType, _CollectionSubResource):
    @classmethod
    def lark_keys(cls):
        return ("sub_resources",)

class CollectionCatRes[T:SubResourceNode](GdType, _CollectionSubResource):
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