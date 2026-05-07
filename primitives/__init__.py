from typing import Callable

class Signal():
    _connections : list[Callable]

    def __init__(self):
        self._connections = []

    def connect(self,val:Callable):
        self._connections.append(val)

    def disconnect(self,val:Callable):
        self._connections.remove(val)

    def emit(self,*args,**kwargs):
        for x in self._connections:
            x(*args,**kwargs)
        