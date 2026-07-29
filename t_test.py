from .t import Signal
from contextvars import ContextVar

class Test_Signal():
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
        s.t_disconnect(token)
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
        def func(res): 
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
        def func(attr,res):
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

    def test_callback(self,):
        ctx = _Context()
        c_var = ContextVar("", default=None)
        def func(attr, res):
            c_var.set(res)
        ctx.callback("a", func)
        assert c_var.get() is None
        ctx.a = "A"
        assert c_var.get() is "A"


    def test_extends_n_dif_signal(self,):
        class _UNSET():...

        ctx_a = _Context(a="A") 
        ctx_b = _Context(b="B")
        ctx_c = _Context(c="C")

        c_var = ContextVar("", default=_UNSET)
        def func(attr, res):
            c_var.set(res)
        ctx_c.callback("a", func)

        ## Basic signals:
        ctx_c.a = "C"
        assert c_var.get() == "C"

        del ctx_c.a
        assert c_var.get() is None

        ## Filter should obscure, as target of callback is "a"
        c_var.set(_UNSET)
        ctx_c.set_extends(ctx_b)
        assert c_var.get() is _UNSET


        ## Filter should call siganl via dif of existing vs incoming.
        ctx_b.set_extends(ctx_a)
        assert ctx_a.a == "A"
        assert ctx_b.a == "A"
        assert c_var.get() == "A"

        ## Ensure update of A does call as well
        ctx_a.a = "A1"
        assert c_var.get() == "A1"

        ## Ensure update of b.a does call as well
        ctx_b.a = "A2"
        assert c_var.get() == "A2"

        ## Ensure value is maintained bc no diff
        ctx_b.set_extends(None)
        assert c_var.get() == "A2"

        ## Ensure value is updated when removed
        del ctx_b.a
        assert c_var.get() is None

        ## Value would not be changed here
        ctx_b.a = "A3"
        assert ctx_c.a == "A3" 
        assert c_var.get() == "A3"
        
        ctx_c.set_extends(None)
        assert ctx_c.a is None 
        assert c_var.get() is None

    def test_extends_callback_timing(self,):
        ctx_a = _Context(a="A") 
        ctx_b = _Context(a="B")
        ctx_c = _Context(a="C")
        ctx_b.set_extends(ctx_a)
        ctx_c.set_extends(ctx_b)

        def fail(attr,val):
            raise Exception()
        def good(attr,val):
            pass
        ctx_c.callback("a",good)
        ctx_c.callback("b",fail)
        ctx_c.callback("c",fail)
        ctx_c.set_extends(None)
        

from .t import Collection

class Test_Collection():
    ...
