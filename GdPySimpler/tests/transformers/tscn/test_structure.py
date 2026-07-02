
from typing import Generator, Type, Any

from ....transformers.tscn import (
    gd_to_py_transformer,
    py_to_gd_transformer,
    GdToPyContext,
    PyToGdContext,
)

from ....core.structure import (
    ResourceSettings,
    ResourceTres,
    ResourceScene,
    SubResource,
    SubResourceCollection,
    Node,
    NodeCollection,
    Category,
    CategoryCollection,
    ExtReference,
    ExtReferenceCollection,
    EditFlag,
    EditFlagCollection,
    GdType,
    GdTypeValueSet,
    Signal,
    SignalCollection,
)

_parser_cache = {}
def make_parser_cached(self, key):
    if res:=_parser_cache.get(key,None):
        return res
    res = make_parser(key)
    _parser_cache[key] = res
    return res

class _StructureTest[T:Type]():
    _type : Type[T]
    _parser_key : str

    def data(self,)->Generator[str,T]:
        raise NotImplementedError()
        yield

    def _yield_gd_to_py(self,):
        for txt, obj in self.data():
            parsed = make_parser_cached(self._parser_key).parse(txt)
            res = gd_to_py_transformer.transform_tree(self.make_gdtopy_context(),parsed)
            yield obj, res

    def _yield_py_to_gd(self,):
        for txt, obj in self.data():
            parsed = make_parser_cached(self._parser_key).parse(txt)
            res = py_to_gd_transformer.transform_tree(self.make_pytogd_context(), obj)
            yield txt, res
    
    def test_py_to_gd(self,):
        for a,b in self._yield_py_to_gd():
            self.py_compare(a,b)
    
    def test_gd_to_py(self,):
        for a,b in self._yield_py_to_gd():
            self.gd_compare(a,b)
    
    def make_pytogd_context(self,)->PyToGdContext:
        return PyToGdContext()

    def make_gdtopy_context(self,)->GdToPyContext:
        return GdToPyContext()

    def py_compare(self, a:T, b:T):
        assert (isinstance(a, self._type))
        assert (a == b)

    def gd_compare(self, a:str, b:str):
        assert(a.replace("/n","").replace(" ","") == b.replace("/n","").replace(" ",""))


class Test_ResourceSettings(_StructureTest):
    ...

class Test_ResourceTres(_StructureTest):
    ...

class Test_ResourceScene(_StructureTest):
    ...

class Test_SubResource(_StructureTest):
    ...

class Test_SubResourceCollection(_StructureTest):
    ...

class Test_Node(_StructureTest):
    ...

class Test_NodeCollection(_StructureTest):
    ...

class Test_Category(_StructureTest):
    ...

class Test_CategoryCollection(_StructureTest):
    ...

class Test_ExtReference(_StructureTest):
    ...

class Test_ExtReferenceCollection(_StructureTest):
    ...

class Test_EditFlag(_StructureTest):
    ...

class Test_EditFlagCollection(_StructureTest):
    ...

class Test_GdType(_StructureTest):
    ...

class Test_GdTypeValueSet(_StructureTest):
    ...

class Test_Signal(_StructureTest):
    ...

class Test_SignalCollection(_StructureTest):
    ...
