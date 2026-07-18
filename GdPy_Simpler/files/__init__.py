from ..core.structure import File, Resource, Node, FileRef
from ..transformer.tscn import gd_to_py_transformer, py_to_gd_transformer

from typing import Any


class FileText(File):
    ''' Generic text Accessor '''
    _extensions_ = ("txt",)


class FileUid(File):
    ''' Uid provider stored as seperate file '''
    _extensions_ = ("uid",)


class FileGeneric(File):
    ''' Generic non-internally covered binary object 
    External UID via `.ext.import`
    '''
    _extensions_ = ("gltf", "glb",)

    import_file : FileRef[FileUid]

    def __setup__(self):
        super().__setup__()
        self.import_file = FileRef(context = self.context)
        def _sync(addr:str):
            self.import_file.set_key(addr.strip(".import"))
        self.filepath.key_updated.connect(_sync)


class FileScript(File):
    _extensions_ = ("gd",)

    uid_file : FileRef[FileUid]

    def __setup__(self):
        super().__setup__()
        self.uid_file = FileRef(context = self.context)
        def _sync(addr:str):
            self.uid_file.set_key(addr.strip(".uid"))
        self.filepath.key_updated.connect(_sync)


class FileTscn(File):
    ''' Text Scene Accessor '''
    _extensions_ = ("tscn",)

    def _transform_to_disc(self,data:Node)->Any:
        raise NotImplementedError()
    
    def _transform_fr_disc(self,data:str)->Node:
        raise NotImplementedError()


class FileTres(File):
    ''' Text Resource Accessor '''
    _extensions_ = ("tres",)

    def _transform_to_disc(self,data:Resource)->Any:
        raise NotImplementedError()
    
    def _transform_fr_disc(self,data:str)->Resource:
        raise NotImplementedError()


class FileSettings(File):
    ''' Text Resource w/ Section subtype '''
    _extensions_ = ("godot","import")

    def _transform_to_disc(self,data:Resource)->Any:
        raise NotImplementedError()
    
    def _transform_fr_disc(self,data:str)->Resource:
        raise NotImplementedError()