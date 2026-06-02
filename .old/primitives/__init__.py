from __future__ import annotations
from typing import Callable, Any

class Signal():
    _connections : list[Callable]
    source : Any = None

    def __init__(self, source:Any, forwards:list[Signal]=[]):
        self.source = source
        self._connections = []
        
        for x in forwards:
            self.connect(x.emit)

    def connect(self,val:Callable, append_source:bool=False):
        self._connections.append((val,append_source))

    def disconnect(self,val:Callable):
        self._connections.remove(val)

    def emit(self,*args,**kwargs):
        to_discon = []
        for x,app in self._connections:
            if app:
                res = x(x.source,*args,**kwargs)
            else:
                res = x(*args,**kwargs)
            if res == True:
                to_discon.append(res)
        for x in to_discon:
            self.disconnect(x)


class Collection():
    items : list[Any]
    item_appended : Signal
    item_removed : Signal
    
    def __init__(self):
        items = []
        self.item_appended = Signal(self) 
        self.item_removed = Signal(self) 
    
    def append(self,item:Any):
        self.items.append(item)
        self.item_appended.emit(item)

    def remove(self,item:Any):
        if item in self.items:
            self.items.remove(item)
            self.item_removed.emit(item)
