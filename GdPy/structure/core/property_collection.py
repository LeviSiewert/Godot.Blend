from .primitives import Collection
from .class_db import ClassDbEnforcable
from typing import Any

class PropertyCollection[T](Collection, ClassDbEnforcable):
    vals : dict[str, type]
    pins : list[str]

    def __init__(self):
        self.vals = {}
        self.pins = []
        super().__init__()

    def set_pin(self,k):
        self.pins.append(k)
        
    def rem_pin(self,k):
        if k in self.pins:
            self.pins.remove(k)

    def append(self, k:str, item:T):
        self._integrate(k,item)
        self.item_appended((k,item))

    def remove(self, k:str, item:T):
        self._disintegrate(k,item)
        self.item_removed((k,item))
    
    def extend(self, iterable):
        for k,v in iterable:
            self.append(k,v)

    def validate(self,):
        ''' Verify Collection state '''
        raise Exception("not yet implimented! Featureset ClassDbEnforcable")

    def allowed(self, key:str, property:Any)->bool:
        ''' Verify key:property being allowed '''
        raise Exception("not yet implimented! Featureset ClassDbEnforcable")
    
    def default(self, key:str, property:Any)->T:
        raise Exception("not yet implimented! Featureset ClassDbEnforcable")
    
    def _integrate(self, key, item):
        # assert(self.allowed(key,item)) ## Featureset ClassDbEnforceable
        self.vals[key] = item
        self.item_appended(key,item)
    
    def _disintegrate(self, key):
        val = self.vals[key]
        self.item_removed(key, val)
        self.vals.remove(key)        
    
    def __getitem__(self, key):
        return self.vals[key]
    
    def __setitem__(self, key, value):
        self._integrate(key, value)
        
    def __delitem__(self, key):
        self._disintegrate(key)
        
