from contextvars import ContextVar

from .collection import Collection, CollectionKey, Context

class _Item():
    context : Context

    var : int = 0
    key : CollectionKey[str]

    def __init__(self, key:str):
        self.context = Context()
        self.var = 0
        self.key = CollectionKey(key)

    def _reference_callback(self, context:Context):
        self.context.set_extends(context)
    
    def _dereference_callback(self, context:Context):
        self.context.set_extends(None)

class Test_CollectionKey():
    def test_basic():
        k = CollectionKey("key")

        assert k._key == "key"
        assert k.key == "key"

        c = ContextVar("")

        k.key_updated.connect(lambda x: c.set(x))
        k.key = "yek"

        assert c.get() == "yek"
        assert k.key == "yek"


class Test_Collection():
    def test_construction(self,):
        c = Collection(context=Context())

    def test_append_remove(self):
        c = Collection(context=Context())
        i = _Item("key")

        c.append(i)

        assert i in c
        assert c["key"] is i
        assert c.var == 1
        assert c.context._extends is c.context

        c.remove(i)

        assert not (i in c)
        assert c.get("key", None) is None 
        assert c.var == 0
        assert c.context._extends is None

    def test_rename(self):
        c = Collection()
        i = _Item("key")

        c.append(i)

        assert c["key"] is i

        c.rename(i, "yek")

        assert c["yek"] is i
        assert c.get("key",None) is None
        

    def test_rename_via_key(self):
        c = Collection()
        i = _Item("key")

        c.append(i)

        assert c["key"] is i

        i.key.key = "yek"

        assert c["yek"] is i
        assert c.get("key",None) is None

    def test_rename_via_setitem(self):
        c = Collection()
        i = _Item("key")

        c.append(i)

        assert c["key"] is i

        c["yek"] = i

        assert c["yek"] is i
        assert c.get("key",None) is None

    def test_name_via_setitem(self):
        c = Collection()
        i = _Item("key")

        c["yek"] = i

        assert c["yek"] is i
        assert c.get("key",None) is None 


    def test_keycollision_via_append(self):
        c = Collection()
        i0 = _Item("key")
        i1 = _Item("key")

        c.append(i0)
        c.append(i1)

        assert len(c) == 2

        assert i0.key.key != "key"
        assert i1.key.key == "key"

    def test_keycollision_via_append_leftprio(self):
        c = Collection()
        i0 = _Item("key")
        i1 = _Item("key")

        c.append(i0)
        c.append(i1, r_key_priority=False)

        assert len(c) == 2

        assert i0.key.key == "key"
        assert i1.key.key != "key"

    def test_replace_via_set():
        c = Collection()
        i0 = _Item()
        i1 = _Item()

        c["key"] = i0
        c.set("key", i1, replace=True)        

        assert len(c) == 1
        assert i1 in c
        assert i1.key.key == "key"

    def test_replace_via_setitem(self):
        """ Assertion error doesn't occur, but should it? What other re-actions are required? """
        c = Collection()
        i0 = _Item()
        i1 = _Item()

        c["key"] = i0
        c["key"] = i1

        assert len(c) == 1
        assert i1 in c
        assert i1.key.key == "key"

    def test_keycollision_via_rename(self):
        ''' Dynamic References must be rectified externally as no strong connection exists between dynamic refs and collections, this will be done via signals the ref subs to
        The signals will not be on the collection itself, but rather the scope containing the collection '''
        c = Collection()
        i0 = _Item("key")
        i1 = _Item("key1")

        c.append(i0)
        c.append(i1)

        c.rename(i1, "key")

        assert i1.key.key == "key"

    def test_keycollision_via_rename_left_priority(self):
        ''' Dynamic References must be rectified externally as no strong connection exists between dynamic refs and collections, this will be done via signals the ref subs to
        The signals will not be on the collection itself, but rather the scope containing the collection '''
        c = Collection()
        i0 = _Item("key")
        i1 = _Item("key1")

        c.append(i0)
        c.append(i1)
        c.rename(i1, "key", r_key_priority=False)

        assert i0.key.key == "key"

from .structure import DynamicPromise, DynamicPromiseStructural


class _Item():
    key : CollectionKey[str]
    def __init__(self, key:str):
        self.key = CollectionKey(str)

class _Resource():
    context : Context
    col : Collection[str, _Item]
    def __init__(self):
        self.context = Context(resource=self)
        self.col = Collection()

class Test_DynamicPromise():

    def test_construction():
        r = _Resource()
        i = _Item("key")

        promise = DynamicPromise("resource", "col", "key")
        assert promise.resolve(r.context) is promise

        r.col.append(i)

        assert promise.resolve(r.context) is i

        r.remap_ref("resource", "col", "key", "resource", "col", "yek")
        assert promise.key == "key"

        promise.context.set_extends(r.context)

        r.remap_ref("resource", "col", "key", "resource", "col", "yek")
        assert promise.key == "yek"
        assert promise.resolve(r.context) is promise


        r.col.rename(i, "yek")
        assert promise.resolve(r.context) is i