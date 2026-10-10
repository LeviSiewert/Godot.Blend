from fsspec.spec import AbstractFileSystem
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem

from .signals import Signal

class FsSignals():
    created : Signal #[str]
    removed : Signal #[str]
    updated : Signal #[str]
    deleted : Signal #[str]
    moved : Signal #[str, str]
    
    def __setup__(self):
        self.created = Signal(self)
        self.removed = Signal(self)
        self.updated = Signal(self)
        self.deleted = Signal(self)
        self.moved = Signal(self)

    def __init__(self,*args,**kwargs):
        self.__setup__()
        super().__init__(*args, **kwargs)

# class _Mixin(FsSignals):
class AbstractFileSystem(AbstractFileSystem,FsSignals):
    def __init__(self,*args,**kwargs):
        self.__setup__()
        super().__init__(*args, **kwargs)
    
class LocalFileSystem(LocalFileSystem,FsSignals):
    def __init__(self,*args,**kwargs):
        self.__setup__()
        super().__init__(*args, **kwargs)
    
class MemoryFileSystem(MemoryFileSystem,FsSignals):
    def __init__(self,*args,**kwargs):
        self.__setup__()
        super().__init__(*args, **kwargs)