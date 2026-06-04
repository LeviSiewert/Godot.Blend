from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..primitives import Signal, SignalContainer, Collection, Context


class File(ABC, SignalContainer):

    uuid : str
    uuid_set : Signal[str, str] #Fr, To

    path : str
    path_set : Signal[str, str] #Fr, To

    data : Any
    data_loaded : Signal[Any]
    data_dumped : Signal
    data_deleted : Signal

    def __init__(self, uuid, path):
        self.uuid = uuid
        self.path = path

    @abstractmethod
    def load(self, context:Context, *args, **kwargs):
        pass

    @abstractmethod
    def save(self,context:Context, *args, **kwargs):
        pass

    @abstractmethod
    def dump(self,):
        pass

    @abstractmethod
    def delete(self,):
        pass

class FileDb[T:File](Collection):
    uuid_set : Signal[T,str,str]
    path_set : Signal[T,str,str]

    by_uuid : dict[str:T]
    by_path : dict[str:T]

    def __init__(self):
        self.by_uuid = {}
        self.by_path = {}
        super().__init__()

    def _integrate(self,item:T):
        if item.uuid: self.by_uuid[item.uuid] = item
        if item.path: self.by_path[item.path] = item
        self.uuid_set.connect(item.uuid_set.forward)
        self.path_set.connect(item.path_set.forward)
    
    def _disintegrate(self,item:T):
        self.uuid_set.disconnect(item.uuid_set.forward)
        self.path_set.disconnect(item.path_set.forward)
        self.by_uuid.rem(item.uuid)
        self.by_path.rem(item.path)

    def __getitem__(self, key)->T:
        return self.by_uuid.get(key, self.by_path.get(key, None))