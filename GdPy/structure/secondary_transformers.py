''' 
This module will contain the PyGd base classes & logic for (distributed or centralized) secondary transformers 
Due to Future plans, The Secondary Transformer chain must allow for:
- Isolated environment(s)
    - File filtering on load via extension
- Bidirectional Testing per constructed transfomer
- Flags for scope of transfomer
    - Single class or all inherited
- pipeline will need to change per env as well. Consider later when problem more well defined.
'''

from abc import ABC, abstractmethod
from ..primitives import Collection

class Transformer(ABC):
    godot_class  : str
    allow_extend : bool = True
    _integrated  : bool = False

class TransformerEnv[T:Transformer](Collection):
    by_gdid : dict[str:T]
    environment : str

    def __init__(self, environment : str):
        self.environment = environment
        self.by_gdid = {}
        super().__init__()

    def _integrate(self,item:Transformer):
        self.by_gdid[item.gdid] = item

    def _disintegrate(self,item:Transformer):
        pass

    def __getitem__(self, key):
        return self.by_gdid.get(key)
    
    def attach_classdb(class_db):
        pass

    def call():
        pass

class TransformerDb[T:TransformerEnv](Collection):
    pass