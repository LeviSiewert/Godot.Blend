from __future__ import annotations

from typing import Self

from .structure import StructReference, RefType, _ItemIO, _ResourceIO
from .collection import Collection, CollectionKey
from .context import Context as _Context
from .signals import Signal

class Context(_Context):
    _slots_ = ("project", "resource", "subresource")

class _Item(_ItemIO, _ResourceIO):
    ''' Nestable test object type '''

    context : Context
    
    key : CollectionKey[str]

    col_a : Collection[str, _Item]
    col_b : Collection[str, _Item]

    fullfill_references : Signal[Self, RefType, str]
    update_references : Signal[RefType, str, RefType, str, _Item|None]

    def provide_reftype_key(self):
        return (None, None)

    def __setup__(self):
        self.context = Context()
        self.key = CollectionKey(src=self, key=None)
        self.update_references = Signal(self)
        self.fullfill_references = Signal(self)
        self.col_a = Collection(key_attr="key",context=self.context)
        self.col_b = Collection(key_attr="key",context=self.context)

    def __init__(self, key:str, ctx_name:str):
        self.__setup__()
        self.key.key = key
        setattr(self.context, ctx_name, self)

class Test_StructReference():

    def test_construction_key(self):
        r = StructReference(key="val", ref_type=RefType.RID)

    def test_construction_obj(self):
        i = _Item("val", "obj")
        r = StructReference(obj=i)
        assert r.sref is i
        assert len(i.fullfill_references.subscribers) == 1

    def test_obj_fullfill_ref(self):
        i = _Item("val", "obj")
        r = StructReference(obj=i)

        i.fullfill_references(RefType.RID, "val")

        assert r.ref_type == RefType.RID
        assert r.key == "val"
        assert r.sref is None
        assert r.wref() is i

    def test_element_changed_connection(self):
        i = _Item("val", "project")
        r = StructReference(obj=_Item("val","resource"))

        r.context.set_extends(i.context)
        
        assert len(i.update_references.subscribers) == 1

    def test_element_changed(self):
        p = _Item("", "project")
        i = _Item("yek","resource")
        p.col_a.append(i)
        
        r = StructReference(obj=i)
        r.context.set_extends(p.context)

        def _filter(r:StructReference):
            return r.sref is i
        def _updater(r:StructReference):
            r.ref_type = ("project", "col_a", True)
            r.key = "yek"

        p.update_references(_filter,_updater)

        assert r.ref_type == ("project", "col_a", True)
        assert r.key == "yek"
        assert r.resolve(p.context) is i



    # def test_obj_update_ref(self):
    #     pass
    