from __future__ import annotations
from typing import Generator, Type, Any

from ._core import make_gd_to_py, make_py_to_gd
from .lark_tools import make_parser

gd_to_py = make_gd_to_py()
py_to_gd = make_py_to_gd()


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

    def data(self,session)->Generator[str,T]:
        raise NotImplementedError()

    def _yield_gd_to_py(self,)->Generator[tuple[Any,Any]]:
        for txt, obj in self.data(gd_to_py):
            parsed = make_parser_cached(self._parser_key).parse(txt)
            gd_to_py.memo.clear()         
            
            ## FOR SOME REASON id(LarkToken) is reusing/producing a non-unique ID between parsing sessions, or id() is evaluating form (not recursive content) 
            res = gd_to_py.transform(parsed)
            yield obj, res  
            

    def _yield_py_to_gd(self,)->Generator[tuple[str,str]]:
        for txt, obj in self.data(py_to_gd):
            # parsed = make_parser_cached(self._parser_key).parse(txt)
            
            ## FOR SOME REASON id(LarkToken) is reusing/producing a non-unique ID between parsing sessions, or id() is evaluating form (not recursive content) 
            py_to_gd.memo.clear()
            res = py_to_gd.transform(obj)
            
            yield txt, res
    
    def test_py_to_gd(self,):
        for a,b in self._yield_py_to_gd():
            self.gd_compare(a,b)
    
    def test_gd_to_py(self,):
        for a,b in self._yield_gd_to_py():
            self.py_compare(a,b)

    def py_compare(self, ground:T, new:T):
        assert (isinstance(new, self._type))
        if (ground != new):
            if hasattr(ground, "_dif"):
                raise Exception({k:v for k,v in ground._dif(new).items() if not v[0]})
            raise Exception("(ground != new)")
        
    def gd_compare(self, ground:str, new:str):
        g = ground.replace("\n","").replace("\t","").replace(" ","")
        n = new.replace("\n","").replace("\t","").replace(" ","")
        assert( g == n ) 