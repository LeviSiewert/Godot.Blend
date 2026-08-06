from contextvars import ContextVar
from .structure import _Wrapper

class _Obj():
    name : str
    def __init__(self, name:str):
        self.name = name

class Test_Wrapper():
    def test_basic():
        w = _Wrapper()
        o = _Obj("name")

        assert w._w_obj is None
        c = ContextVar("")
        w._w_filled.connect(lambda x: c.set(x))
        w._w_replace(o)

        assert c.get() is o
        assert isinstance(w, _Wrapper)
        assert isinstance(w, _Obj)
        assert w.name == "name"
