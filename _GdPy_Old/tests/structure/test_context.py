from contextvars import ContextVar

from ...core.context import StructContext as _StructContext


class Test_Context():
    def get_abc(self):
        class Context(_StructContext):
            _slots_ = ("slot_a", "slot_b", "slot_c")
        
        context_a = Context()
        context_b = Context(extends=context_a)
        context_c = Context(extends=context_b)
        context_d = Context()
        return context_a, context_b, context_c, context_d
    def test_basic_extension(self,):

        context_a, context_b, context_c, context_d = self.get_abc()

        context_a.slot_a = "val_a"
        assert (context_b.slot_a == "val_a")
        assert (context_c.slot_a == "val_a")
        assert (context_d.slot_a is None)

        context_b.slot_a = "val_a1"
        assert (context_a.slot_a == "val_a")
        assert (context_b.slot_a == "val_a1")
        assert (context_c.slot_a == "val_a1")
        assert (context_d.slot_a is None)

        delattr(context_b, "slot_a")
        assert (context_b.slot_a == "val_a")
        assert (context_c.slot_a == "val_a")
        assert (context_d.slot_a is None)

        context_d._extends(context_a)
        assert (context_d.slot_a == "val_a")
    
    def test_basic_callback(self):
        context_a, context_b, context_c, context_d = self.get_abc()
        
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
        context_a, context_b, context_c, context_d = self.get_abc()

        endpoint = ContextVar("Assertion", default=None)
        
        context_c.callback("slot_a", once=True, local_only=False, callback=lambda val: endpoint.set(val))
        context_b.slot_a = "val_a"
        assert endpoint.get() == "val_a"

        context_c.callback("slot_a", once=True, local_only=False, callback=lambda val: endpoint.set(val))
        context_a.slot_a = "val_a1"
        assert endpoint.get() == "val_a1"

    def test_diffed_extension(self,):
        ''' Verify that setting an extension (add and remove), will dif and callback relevent. 
        Add && Remove -> Callback
        Modify where (not ( Old is New )) -> Callback
        Modify where (Old is New) -> No Callback
        '''

        context_a, context_b, context_c, context_d = self.get_abc()

        context_a.slot_a = "val_a"
        assert context_d.slot_a is None

        endpoint = ContextVar("Endpoint", default=None)
        context_d.callback("slot_a", callback=lambda v:endpoint.set(v), once=False, local_only=False)

        context_d.set_extends(context_a)
        assert endpoint.get() == "val_a"

        context_d.set_extends(None)
        assert endpoint.get() is None

        #TODO: Test dif
