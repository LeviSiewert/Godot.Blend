from typing import Generator, Type, Any

from ._core import gd_to_py, py_to_gd
from .lark import make_parser

from ._transformer import ( GdToPyContext, PyToGdContext )

_parser_cache = {}
def make_parser_cached(key):
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

    def _yield_gd_to_py(self,)->Generator[tuple[Any,Any]]:
        for txt, obj in self.data():
            parsed = make_parser_cached(self._parser_key).parse(txt)
            res = gd_to_py.transform_tree(self.make_gdtopy_context(), parsed)
            yield obj, res

    def _yield_py_to_gd(self,)->Generator[tuple[str,str]]:
        for txt, obj in self.data():
            parsed = make_parser_cached(self._parser_key).parse(txt)
            res = py_to_gd.transform_tree(self.make_pytogd_context(), obj)
            yield txt, res
    
    def test_py_to_gd(self,):
        for a,b in self._yield_py_to_gd():
            self.gd_compare(a,b)
    
    def test_gd_to_py(self,):
        for a,b in self._yield_gd_to_py():
            self.py_compare(a,b)
    
    def make_pytogd_context(self,)->PyToGdContext:
        return PyToGdContext()

    def make_gdtopy_context(self,)->GdToPyContext:
        return GdToPyContext()

    def py_compare(self, ground:T, new:T):
        assert (isinstance(new, self._type))
        assert (ground == new)

    def gd_compare(self, ground:str, new:str):
        g = ground.replace("\n","").replace("\t","").replace(" ","")
        n = new.replace("\n","").replace("\t","").replace(" ","")
        assert( g == n ) 