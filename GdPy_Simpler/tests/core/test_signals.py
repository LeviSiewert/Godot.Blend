import pytest 

from ...core.signals import Signal

@pytest.mark.dependency(name="Test_Signal")
class Test_Signal():
    
    def test_connect(self):
        raise NotImplementedError()
    
    def test_connect_once(self):
        raise NotImplementedError()
    
    def test_append_self(self):
        raise NotImplementedError()
    
    def test_forward(self):
        raise NotImplementedError()
    
    def test_remove(self):
        raise NotImplementedError()

