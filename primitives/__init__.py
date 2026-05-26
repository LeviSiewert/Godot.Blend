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
        to_discon = []
        for x in self._connections:
            res = x(*args,**kwargs)
            if res == True:
                to_discon.append(res)
        for x in to_discon:
            self.disconnect(x)

# def listener():
#     pass