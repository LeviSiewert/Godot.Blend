
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Type
from ...primitives import Signal, SignalContainer, Collection, Context
from pathlib import Path
from watchdog.events import FileSystemEventHandler as _FileSystemEventHandler#type:ignore
from watchdog import Observer as _Observer #type:ignore

class File(ABC, SignalContainer):
    
    uuid : str
    uuid_set : Signal[str, str] #Fr, To

    path : str
    path_set : Signal[str, str] #Fr, To

    data : Any
    data_loaded : Signal[Any]
    data_dumped : Signal
    data_deleted : Signal

    ## Triggered by FileDb container
    fs_created : Signal
    fs_modified : Signal
    fs_deleted : Signal
    fs_moved : Signal[str, str]
    fs_queue_empty : Signal

    def __init__(self, uuid:str, path:str):
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
    # TODO: Properly support all 3 paths of res:// uid:// {absolute} 

    root : Path
    file_types : list[Type[File]]
    
    _observer : _Observer

    uuid_set : Signal[T,str,str]
    path_set : Signal[T,str,str]

    by_uuid : dict[str:T]
    by_path : dict[str:T]

    fs_created : Signal[str]
    fs_modified : Signal[str]
    fs_deleted : Signal[str]
    fs_moved : Signal[str, str]
    fs_queue_empty : Signal
    _queue_targets : list[File]


    def __init__(self, root:Path, file_types:list[Type[File]]):
        self.root = root        
        self.file_types = file_types

        self.by_uuid = {}
        self.by_path = {}
        self._queue_targets = []
        
        self._observer = _Observer()
        self._observer.schedule(self._EventHandler(self), path=root, recursive=True)
        self._observer.start()
        
        super().__init__()
        self.uuid_set.connect(self._on_file_uuid_set)
        self.path_set.connect(self._on_file_path_set)
        self.populate_existing()

    def populate_existing(self,):
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if not self.file_filter(path):
                continue
            if self[path]:
                continue
            self.append(self.generate_file(path))

    def file_filter(self, path:str)->bool:
        ''' Override; Env based. Source data from self.file_types '''
        return True

    def generate_file(self, path:Path)->File:
        ''' Override; Env based. Source data from self.file_types '''
        return File(path)

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
    
    def _on_file_uuid_set(self, file:File, fr_uuid:str, to_uuid:str):
        if fr_uuid in self.by_uuid.keys():
            del self.by_uuid[fr_uuid]
        self.by_uuid[to_uuid] = file
        
    def _on_file_path_set(self, file:File, fr_path:str, to_path:str):
        if fr_path in self.by_path.keys():
            del self.by_path[fr_path]
        self.by_path[to_path] = file


    ## "Tells" called by FileDb && initial file discovery
    def tell_fs_created(self, path:str):
        if file := self[path]:
            file.fs_created(path)
            self._queue_targets.append(file)
        else: ## If untracked:
            file = self.generate_file(path)
            self.append(file)
            self.fs_created(file)
            self._queue_targets.append(file)

    def tell_fs_modified(self, path:str):
        if file := self[path]:
            file.fs_modified()
            self.fs_modified(file)
            self._queue_targets.append(file)
        else: ## If untracked:
            file = self.generate_file(path)
            self.append(file)
            self.fs_created(file)
            self._queue_targets.append(file)

    def tell_fs_deleted(self, path:str):
        if file := self[path]:
            file.fs_deleted()
            self.fs_deleted(file)
            self.remove(file)
            self._queue_targets.append(file)
        else: ## If untracked:
            pass

    def tell_fs_moved(self, fr_path:str, to_path:str):
        if file := self[fr_path]:
            file.fs_moved(fr_path, to_path)
            self._queue_targets.append(file)
        elif file := self[to_path]: ## File already has corrected path
            pass
        else:
            self.append(self.generate_file(fr_path))
    
    def tell_fs_queue_empty(self):
        for x in self._queue_targets:
            x.fs_queue_empty()
        self._queue_targets.clear()

    class _EventHandler(_FileSystemEventHandler):
        ''' Utility class, forward events to local signals '''
        file_db : FileDb 
        def __init__(self, file_db:FileDb):
            self.file_db = file_db
            super().__init__()

        def on_created(self, event):
            if event.is_directory: return
            if not self.file_db.file_filter(event.src_path): return
            self.file_db.tell_fs_created(event.src_path)
            self._check_empty()
        
        def on_modified(self, event):
            if event.is_directory: return
            if not self.file_db.file_filter(event.src_path): return
            self.file_db.tell_fs_modified(event.src_path)
            self._check_empty()
        
        def on_deleted(self, event):
            if event.is_directory: return
            if not self.file_db.file_filter(event.src_path): return
            self.file_db.tell_fs_deleted(event.src_path)
            self._check_empty()

        def on_moved(self, event):
            if event.is_directory: return
            if not self.file_db.file_filter(event.src_path): return
            self.file_db.tell_fs_moved(event.src_path, event.dest_path)
            self._check_empty()

        def _check_empty(self):
            if self.file_db._observer._event_queue.is_empty():
                self.file_db.tell_fs_queue_empty()