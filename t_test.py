from .t import Signal
from contextvars import ContextVar

class test_signal():
    def test_connection(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(res): 
            t_val.set(res)
        token = s.connect(func)
        assert len(s.subscribers) == 1

    def test_disconnect(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(res): 
            t_val.set(res)
        token = s.connect(func)
        assert len(s.subscribers) == 1
        s.disconnect(func)
        assert len(s.subscribers) == 0

    def test_token_discon(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(res): 
            t_val.set(res)
        token = s.connect(func)
        assert len(s.subscribers) == 1
        s.disconnect(token)
        assert len(s.subscribers) == 0

    def test_emit(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(res): 
            t_val.set(res)
        s.connect(func)
        s(True)
        assert t_val.get() == True

    def test_filter(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(res): 
            t_val.set(res)
        s.connect(func, filter=lambda x: x != False)
        s(True)
        assert t_val.get() == True
        s(False)
        assert t_val.get() == True
        s("value")
        assert t_val.get() == "value"
        
    def test_prepend_source(self,):
        s = Signal(self)
        def func(src, res): 
            assert (src is self)
        s.connect(func, prepend_source=True)
        s(True)

    def test_prepend_signal(self,):
        s = Signal(self)
        def func(signal, res): 
            assert (signal is s)
        s.connect(func, prepend_signal=True)
        s(True)
        
    def test_once_only(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(src, res): 
            t_val.set(res)
        t_val = ContextVar("", default=None)
        s.connect(func, once_only=True)
        s(1)
        assert t_val.get() == 1
        s(2)
        assert t_val.get() == 1

from .t import Context

class _Context(Context):
    _slots_ = ("a","b","c")

class Test_Context():

    def test_construction(self):
        ctx = _Context(a="A")
        assert ctx.a == "A"

    def test_extends_1(self,):
        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_b.set_extends(ctx_a)

        assert ctx_b._extends is ctx_a

        assert ctx_a.a == "A"
        assert ctx_b.a == "A"

        assert ctx_a.b is None
        assert ctx_b.b == "B"

    def test_extends_1_remove(self,):
        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_b.set_extends(ctx_a)

        assert ctx_b.a == "A"
        ctx_b.set_extends(None)
        assert ctx_b.a is None

    def test_extends_1_dif_signal(self,):
        c_var = ContextVar("", default=None)
        def func(res):
            c_var.set(res)

        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_b.callback("a", func)

        ctx_b.set_extends(ctx_a)
        assert c_var.get() == "A"

        ctx_a.a = "A1"
        assert c_var.get() == "A1"

        ctx_b.set_extends(None)
        assert c_var.get() is None

    def test_extends_n(self,):
        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_c = _Context(c="C")
        ctx_b.set_extends(ctx_a)
        ctx_c.set_extends(ctx_b)

        assert ctx_c._extends is ctx_b
        assert ctx_c.a == "A"
        assert ctx_c.b == "B"


    def test_extends_n_remove(self,):
        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_c = _Context(c="C")
        ctx_b.set_extends(ctx_a)
        ctx_c.set_extends(ctx_b)

        assert ctx_b.a == "A"
        assert ctx_c.a == "A"
        ctx_b.set_extends(None)
        assert ctx_b.a is None
        assert ctx_c.a is None

        ctx_c.set_extends(None)
        assert ctx_c.b is None

    def test_extends_n_dif_signal(self,):
        class _UNSET():...
        c_var = ContextVar("", default=_UNSET)
        def func(res):
            c_var.set(res)

        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_c = _Context(c="C")

        ctx_c.callback("a", func)

        ctx_c.set_extends(ctx_b)
        assert c_var.get() is _UNSET

        ctx_b.set_extends(ctx_a)
        assert c_var.get() == "A"

        ctx_a.a = "A1"
        assert c_var.get() == "A1"

        ctx_b.a = "A2"
        assert c_var.get() == "A2"
        c_var.set(_UNSET)

        ctx_b.set_extends(None)
        assert c_var.get() is _UNSET

        del ctx_b.a
        assert c_var.get() is None

        ctx_c.set_extends(None)
        assert c_var.get() is None


from .t import Collection

class Test_Collection():
    ...
