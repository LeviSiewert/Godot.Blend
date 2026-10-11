from .signals import Signal
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
        
    def test_once(self,):
        s = Signal(self)
        t_val = ContextVar("", default=None)
        def func(res): 
            t_val.set(res)
        t_val = ContextVar("", default=None)
        s.connect(func, once=True)
        s(1)
        assert t_val.get() == 1
        s(2)
        assert t_val.get() == 1