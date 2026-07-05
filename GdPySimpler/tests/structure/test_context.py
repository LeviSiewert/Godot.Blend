from contextvars import ContextVar

from ...core.context import StructContext as _StructContext


class Test_Context():
    def get_abc(self):
        class Context(_StructContext):
            _slots_ = ("slot_a", "slot_b", "slot_c")
        
        context_a = Context()
        context_b = Context(extends=context_a)
        context_c = Context(extends=context_b)
        return context_a, context_b, context_c
    def test_basic_extension(self,):

        context_a, context_b, context_c = self.get_abc()

        context_a.slot_a = "val_a"
        assert (context_b.slot_a == "val_a")
        assert (context_c.slot_a == "val_a")

        context_b.slot_a = "val_a1"
        assert (context_a.slot_a == "val_a")
        assert (context_b.slot_a == "val_a1")
        assert (context_c.slot_a == "val_a1")

        delattr(context_b, "slot_a")
        assert (context_b.slot_a == "val_a")
        assert (context_c.slot_a == "val_a")
    
    def test_basic_callback(self):
        context_a, context_b, context_c = self.get_abc()
        
        class _UNSET(): pass
        endpoint = ContextVar("Assertion", default=_UNSET)

        endpoint.set([])
        context_c.callback("slot_a", once=False, local_only=True, callback=lambda val: endpoint.get().append(val) )
        context_c.callback("slot_b", once=False, local_only=True, callback=lambda val: endpoint.get().append(val) )
        context_c.callback("slot_c", once=False, local_only=True, callback=lambda val: endpoint.get().append(val) )

        context_c.slot_a = "val_a"
        assert endpoint.get()==["val_a"]
        context_c.slot_b = "val_b"
        assert endpoint.get()==["val_a","val_b"]
        context_c.slot_c = "val_c"
        assert endpoint.get()==["val_a","val_b","val_c"]
        context_c.slot_a = "val_a"
        assert endpoint.get()==["val_a","val_b","val_c","val_a"]

        ## SINCE LOCAL ONLY: 
        context_b.slot_a = "val_a1"
        assert endpoint.get()==["val_a","val_b","val_c","val_a"]

        context_a.slot_a = "val_a1"
        assert endpoint.get()==["val_a","val_b","val_c","val_a"]

    def test_nested_callback(self,):
        context_a, context_b, context_c = self.get_abc()

        endpoint = ContextVar("Assertion", default=None)
        
        context_c.callback("slot_a", once=True, local_only=False, callback=lambda val: endpoint.set(val))
        context_b.slot_a = "val_a"
        assert endpoint.get() == "val_a"

        context_c.callback("slot_a", once=True, local_only=False, callback=lambda val: endpoint.set(val))
        context_a.slot_a = "val_a1"
        assert endpoint.get() == "val_a1"