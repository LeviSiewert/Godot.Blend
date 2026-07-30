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
        
from .t import Collection, CollectionKey, _Wrapper

class _Item():
    key = CollectionKey()
    def __init__(self, key:None|str):
        self.key = CollectionKey(self, key)

class Test_Collections():
    def test_construction(self,):
        c = Collection("key", None)

    def test_append(self):
        c = Collection("key", None)
        i = _Item("key")
        c.append(i)
        r = c["key"]

        assert len(c) == 1
        assert isinstance(r, _Wrapper)
        assert r._w_obj is i
        assert c[r] == c[i]
        assert c[r] == "key"

    def test_remove(self):
        c = Collection("key", None)
        i = _Item("key")
        c.append(i)
        r = c["key"]

        del c["key"]
        assert len(c) == 0

    def test_promise(self):
        c = Collection("key", None)
        i = _Item("key")
        r = c.append_promise("key")

        assert c["key"] is r
        assert isinstance(r, _Wrapper)
        assert r._w_obj is None

        c.append(i)
        assert r._w_obj is i

    def test_collision_rightprio(self):
        c = Collection("key", None)
        i1 = _Item("key")
        i2 = _Item("key")
        c.append(i1)
        c.append(i2, key_priority=True)

        assert i1.key.key != "key"
        assert c[i1.key.key] is i1

        assert i2.key.key == "key"
        assert c[i2.key.key] is i2

    def test_collision_leftprio(self):
        c = Collection("key", None)
        i1 = _Item("key")
        i2 = _Item("key")
        c.append(i1)
        c.append(i2, key_priority=False)

        assert i1.key.key == "key"
        assert c[i1.key.key] is i1

        assert i2.key.key != "key"
        assert c[i2.key.key] is i2

    def test_rename_via_col(self):
        c = Collection("key", None)
        i = _Item("key")
        c.append(i)

        c.rename("key", "yek")

        assert i.key.key == "yek"
        assert c["yek"] is i
        assert c.get("yek", None) is None

    def test_rename_via_key(self):
        c = Collection("key", None)
        i = _Item("key")
        c.append(i)

        i.key.key = "yek"

        assert i.key.key == "yek"
        assert c["yek"] is i
        assert c.get("yek", None) is None




# from .t import Collection, CollectionKey, CollectionRef
# class _Item():
#     context : Context
#     key : CollectionKey[str]
#     def __init__(self, key):
#         self.context = Context()
#         self.key = CollectionKey()

# class Test_Collection():
#     def test_construction(self):
#         c = Collection(None, _Item, "key", False)

#     def test_add_rem(self):
#         c = Collection(None, _Item, "key", False)
#         i = _Item("key")
#         c.append(i)

#         assert c._inverse[i] == "key"
#         assert c.data["key"] is i

#         assert len(c) == 1
#         assert c["key"] is i
#         assert c.get("key") is i
#         assert i.key.col is c

#         c.remove(i)
#         assert c.get("key",None) is None
#         assert i.key.col is None
#         assert len(c) == 0

#     def test_key_change(self):
#         c = Collection(None, _Item, "key", False)
#         i = _Item("key")
#         c.append(i)
#         i.key.set("yek")
#         assert i.key.key == "yek"
#         assert c["yek"] is i
#         assert c.get("key",None) is None

#     def test_add_signal(self):
#         c = Collection(None, _Item, "key", False)
#         i = _Item("key")
#         t_var = ContextVar("", default=None)

#         c.item_created.connect(func)
#         def func(k,v):
#             t_var.set((k,v))
#         c.append(i)
#         assert t_var.get() == ("key", i)

#     def test_rem_signal(self):
#         c = Collection(None, _Item, "key", False)
#         i = _Item("key")
#         t_var = ContextVar("", default=None)

#         c.item_removed.connect(func)
#         def func(k,v):
#             t_var.set((k,v))
#         c.append(i)
#         assert t_var.get() is None
#         c.remove(i)
#         assert t_var.get() == ("key", i)

#     def test_key_change_signals(self):
#         c = Collection(None, _Item, "key", False)
#         i = _Item("key")
#         t_var = ContextVar("", default=None)

#         c.item_changed.connect(func)
#         def func(k,v):
#             t_var.set((k,v))
#         c.append(i)
#         assert t_var.get() is None
#         i.key.set("yek")
#         assert t_var.get() == ("yek", i)

#     def test_add_rem_context(self):
#         c = Collection(None, _Item, "key", True)
#         i = _Item("key")

#         c.append(i)
#         assert i.context._extends is c.context

#         c.remove(i)
#         assert i.context._extends is c.context

#     def test_set_item_unique_id(self):
#         c = Collection(None, _Item, "key", False)
#         i1 = _Item("key_1")
#         i2 = _Item("key_2")
#         c.append(i1)
#         c.append(i2)
#         assert c["key_1"] is i1
#         assert c["key_2"] is i2

#     def test_append_item_shared_id(self):
#         c = Collection(None, _Item, "key", False)
#         i1 = _Item("key_1")
#         i2 = _Item("key_1")
#         i3 = _Item("key_1")

#         c.append(i1)
#         c.append(i2, right_key_priority=True)
#         assert i1.key != "key_1"
#         assert i2.key == "key_1"

#         c.append(i3, right_key_priority=False)
#         assert i2.key == "key_1"
#         assert i3.key != "key_1"
        

#     def test_add_change_rem_refs(self):
#         c = Collection(None, _Item, "key", False)
#         i = _Item("key")
#         c.append(i)

#         ## Loose ref, no collection
#         ref = CollectionRef("key")
#         assert ref() is None

#         ## Tied ref, collection set and find by key
#         ref.set_col(c)
#         assert ref() is i
#         assert ref.key is "key"

#         ## Key of target object changes, reflect in reference
#         i.key.set("yek")
#         assert ref.key is "yek"
#         assert ref() is i

#         ## Itme removed from collection, keep in cached, keep key
#         c.remove(i)
#         assert ref() is None
#         assert ref.key is "yek"
#         assert ref.cached() is i

#         ## Change key of item, re-append, reattach reference from cached:
#         i.key.set("key_2")
#         c.append(i)
#         assert ref() is i
#         assert ref.key is "key_2"


#     def test_replace_refs(self):
#         ''' Wack ass reference system '''
#         c = Collection(None, _Item, "key", False)
#         i1 = _Item("key_1")
#         i2 = _Item("key_2")
#         c.append(i1)
#         c.append(i2)

#         ref = CollectionRef("key_1", col = c)
#         assert ref() is i1

#         c.update_ref_byitem(i1, "key_2")
#         assert ref() is i2

#         c.update_ref_bykey("key_2", i1)
#         assert ref() is i1
