import pytest 

from ...core.context import StructContext

@pytest.mark.dependency(name="Test_Context", depends=["test_signals.py::Test_Signals"] )
class Test_Context():
    pass

    # def test_local(self):
    #     raise NotImplementedError()

    # def test_extend(self):
    #     raise NotImplementedError()

    # def test_signals(self):
    #     raise NotImplementedError()

    # def test_signals_extend_at(self):
    #     raise NotImplementedError()

    # def test_signals_extend_post(self):
    #     raise NotImplementedError()

    # def test_callback(self):
    #     raise NotImplementedError()

    # def test_callback_once(self):
    #     raise NotImplementedError()

    # def test_callback_remove(self):
    #     raise NotImplementedError()
