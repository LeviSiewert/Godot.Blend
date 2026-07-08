from __future__ import annotations

from typing import Any, Type
from fsspec import AbstractFileSystem
from contextlib import contextmanager
from contextvars import ContextVar


from .collections import (
    Key, 
    Collection as _Collection, 
    Reference as _Reference,
)
from .context import StructContext as _StructContext
from .signals import Signal

class StructContext(_StructContext):
    project : Project
    file : _File
    resource : _Resource
    subresource : Any

class _ContextualReference(_Reference):
    _context_target : str
    _collection_key : str

    def __setup__(self):
        self.context = StructContext()
        self.context.callback(self._context_target, self._on_context_updated)

    def __init__(self, address = None, /, context:StructContext=None, key_id = None, cached_value = None, collection=None):
        super().__init__(key_id, address, cached_value, collection)
        self.context.set_extends(context)

    def _on_context_updated(self, ctx_obj:object):
        if ctx_obj is None:
            self.set_collection(None)
        else:
            self.set_collection(getattr(ctx_obj, self._collection_key))


class Project():
    context : StructContext
    files : FileCollection
    resources : ResourceCollection

    file_system : AbstractFileSystem

    disc_file_created : Signal[str]
    disc_file_deleted : Signal[str]
    disc_file_updated : Signal[str]
    disc_file_moved : Signal[str,str]

    def __setup__(self):
        self.context = StructContext(project=self)
        self.files = FileCollection(self.context)
        self.resources = ResourceCollection(self.context)
        
        self.disc_file_created = Signal(self)
        self.disc_file_deleted = Signal(self)
        self.disc_file_updated = Signal(self)
        self.disc_file_moved = Signal(self)

    def __init__(self, file_system:AbstractFileSystem, file_types:list[Type[_File]], search:bool=True):
        self.__setup__()
        self.file_system = file_system
        self.file_types = file_types
        if search:
            self.search()

    @classmethod
    def construct(cls, file_system:AbstractFileSystem=None, file_types:list[Type[_File]]=tuple(), search:bool=False, **kwargs):
        self = cls(file_system, file_types, search=False)

        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise AttributeError(obj=self, name=k)
            setattr(self, v)

        if search:
            self.search()

        return self

    def search(self):
        # search file_system, populate self.files, update all uid paths on files.
        raise NotImplementedError()

    def match_filetype(self, filepath:str)->Type[_File]:
        ## find first match from self.file_types and return
        raise NotImplementedError()

    def filter_folder(self, folder:list[str])->list[str]:
        ## pass folder through all self.file_types
        raise NotImplementedError()


class _FileMetadata():
    __slots__ = ("last_imported", "last_exported", "file")
    file : _File

    last_imported : int|None = None
    last_exported : int|None = None

    def __init__(self, file:_File):
        self.file = file


