
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Type
from .primitives import Signal, SignalContainer, Collection, Context
from pathlib import Path
from watchdog.events import FileSystemEventHandler as _FileSystemEventHandler#type:ignore
from watchdog.observers import Observer as _Observer #type:ignore
from contextlib import contextmanager
from contextvars import ContextVars
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

    @abstractmethod
    def exists(self, path_or_uid)->bool:
        pass

    @abstractmethod
    def to_path(self, path)->str:
        pass

    @abstractmethod
    def to_uid(self, path)->str:
        pass

    @abstractmethod
    def add_uid(self, path, uid)->str:
        pass

    @abstractmethod
    def rem_uid(self, path_or_uid:str)->str:
        pass

class File[T:Any](ABC, SignalContainer):
    ''' Implimentation of File level abstraction
    Registered to FileDB at project construction
    Handles pipeline loading file types into python
        - References may be defered
    Forwards file system signals
    Declares dependencies for moving asc files
    '''
    
    fs_created : Signal
    fs_modified : Signal
    fs_deleted : Signal
    fs_moved : Signal[str, str]
    fs_queue_empty : Signal

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


class FileDb(ABC, SignalContainer):
    ''' Implimentation of project filesystem level abstraction 
    Matches Type[File] to files being loaded
    Watches & Signals filesystem changes (within project scope)
    Handles file movement dependencies
    '''

    item_added : Signal[Any]
    item_removed : Signal[Any]

    files : dict[str, File]
    file_types : list[Type[File]]
    project_root : Path

    gd_project : Any

    def __init__(self, project_root:Path, file_types:list[Type[File]]):
        self.project_root = project_root
        self.file_types = sorted(file_types, key = lambda x: x._file_match_priority)
        self.resource_uid = ResourceUID()
        self.setup_fs_listener()
        super().__init__()

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

    def get_file(self, value:str|Path, ensure:bool=True)->File|None:

        path = Path(self.get_abs(value))

        if not path.exists():
            raise KeyError("Could not find filepath", path)

        if res := self.files.get(str(path), None):
            return res
        
        if ensure:
            inst = self.match_filetype(path)(path)
            self.register(inst)
            return inst
        
        return None
    
    def register(self,file:File):
        self.files[str(file.path)] = file
        if uid:=file.get_uid():
            self.resource_uid.add(file.path, uid)
        self.item_appended(file)
    
    def unregister(self,file:File):
        uid = file.get_uid()
        path = str(file.path)
        if path in self.files.keys():
            del self.files[path] ## Remove all instances of file
        if self.resource_uid.exists(uid):
            self.resource_uid.remove(uid)
        if self.resource_uid.exists(path):
            self.resource_uid.remove(path)
        self.item_removed(file, uid, path)

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


    @abstractmethod
    def exists(self, path:str|Path)->bool:
        return not (self.get_abs(path) is None)

    @abstractmethod
    def get_if_exists(self, paths:tuple[File|str|Path])->tuple[File]:
        res = []
        for x in paths:
            if isinstance(x,File):
                res.append(x)
                continue
            else:
                _t = self.get_file(x)
                if _t is None: 
                    continue 
                res.append(_t)
        return tuple(res)

    @abstractmethod
    def load(self, file:File|Path|str)->File:
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    @abstractmethod
    def save(self, file:File|Path|str)->None:
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    @abstractmethod
    def dump(self, file:File|Path|str)->None:
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    @abstractmethod
    def move(self, file:File|Path|str, path:str|Path):
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    @abstractmethod
    def delete(self, file:File|Path|str):
        ## Determine best secondary event/reactionary event resolutions?
        pass
             
    def match_filetype(self, path):
        for ft in self.file_types:
            for k in ft._file_match_extensions:
                if k == "*":
                    return ft
                if path.endswith(k):
                    return ft 
                
        raise KeyError("Could not match filetype to File!")

    def setup_fs_listener(self,):
        pass



