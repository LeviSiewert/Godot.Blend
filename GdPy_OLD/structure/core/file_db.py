
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Type
from .primitives import Signal, SignalContainer, Collection, Context
from pathlib import Path
from watchdog.events import FileSystemEventHandler as _FileSystemEventHandler#type:ignore
from watchdog.observers import Observer as _Observer #type:ignore
from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum

class FsEvent(Enum):
    LOAD = 0
    SAVE = 1
    DUMP = 2
    MOVE = 3
    DELETE = 4

class ResourceUID(ABC, SignalContainer):
    ''' Equiv to Godot's ResourceUID
    Caches dependencies && mappings of UIDs within the FileDB
    '''

    uid_set : Signal[str,str,str] #path, fr_uid, to_uid

    uids : dict[str,str]
    cached_references : dict[str,list[str]]

    def __init__(self):
        self.uids = {}
        self.cached_references = {}
        super().__init__()

    def exists(self, path_or_uid)->bool:
        if path_or_uid.startswith("uid://"):
            return path_or_uid in self.uids.keys()
        else:
            return path_or_uid in self.uids.values()

    def to_path(self, uid:str)->str:
        return self.uids.get(uid)

    def to_uid(self, path:str)->str:
        for k,v in self.uids.items:
            if path == v:
                return k
        return False

    def add_uid(self, path, uid)->str:
        assert(not (uid in self.uids.keys()))
        self.uids[uid] = path        

    def rem_uid(self, path_or_uid:str)->str:
        if path_or_uid.startswith("uid://"):
            self.uids.pop(path_or_uid)
        else:
            self.rem_uid(self.to_uid(path_or_uid))

class File[T:Any](ABC, SignalContainer):
    ''' Implimentation of File level abstraction
    Registered to FileDB at project construction
    Handles pipeline loading file types into python
        - References may be defered
    Forwards file system signals
    Declares dependencies for moving asc files
    '''
    _cache_layers = tuple()
    
    fs_created : Signal
    fs_modified : Signal
    fs_deleted : Signal
    fs_moved : Signal[str, str]
    fs_queue_empty : Signal

    data_loaded : Signal
    data_dumped : Signal

    path_changed : Signal[str,str]
    uid_changed : Signal[str,str]

    _file_match_priority : int = 0
    _file_match_extensions : tuple[str] = tuple()

    path : Path
    data : T

    def __init__(self, path:str|Path, data:T=None):
        self.path = path
        self.data = data
        super().__init__()

    def get_uid(self, c:Context)->str|None:
        """ Get internal or adjecent UID w/a """
        return None
    
    def get_references(self,)->tuple[str]:
        ''' Return all uids && filepaths contained within this file for updating when/a '''
        ## TODO
        return tuple()

    def fsevent_bundle(self, c:Context, event:FsEvent, is_reaction:bool)->tuple[File]:
        ''' All fps returned will be bundled into current file system event, 
        resolved after stack completed and does not raise errors if file path is missing '''
        pass

    @abstractmethod
    def load(self, c:Context):
        pass

    @abstractmethod
    def save(self, c:Context):
        pass

    @abstractmethod
    def dump(self, c:Context):
        pass

    @abstractmethod
    def delete(self, c:Context):
        pass

    def __str__(self):
        return self.path

    def __repr__(self):
        length = len(self.path.parts)
        r = min(length, 2)
        pth = "/".join(self.path.parts[-r:])

        return f'{self.__class__.__name__}(.../{pth})'

