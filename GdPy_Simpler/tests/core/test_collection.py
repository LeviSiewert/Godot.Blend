from ...core.collections import (
    Collection, 
    CollectionKey, 
    CollectionRef, 
    StructContext)

import pytest

class ExampleObject():
    context : StructContext
    key : CollectionKey[str]

    def __setup__(self):
        self.context = StructContext()
        self.key = CollectionKey(self)

    def __init__(self, key:str|None):
        self.__setup__() 
        self.key.set_key(key)


# @pytest.mark.dependency(name="Test_Collection", depends=["test_context.py::Test_Context", "test_signals.py::Test_Signals"])
class Test_Collections():
    def test_make(self,):
        collection : Collection[ExampleObject] = Collection("key", StructContext())


    def test_append_remove(self):
        col : Collection[ExampleObject] = Collection("key", StructContext())
        obj = ExampleObject("keyval")

        col.append(obj)
        assert "keyval" == col.find(obj)
        assert col["keyval"] is obj
        assert obj.key.col is col

        col.remove(obj)
        assert(len(col) == 0)
        assert col.find(obj,None) is None
        assert obj.key.col is None


    def test_rename(self):
        col : Collection[ExampleObject] = Collection("key", StructContext())
        obj = ExampleObject("oldkey")

        col.append(obj)
        obj.key.set_key("newkey")
        assert col["newkey"] is obj
        assert col.get("oldkey",None) is None


    def test_reference_read_existing(self):
        col : Collection[ExampleObject] = Collection("key", StructContext())
        obj = ExampleObject("keyval")

        col.append(obj)
        ref = CollectionRef(key="keyval", col=col)
        assert ref.get() is obj


    def test_reference_read_existing_cached(self):
        col : Collection[ExampleObject] = Collection("key", StructContext())
        obj = ExampleObject("keyval")

        col.append(obj)
        ref = CollectionRef(col=col, cache=obj)
        assert ref.key == "keyval"
        assert ref.get() is obj


    def test_reference_read_delayed(self):
        col : Collection[ExampleObject] = Collection("key", StructContext())
        obj = ExampleObject("keyval")

        ref = CollectionRef(key="keyval", col=col)
        assert ref.get() is None

        col.append(obj)
        assert ref.get() is obj


    def test_reference_read_existing_cached(self):
        col : Collection[ExampleObject] = Collection("key", StructContext())
        obj = ExampleObject("keyval")        
        ref = CollectionRef(col=col, cache=obj)

        col.append(obj)
        assert ref.get() is obj
        assert ref.key == "keyval"

    # def test_reference_cached_swap_key():
    #     ''' By default, removing and adding a ref will swap the key towards the new ref'''
    #     ## TODO: option to disable cached refs. this behavior can be confusing

    #     col : Collection[ExampleObject] = Collection("key", StructContext())
    #     obj_a = ExampleObject("oldkey")
    #     col.append(obj_a)
    #     ref = CollectionRef(key="oldkey", col=col)
        
    #     assert ref.get() is obj_a
    #     col.remove(obj_a)
    #     assert ref.get() is None
    #     assert ref.key is 'oldkey'

    #     obj_a.key.set_key("newkey")
    #     col.append(obj_a)
    #     assert ref.get() is obj_a
    #     assert ref.key is "newkey"

    # def test_reference_rename_keep_target(self):
    #     col : Collection[ExampleObject] = Collection("key", StructContext())
    #     obj_a = ExampleObject("oldkey")
    #     ref = CollectionRef(key="oldkey", col=col)
    #     col.append(obj_a)

    #     obj_a.key.set_key("newkey", update_sub_refs=True)
    #     assert ref.get() is obj_a
    #     assert ref._cached() is "newkey"

    # def test_reference_rename_drop_target(self):
    #     col : Collection[ExampleObject] = Collection("key", StructContext())
    #     obj_a = ExampleObject("oldkey")
    #     ref = CollectionRef(key="oldkey", col=col)
    #     col.append(obj_a)

    #     obj_a.key.set_key("newkey", update_sub_refs=False)
    #     assert ref.get() is None
    #     assert ref._cached() is None

    # def test_reference_switch_via_remove_add(self,):
    #     col : Collection[ExampleObject] = Collection("key", StructContext())
    #     obj_a = ExampleObject("keyval")
    #     obj_b = ExampleObject("keyval")

    #     col.append(obj_a)
    #     ref = CollectionRef(key="keyval", col=col)
    #     assert ref.get() is obj_a

    #     col.remove(obj_a)
    #     assert ref.get() is None
    #     assert ref._cached() is obj_a
 
    #     col.append(obj_b)
    #     assert ref.get() is obj_b
    #     assert ref._cached() is obj_b