# class File[T:Any](ABC, SignalContainer):
#     _cache_layers = ("*",)
#     _context_key = "file"

#     _match_priority : int = 0

#     @classmethod
#     @abstractmethod
#     def matches_file(cls, abs_path:str, rel_path:str)->dict:
#         return False
    
#     uuid : str = None
#     def get_uuid(self,):pass
#     def set_uuid(self,value):pass
#     uuid_set : Signal[str, str] #Fr, To

#     path : str
#     def get_path(self,):pass
#     def set_path(self,value):pass
#     path_set : Signal[str, str] #Fr, To

#     data : T = None
#     data_loaded : Signal[T]
#     data_dumped : Signal
#     data_deleted : Signal

#     ## Triggered by FileDb container
#     fs_created : Signal
#     fs_modified : Signal
#     fs_deleted : Signal
#     fs_moved : Signal[str, str]
#     fs_queue_empty : Signal

#     def __init__(self, path:str):
#         self.path = path
#         super().__init__()

#     @abstractmethod
#     def load(self, context:Context, *args, **kwargs):
#         pass

#     @abstractmethod
#     def save(self,context:Context, *args, **kwargs):
#         pass

#     @abstractmethod
#     def dump(self,):
#         pass

#     @abstractmethod
#     def delete(self,):
#         pass

# class FileDb[T:File](Collection):
#     # TODO: Properly support all 3 paths of res:// uid:// {absolute} 

#     root : Path
#     file_types : list[Type[File]]
    
#     _observer : _Observer

#     uuid_set : Signal[T,str,str]
#     path_set : Signal[T,str,str]

#     by_uuid : dict[str:T]
#     by_path : dict[str:T]

#     fs_created : Signal[str]
#     fs_modified : Signal[str]
#     fs_deleted : Signal[str]
#     fs_moved : Signal[str, str]
#     fs_queue_empty : Signal
#     _queue_targets : list[File]


#     def __init__(self, root:Path, file_types:list[Type[File]]):
#         self.root = root        
#         self.file_types = sorted(file_types, key=lambda x: x._match_priority)

#         self.by_uuid = {}
#         self.by_path = {}
#         self._queue_targets = []
        
#         self._observer = _Observer()
#         self._observer.schedule(self._EventHandler(self), path=root, recursive=True)
#         self._observer.start()
        
#         super().__init__()
#         self.uuid_set.connect(self._on_file_uuid_set)
#         self.path_set.connect(self._on_file_path_set)
#         self.populate_existing()

#     def populate_existing(self,):
#         for path in self.root.rglob("*"):
#             if not path.is_file():
#                 continue
#             if not self.file_filter(path):
#                 continue
#             if self[path]:
#                 continue
#             file = self.generate_file(path)
#             if file: 
#                 self.append(file)

#     def file_filter(self, path:str)->bool:
#         ''' Override; Env based. Source data from self.file_types '''
#         return True

#     def generate_file(self, path:Path)->File:
#         ''' Override; Env based. Source data from self.file_types 
#         default behavior is asking input file_types
#         '''
#         ##TODO: Generate warnings here
#         for x in self.file_types:
#             if x.matches_file(path, path.relative_to(self.root)):
#                 return x(path)
#         return None

#     def _integrate(self,item:T):
#         if item.uuid: self.by_uuid[item.uuid] = item
#         if item.path: self.by_path[item.path] = item
#         self.uuid_set.connect(item.uuid_set.forward)
#         self.path_set.connect(item.path_set.forward)
    
#     def _disintegrate(self,item:T):
#         self.uuid_set.disconnect(item.uuid_set.forward)
#         self.path_set.disconnect(item.path_set.forward)
#         self.by_uuid.rem(item.uuid)
#         self.by_path.rem(item.path)

#     def __getitem__(self, key)->T:
#         return self.by_uuid.get(key, self.by_path.get(key, None))
    
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