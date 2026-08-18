from .collection import Collection, CollectionKey
from contextvars import ContextVar

class _Item():
    key : CollectionKey[str]
    def __init__(self, key:str|None):
        self.key = CollectionKey(src=self, key=key)

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

    def test_key_generation_str():
        raise NotImplementedError()

    def test_key_generation_int():
        raise NotImplementedError()

    def test_key_generation_str_index():
        raise NotImplementedError()

    def test_key_generation_int_index():
        raise NotImplementedError()

    def test_key_generation_custom():
        raise NotImplementedError()



    # def test_resolve_replace(self):
    #     raise NotImplementedError()
    # def test_resolve_replace_lpriority(self):
    #     raise NotImplementedError()
    # def test_resolve_replace_signal(self):
    #     raise NotImplementedError()
        