class _File():
    context : StructContext
    metadata : _FileMetadata

    path : Key[str]
    data : Any|None

    lock : ContextVar[bool]
        # If locked, do not interpret input signals.

    def __setup__(self):
        self.context = StructContext(file=self)
        self.context.callback("project", self._on_project_updated)

        self.lock = ContextVar("locked", default=False)
        self.metadata = _FileMetadata(self)
        self.path = Key(self, "path", None)
        self.data = None

    _project_cached : Project = None

    def _on_project_updated(self, project:Project|None):
        if self._project_cached:
            self._project_cached.disc_file_created.disconnect(self._on_disc_created_filter)
            self._project_cached.disc_file_deleted.disconnect(self._on_disc_deleted_filter)
            self._project_cached.disc_file_updated.disconnect(self._on_disc_updated_filter)
            self._project_cached.disc_file_moved.disconnect(self._on_disc_moved_filter)
        
        self._project_cached = project
        if project:
            self._project_cached.disc_file_created.connect(self._on_disc_created_filter)
            self._project_cached.disc_file_deleted.connect(self._on_disc_deleted_filter)
            self._project_cached.disc_file_updated.connect(self._on_disc_updated_filter)
            self._project_cached.disc_file_moved.connect(self._on_disc_moved_filter)
        

    def __init__(self, path:str, data:Any=None):
        self.__setup__()
        self.path.set(path)
        self.data = data

    def __colkeys__(self,):
        return (self.path, )

    def get_file_system(self):
        return self.context.project.file_system

    @contextmanager
    def locked(self, lock=True, update_meta=False):
        t = self.lock.set(lock)
        yield
        if update_meta:
            self.update_metadata()
        t = self.lock.reset(t)

    def update_metadata(self):
        fs = self.get_file_system()
        #TODO
        raise NotImplementedError()


    def read(self, force=False):
        fs = self.get_file_system()
        raise NotImplementedError()
        self.update_metadata()


    def write(self):
        assert not (self.data is None)
        fs = self.get_file_system()
        raise NotImplementedError()

    def _on_disc_created_filter(self, fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_created_filter(fp, *args)
    def _on_disc_created(self, fp):
        fs = self.get_file_system()
        raise NotImplementedError()
            

    def _on_disc_updated_filter(self,fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_updated_filter(fp, *args)
    def _on_disc_updated(self, fp):
        fs = self.get_file_system()
        raise NotImplementedError()
    

    def move(self):
        fs = self.get_file_system()
        raise NotImplementedError()
    
    def _on_disc_moved_filter(self,fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_moved_filter(fp, *args)
    def _on_disc_moved(self, fr:str, to:str):
        fs = self.get_file_system()
        raise NotImplementedError()


    def delete(self):
        fs = self.get_file_system()
        raise NotImplementedError()

    def _on_disc_deleted_filter(self,fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_deleted_filter(fp, *args)
    def _on_disc_deleted(self,fp):
        fs = self.get_file_system()
        raise NotImplementedError()


    @classmethod
    def construct(cls, path, /, data:Any=None, _defered_write:bool=False, _defered_write_data:Any=None, **kwargs):
        self = cls(path)

        if not (data is None):
            self.data = data

        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise AttributeError(obj=self, name=k)
            setattr(self, v)

        if _defered_write:
            def _write(prj):
                if _defered_write_data:
                    fs = self.get_file_system()
                    fs.write_text(self.path.add, _defered_write_data)
                    return
                self.write()
            self.context.callback("project", _write, once=True, )

        return self
        

class _FileResource(_File):
    context : StructContext
    path : Key[str]
    # _uid : Key[str] ## Pre-Fetched / Cached
    data : _Reference[str, _Resource]
    
    def __setup__(self):
        self.metadata = _FileMetadata(self)
        self.path = Key(self, "path", None)
        self.context = StructContext(file=self)
        self.data = ResourceRef(context=self.context)

    def __init__(self, path:str):
        self.__setup__()
        self.path.set(path)

    @classmethod
    def construct(cls, path, /, data_or_uid:_Resource|str, _defered_write:bool=False, _defered_write_data:Any=None, **kwargs):
        self = super().construct(path, data=None, _defered_write=_defered_write, _defered_write_data=_defered_write_data)
        
        if isinstance(data_or_uid, str):
            self.data.store_address(data_or_uid)
        elif isinstance(data_or_uid, _Resource):
            self.data.store_value(data_or_uid)

        return self
        

class FileCollection(_Collection):
    unique_keys = ("path",)

    def key_matcher(self, addr):
        return "path"

class FileRef(_ContextualReference):
    _context_target : str = "project"
    _collection_key : str = "files"


class _Resource():
    context : StructContext
    uid : Key[str, _FileResource]
    file : _Reference[str, _FileResource]
    
    def __setup__(self):
        self.uid = Key(self, "uid", None)
        self.context = StructContext(file=self)
        self.data = ResourceRef(context=self.context)

    def __init__(self, uid=None):
        self.__setup__()
        self.uid.set(uid)

    @classmethod
    def construct(cls,):
        raise NotImplementedError()

    def __colkeys__(self,):
        return (self.uid, )

    def write(self):
        assert self.file.get()
        raise NotImplementedError()
    
    def _on_disc_created(self):
        ## TODO: Signal forwarding from file.
        ## Uncertain behavior here as
        raise NotImplementedError()
    
    def write_update(self,):
        assert self.file.get()
        raise NotImplementedError()

    def _on_disc_updated(self,):
        ## TODO: Signal forwarding from file.
        ## File lock will prevent this from being forwarded
        ## Import-dif.
        raise NotImplementedError()
    
    def _on_disc_moved(self,):
        ## TODO: Signal forwarding from file.
        ## File lock will prevent this from being forwared
        ## Disc moving should not impact local
        raise NotImplementedError()
    
    def _on_disc_deleted(self,):
        ## TODO: Signal forwarding from file.
        ## File lock will prevent this from being forwared
        ## Unknown desired behavior. Perhaps removal and cleanup of self?
        raise NotImplementedError()

class ResourceCollection(_Collection):
    unique_keys = ("uid",)

    def key_matcher(self, addr):
        return "uid"

class ResourceRef(_ContextualReference):
    _context_target : str = "project"
    _collection_key : str = "references"


