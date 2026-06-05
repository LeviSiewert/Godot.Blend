
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..primitives import Signal, SignalContainer, Collection, Context
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
    root : Path
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

    def __init__(self, root:Path):
        self.by_uuid = {}
        self.by_path = {}
        
        self.root = root
        self._observer = _Observer()
        self._observer.schedule(self._EventHandler(self), path=root, recursive=True)
        self._observer.start()
        
        super().__init__()
        self.fs_created.connect(self._on_fs_created)
        self.fs_modified.connect(self._on_fs_modified)
        self.fs_deleted.connect(self._on_fs_deleted)
        self.fs_moved.connect(self._on_fs_moved)

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
    
    def _on_fs_created(self, path:str):
        if file := self[path]:
            file.fs_created(path)
        else:
            self.append(self._generate_file(path))

    def _on_fs_modified(self, path:str):
        if file := self[path]:
            file.fs_modified()
        else:
            ## If untracked:
            self.append(self._generate_file(path))

    def _on_fs_deleted(self, path:str):
        if file := self[path]:
            file.fs_deleted()
        else:
            pass

    def _on_fs_moved(self, fr_path:str, to_path:str):
        if file := self[fr_path]:
            file.fs_moved(fr_path, to_path)
        elif file := self[to_path]: ## File already has corrected path
            pass
        else:
            self.append(self._generate_file(fr_path))
    
    _queue_targets : list[File]
    def _on_fs_queue_empty(self):
        for x in self._queue_targets:
            x.fs_queue_empty()

    def _generate_file(path:Path)->File:
        ## TODO: Overwrite in env for more file types
        return File(Path)

    class _EventHandler(_FileSystemEventHandler):
        ''' Utility class, forward events to local signals '''
        file_db : FileDb 
        def __init__(self, file_db:FileDb):
            self.file_db = file_db
            super().__init__()

        def on_created(self, event):
            if event.is_directory: return
            self.file_db.fs_created(event.src_path)
            self._check_empty()
        def on_modified(self, event):
            if event.is_directory: return
            self.file_db.fs_modified(event.src_path)
            self._check_empty()
        def on_deleted(self, event):
            if event.is_directory: return
            self.file_db.fs_deleted(event.src_path)
            self._check_empty()
        def on_moved(self, event):
            if event.is_directory: return
            self.file_db.fs_moved(event.src_path, event.dest_path)
            self._check_empty()

        def _check_empty(self):
            if self.file_db._observer._event_queue.is_empty():
                self.file_db.fs_queue_empty()