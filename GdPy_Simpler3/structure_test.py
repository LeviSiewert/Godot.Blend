from .context import Context
from .collection import Collection, CollectionKey
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

class Test_DynamicPromiseStructural():

    def test_all(self):
        r = _Resource()
        i = _Item("key")

        promise = DynamicPromiseStructural("resource", "col", "key")
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