class FileDb(ABC, SignalContainer):
    ''' Implimentation of project filesystem level abstraction 
    Matches Type[File] to files being loaded
    Watches & Signals filesystem changes (within project scope)
    Handles file movement dependencies
    '''

    item_appended : Signal[Any]
    item_removed : Signal[Any]

    files : dict[str, File]
    file_types : list[Type[File]]
    project_root : Path

    gd_project : Any

    def __init__(self, project_root:Path, file_types:list[Type[File]]):
        self.files = {}
        self.project_root = project_root
        self.file_types = sorted(file_types, key = lambda x: x._file_match_priority)
        self.resource_uid = ResourceUID()
        super().__init__()
        self.setup_fs_listener()
        self.populate_existing()

    def get_abs(self, value:str|Path)->str:
        if isinstance(value, Path):
            value = str(value)

        if value.startswith("res://"):
            return self.project_root / value[6:]

        if value.startswith("uid://"):
            if not self.resource_uid.exists(value):
                raise KeyError("ResourceUID could not be found;", value)
            return self.resource_uid.to_path(value)
        
        if value.startswith("user://"):
            raise KeyError("user:// path is not currently supported;", value)

        return value

    def get_file(self, value:str|Path, ensure:bool=True, null_ok:bool=False)->File|None:

        path = Path(self.get_abs(value))

        if (not path.exists()):
            if not null_ok:
                raise KeyError("Could not find filepath", path)
            return None

        if res := self.files.get(str(path), None):
            return res
        
        if ensure:
            inst = self.match_filetype(path)(path)
            self.register(inst)
            return inst
        
        return None
    
    def register(self,file:File):
        self.files[str(file.path)] = file
        with self.c() as c:
            if uid:=file.get_uid(c):
                self.resource_uid.add_uid(file.path, uid)
                # raise Exception((file, uid))
        self.item_appended(file)
    
    def unregister(self,file:File):
        with self.c() as c:
            uid = file.get_uid(c)
        path = str(file.path)
        if path in self.files.keys():
            del self.files[path] ## Remove all instances of file
        if self.resource_uid.exists(uid):
            self.resource_uid.remove(uid)
        if self.resource_uid.exists(path):
            self.resource_uid.remove(path)
        self.item_removed(file, uid, path)

    def populate_existing(self,):
        for path in self.project_root.rglob("*"):
            if not path.is_file():
                continue
            self.get_file(path, ensure=True)


    def exists(self, path:str|Path)->bool:
        return Path(self.get_abs(path)).exists()

    # @abstractmethod
    def load(self, file:File|Path|str)->File:
        ## Determine best secondary event/reactionary event resolutions?
        if not isinstance(file, File):
            file = self.get_file(file)
        with self.c() as c:
            file.load(c)
        return file 
             
    # @abstractmethod
    def save(self, file:File|Path|str)->None:
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    # @abstractmethod
    def dump(self, file:File|Path|str)->None:
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    # @abstractmethod
    def move(self, file:File|Path|str, path:str|Path):
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    # @abstractmethod
    def delete(self, file:File|Path|str):
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    def match_filetype(self, path:Path):
        for ft in self.file_types:
            for k in ft._file_match_extensions:
                if k == "*":
                    return ft
                if str(path).endswith(k):
                    return ft 
                
        raise KeyError("Could not match filetype to File!")

    def setup_fs_listener(self,):
        pass

    @contextmanager
    def c(self):
        if proj := getattr(self,"gd_project",None):
            with proj.c() as c:
                with c.w("file_db",self):
                    yield c
            return
        c = Context()
        with c.w("file_db",self):
            yield c

    def __getitem__(self,key)->File:
        if res:=self.get_file(key):
            return res
        raise KeyError(self, key)

    ## These are live env behavior features that the lion will concern himself with *later*
    # @abstractmethod
    # def _on_uid_changed(self, path, fr_uid, to_uid):
    #     file = self.get_file(path)
    #     for rfp in self.resource_uid.cached_references.get(fr_uid, tuple()):
    #         referencer = self.get_file(referencer)
    #         referencer.dep_uid_changed(file, path, fr_uid, to_uid)

    # @abstractmethod
    # def _on_fp_changed(self, fr_path, to_path):
    #     file = self.get_file(fr_path, False)
    #     if file is None:
    #         file = self.get_file(to_path, False)
    #     if file is None:
    #         raise Exception("wtf")
    #     for rfp in self.resource_uid.cached_references.get(fr_path, tuple()):
    #         referencer = self.get_file(referencer)
    #         referencer.dep_fp_changed(fr_path, to_path)
    # def _on_file_deleted():
    #     pass

#     def _on_file_uuid_set(self, file:File, fr_uuid:str, to_uuid:str):
#         if fr_uuid in self.by_uuid.keys():
#             del self.by_uuid[fr_uuid]
#         self.by_uuid[to_uuid] = file
        
#     def _on_file_path_set(self, file:File, fr_path:str, to_path:str):
#         if fr_path in self.by_path.keys():
#             del self.by_path[fr_path]
#         self.by_path[to_path] = file


#     ## "Tells" called by FileDb && initial file discovery
#     def tell_fs_created(self, path:str):
#         if file := self[path]:
#             file.fs_created(path)
#             self._queue_targets.append(file)
#         else: ## If untracked:
#             file = self.generate_file(path)
#             self.append(file)
#             self.fs_created(file)
#             self._queue_targets.append(file)

#     def tell_fs_modified(self, path:str):
#         if file := self[path]:
#             file.fs_modified()
#             self.fs_modified(file)
#             self._queue_targets.append(file)
#         else: ## If untracked:
#             file = self.generate_file(path)
#             self.append(file)
#             self.fs_created(file)
#             self._queue_targets.append(file)

#     def tell_fs_deleted(self, path:str):
#         if file := self[path]:
#             file.fs_deleted()
#             self.fs_deleted(file)
#             self.remove(file)
#             self._queue_targets.append(file)
#         else: ## If untracked:
#             pass

#     def tell_fs_moved(self, fr_path:str, to_path:str):
#         if file := self[fr_path]:
#             file.fs_moved(fr_path, to_path)
#             self._queue_targets.append(file)
#         elif file := self[to_path]: ## File already has corrected path
#             pass
#         else:
#             self.append(self.generate_file(fr_path))
    
#     def tell_fs_queue_empty(self):
#         for x in self._queue_targets:
#             x.fs_queue_empty()
#         self._queue_targets.clear()

#     class _EventHandler(_FileSystemEventHandler):
#         ''' Utility class, forward events to local signals '''
#         file_db : FileDb 
#         def __init__(self, file_db:FileDb):
#             self.file_db = file_db
#             super().__init__()

#         def on_created(self, event):
#             if event.is_directory: return
#             if not self.file_db.file_filter(event.src_path): return
#             self.file_db.tell_fs_created(event.src_path)
#             self._check_empty()
        
#         def on_modified(self, event):
#             if event.is_directory: return
#             if not self.file_db.file_filter(event.src_path): return
#             self.file_db.tell_fs_modified(event.src_path)
#             self._check_empty()
        
#         def on_deleted(self, event):
#             if event.is_directory: return
#             if not self.file_db.file_filter(event.src_path): return
#             self.file_db.tell_fs_deleted(event.src_path)
#             self._check_empty()

#         def on_moved(self, event):
#             if event.is_directory: return
#             if not self.file_db.file_filter(event.src_path): return
#             self.file_db.tell_fs_moved(event.src_path, event.dest_path)
#             self._check_empty()

#         def _check_empty(self):
#             if self.file_db._observer._event_queue.is_empty():
#                 self.file_db.tell_fs_queue_empty()