from ...core.collections import (
    Collection, 
    CollectionKey, 
    CollectionRef, 
    StructContext)

import pytest

class ExampleObject():
    key : CollectionKey[str]

    def __setup__(self):
        self.key = CollectionKey(self)

collection : Collection[ExampleObject] = Collection("key", StructContext())

@pytest.mark.dependency(name="Test_Collection", depends=["test_context.py::Test_Context", "test_signals.py::Test_Signals"])
class Test_Collections():

    def test_append(self):
        raise NotImplementedError()

    def test_find(self):
        raise NotImplementedError()

    def test_rename(self):
        raise NotImplementedError()

    def test_remove(self):
        raise NotImplementedError()



    def test_read_reference(self):
        raise NotImplementedError()

    def test_append_reference(self):
        raise NotImplementedError()

    def test_rename_reference(self):
        raise NotImplementedError()

    def test_remove_reference(self):
        raise NotImplementedError()

    

