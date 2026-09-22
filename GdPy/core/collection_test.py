from .collection import Collection, CollectionKey, _ItemIo, OverlayMode
from contextvars import ContextVar

from typing import Self

class _Item(_ItemIo):
    key : CollectionKey[str]
    value : int = 0
    overlay : Self|None=None

    def overlay_copy(self,)->Self:
        r = _Item(self.key)
        r.set_overlay(self)
        return r

    def overlay_is_thin(self)->bool:
        if self.overlay is None: 
            return False
        return self.overlay.value == self.value

    def set_overlay(self, item:Self|None)->None:
        self.overlay=item

    def __init__(self, key:str, value:int=0):
        self.value = value
        self.key = CollectionKey(self, key)

class Test_Collection():

    def test_append(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        c.append(i)
        assert len(c) == 1
        assert c["key_value"] is i

    def test_append_collectionkeysignal(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        c.append(i)
        assert len(i.key.key_updated.subscribers) == 1
        # assert (c._on_rename_signal in i.key.key_updated)

    def test_append_signal(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        cvar = ContextVar("")
        c.appended.connect(lambda k,v: cvar.set((k,v)))

        c.append(i)

        assert cvar.get() == ("key_value", i)


    def test_remove(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        c.append(i)

        c.remove(i)
        assert len(c) == 0
        assert c.get("key_value", None) is None

    def test_remove_signal(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        c.append(i)
        cvar = ContextVar("")
        c.removed.connect(lambda k,v: cvar.set((k,v)))

        c.remove(i)

        assert cvar.get() == ("key_value", i)
        

    def test_rename(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")

        c.append(i)
        c.rename(i, "eulav_yek")

        assert i.key.key == "eulav_yek"
        assert c["eulav_yek"] is i
        assert c.get("key_value", default=None) is None

    def test_rename_signal(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        cvar = ContextVar("")
        c.renamed.connect(lambda k0,k,v: cvar.set((k0,k,v)))

        c.append(i)
        c.rename(i, "eulav_yek")

        assert cvar.get() == ("key_value", "eulav_yek", i)

    def test_rename_via_collectionkey(self):
        c = Collection(key_attr="key")
        i = _Item("key_value")
        c.append(i)

        i.key.key = "eulav_yek"

        assert c["eulav_yek"] is i
        assert c.get("key_value", None) is None
        

    def test_resolve_rename(self):
        c = Collection(key_attr="key")
        c.generate_key = lambda x: "standin" ## Monkeypatch for verification
        i1 = _Item("i1")
        i2 = _Item("i2")
        c.append(i1)
        c.append(i2)

        c._resolve_key_collision("i1", i1, i2, rename=True, replace=False, right_key_priority=True)

        assert i1.key.key == "standin"
        assert i2.key.key == "i1"

    def test_resolve_rename_lpriority(self):
        c = Collection(key_attr="key")
        c.generate_key = lambda x: "standin" ## Monkeypatch for verification
        i1 = _Item("i1")
        i2 = _Item("i2")
        c.append(i1)
        c.append(i2)

        c._resolve_key_collision("i1", i1, i2, rename=True, replace=False, right_key_priority=False)

        assert i1.key.key == "i1"
        assert i2.key.key == "standin"

    def test_resolve_rename_signal(self):
        c = Collection(key_attr="key")
        c.generate_key = lambda x: "standin" ## Monkeypatch for verification
        i_l = _Item("i_l")
        i_r = _Item("i_r")
        c.append(i_l)
        c.append(i_r)

        _removed = []
        _appended = []
        _renamed = []
        _replaced = []
        c.removed.connect(lambda k,v: _removed.append((k,v)))
        c.appended.connect(lambda k,v: _appended.append((k,v)))
        c.renamed.connect(lambda k0,k,v: _renamed.append((k0,k,v)))
        c.replaced.connect(lambda k,v0,v: _replaced.append((k,v0,v)))

        c._resolve_key_collision("i_l", i_l, i_r, rename=True, replace=False, right_key_priority=True)

        assert len(_removed) == 0
        assert len(_appended) == 0
        assert _renamed == [("i_l", "standin", i_l)]
        assert _replaced == [("i_l", i_l, i_r)]

    def test_key_generation_str(self):
        c = Collection(key_attr="key", key_is_string=True, key_resolve_incriment=False ,key_formatter=None)
        i1 = _Item("key")
        i2 = _Item("key")
        c.append(i1)
        c.append(i2, rename=True, right_key_priority=True)

        assert i1.key.key != "key"
        assert i1.key.key != "key1"
        assert i2.key.key == "key"



    def test_key_generation_int(self):
        c = Collection(key_attr="key", key_is_string=False, key_resolve_incriment=False, key_formatter=None)

        i1 = _Item(1)
        i2 = _Item(1)
        c.append(i1)
        c.append(i2, rename=True, right_key_priority=True)

        assert i1.key.key != 1
        assert i2.key.key == 1

    def test_key_generation_str_incriment(self):
        c = Collection(key_attr="key", key_is_string=True, key_resolve_incriment=True, key_formatter=None)

        i1 = _Item("key")
        i2 = _Item("key")
        c.append(i1)
        c.append(i2, rename=True, right_key_priority=True)

        assert i1.key.key == "key1"
        assert i2.key.key == "key"


    def test_key_generation_int_incriment(self):
        c = Collection(key_attr="key", key_is_string=False, key_resolve_incriment=True ,key_formatter=None)

        i1 = _Item(1)
        i2 = _Item(1)
        c.append(i1)
        c.append(i2, rename=True, right_key_priority=True)

        assert i1.key.key == 2
        assert i2.key.key == 1

    def test_key_generation_formatter(self):
        cvar = ContextVar("")
        def formatter(col,obj,key): 
            cvar.set((col,obj,key))
            return key 
        
        c = Collection(key_attr="key", key_is_string=True, key_resolve_incriment=True, key_formatter=formatter)
        i1 = _Item("key")
        i2 = _Item("key")
        c.append(i1)
        c.append(i2, rename=True, right_key_priority=True)

        assert cvar.get()[0] is c 
        assert cvar.get()[1] == i1
        assert cvar.get()[2] == "key1"


    def test_overlay_empty(self):
        C0 = Collection("key", OverlayMode.COPY)
        C1 = Collection("key", OverlayMode.COPY)

        C1.set_overlay(C0)
        assert C1.overlay is C0

        C1.set_overlay(None)
        assert C1.overlay is None

    def test_overlay_empty_signals(self):
        C0 = Collection("key", OverlayMode.COPY)
        C1 = Collection("key", OverlayMode.COPY)
        c = ContextVar("")
        C1.overlay_updated.connect(lambda x:c.set(x))

        C1.set_overlay(C0)
        assert c.get() is C0

        C1.set_overlay(None)
        assert c.get() is None

    def test_overlay_empty_dif(self):
        C0 = Collection("key", OverlayMode.COPY)
        C1 = Collection("key", OverlayMode.COPY)

        dif = C1.set_overlay(C0)
        assert dif == {"appended":{},"removed":{},"replaced":{}} 


    def test_overlay_basic_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])
        C1 = Collection("key", OverlayMode.COPY)

        C1.set_overlay(C0)

        I1 = C1["key"]

        assert len(C1) == 1
        assert not (I1 is I0)
        assert I1.overlay is I0
        assert I1.overlay_is_thin()

        C1.set_overlay(None)

        assert C1.overlay is None
        assert len(C1) == 0
        assert not (I1 in C1)

    # def test_overlay_basic_copy_signals(self):
    #     pass

    def test_overlay_basic_copy_dif(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])
        C1 = Collection("key", OverlayMode.COPY)

        dif = C1.set_overlay(C0)

        I1 = C1["key"]
        assert dif == {"appended":{"key":I1}, "removed":{}, "replaced":{}}

        dif = C1.set_overlay(None)
        assert dif == {"appended":{}, "removed":{"key":I1}, "replaced":{}}


    def test_overlay_basic_passthrough(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.PASSTHROUGH, iterable=[I0])
        C1 = Collection("key", OverlayMode.PASSTHROUGH)

        C1.set_overlay(C0)

        I1 = C1["key"]

        assert C1.overlay is C0
        assert len(C1) == 1
        assert len(C1.data) == 0
        assert I1 is I0
        assert I0 in C1

        C1.set_overlay(None)

        assert C1.overlay == None
        assert len(C1) == 0
        assert len(C1.data) == 0
        assert not (I1 in C1)

    # def test_overlay_basic_passthrough_signals(self):
    #     pass

    def test_overlay_basic_passthrough_dif(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.PASSTHROUGH, iterable=[I0])
        C1 = Collection("key", OverlayMode.PASSTHROUGH)

        dif = C1.set_overlay(C0)
        assert dif == {"appended":{"key":I0}, "removed":{}, "replaced":{}}

        dif = C1.set_overlay(None)
        assert dif == {"appended":{}, "removed":{"key":I0}, "replaced":{}}


    def test_overlay_intigrate_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        I1 = _Item("key", 1)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])

        C1.set_overlay(C0)
        assert I1.overlay is I0

        C1.set_overlay(None)
        assert I1 in C1
        assert I1.overlay is None

    def test_overlay_intigrate_copy_thin(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])

        C1.set_overlay(C0)
        assert I1.overlay is I0

        C1.set_overlay(None)
        assert not (I1 in C1)
        assert I1.overlay is I0 ## Kept, as this object is now orphaned


    def test_overlay_intigrate_passthrough(self):
        I0 = _Item("key", 0)
        I0_b = _Item("key2", 0)
        C0 = Collection("key", OverlayMode.PASSTHROUGH, iterable=[I0, I0_b])

        I1 = _Item("key", 1)
        C1 = Collection("key", OverlayMode.PASSTHROUGH, iterable=[I1])

        C1.set_overlay(C0)

        assert C1.overlay is C0
        assert I1.overlay is None
        assert I1 in C1
        assert not (I0 in C1)
        assert I0_b in C1

        C1.set_overlay(None)

        assert C1.overlay is None
        assert I1 in C1
        assert not (I0_b in C1)

    def test_overlay_intigrate_passthrough_thin(self):
        I0 = _Item("key", 0)
        I0_b = _Item("key2", 0)
        C0 = Collection("key", OverlayMode.PASSTHROUGH, iterable=[I0, I0_b])

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.PASSTHROUGH, iterable=[I1])

        C1.set_overlay(C0)

        assert C1.overlay is C0
        assert I1.overlay is None
        assert I1 in C1
        assert not (I0 in C1)
        assert I0_b in C1

        C1.set_overlay(None)

        assert C1.overlay is None
        assert I1 in C1
        assert not (I0_b in C1)


    def test_overlay_leaf_appended_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        C1 = Collection("key", OverlayMode.COPY)
        C1.set_overlay(C0)

        I1 = _Item("key", 0)
        C1.append(I1)
        ## Unknown desired behavior; Integrate OR rename left priority?
        raise NotImplementedError()

    def test_overlay_leaf_removed_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])
        C1.set_overlay(C0)

        C1.remove(I1)
        ## Unknown desired behavior; if present in parent, error?

        raise NotImplementedError()

    def test_overlay_leaf_replaced_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])
        C1.set_overlay(C0)

        C1.remove(I1)
        ## Unknown desired behavior; replace w/ new & set overlay?

        raise NotImplementedError()

    def test_overlay_root_appended_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY)

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])
        C1.set_overlay(C0)

        C0.append(I0)
        ## Unknown desired behavior!

        raise NotImplementedError()

    def test_overlay_root_removed_copy(self):
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])
        C1.set_overlay(C0)

        C0.remove(I0)

        ## Unknown desired behavior!
        raise NotImplementedError()

    def test_overlay_root_replaced_copy(self): 
        I0 = _Item("key", 0)
        C0 = Collection("key", OverlayMode.COPY, iterable=[I0])

        I1 = _Item("key", 0)
        C1 = Collection("key", OverlayMode.COPY, iterable=[I1])
        C1.set_overlay(C0)

        C0["key"] = _Item("key", value = 1)

        ## Unknown desired behavior!
        raise NotImplementedError()


    def test_overlay_appended_passthrough(self):
        ## Desired behavior: Replaced signal.
        raise NotImplementedError()

    def test_overlay_removed_passthrough(self):
        ## Desired behavior: (Replaced) if lower level key present, removed otherwise 
        raise NotImplementedError()

    def test_overlay_replaced_passthrough(self):
        ## Desired behavior: (Replaced) signal emit
        raise NotImplementedError()
        