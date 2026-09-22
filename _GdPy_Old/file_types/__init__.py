from __future__ import annotations

from typing import Any

from ..core.structure import _File, _FileResource, _Resource, FileRef

from ..core.settings import ResourceSettings
from ..core.resources import ResourceTres
from ..core.nodes import ResourceScene

from ..transformers.tscn import( 
    gd_to_py_transformer, 
    GdToPyContext,
    py_to_gd_transformer, 
    PyToGdContext,
    file_parser,
)


class FileTxt(_File):
    ''' string container '''
    extensions = ("uid","txt","md")
    data : str = None

class FileScript(_File):
    extensions = ("gd",)
    uid_file : FileRef
    ## TODO : Move should include uid_file
    ## TODO : import uid from settings file

    def __setup__(self):
        super().__setup__()
        self.uid_file = FileRef(context=self.context)

        ## synced .uid for future path updates.
        def _sync(addr):
            self.uid_file.store_address(addr+".uid")
        self.path.addr_updated.connect(_sync)


class _FileGodot(_FileResource):
    def _transform_to_disc(self,data:_Resource)->Any:
        c = PyToGdContext()
        c.project.set(self.context.resource)
        c.file.set(self)
        return py_to_gd_transformer.transform_tree(c, data)
    
    def _transform_fr_disc(self,data:str)->_Resource:
        c = GdToPyContext()
        c.project.set(self.context.resource)
        c.file.set(self)
        return gd_to_py_transformer.transform_tree(c, file_parser(data))

class FileTres(_FileGodot):
    extensions = ("tres",)

class FileTscn(_FileGodot):
    extensions = ("tscn",)

class FileImportSettings(_FileGodot):
    extensions = ("import",)
    data_file :  FileRef

    def __setup__(self):
        super().__setup__()
        self.data_file = FileRef(context=self.context)

        ## synced .uid for future path updates.
        def _sync(addr:str):
            self.data_file.store_address(addr.strip(".import"))
        self.path.addr_updated.connect(_sync)


class FileProject(_FileGodot):
    extensions = ("godot",)

class FileImported(_FileResource):
    extensions = ("*",)
    settings_file : FileRef #FileImportSettings
    ## TODO : Move should include settings_file
    ## TODO : import uid from settings file

    def __setup__(self):
        super().__setup__()
        self.import_file = FileRef(context=self.context)

        ## synced .uid for future path updates.
        def _sync(addr):
            self.import_file.store_address(addr+".import")
        self.path.addr_updated.connect(_sync)

    def _transform_to_disc(self,data:_Resource)->Any:
        raise NotImplementedError()
    
    def _transform_fr_disc(self,data:str)->_Resource:
        raise NotImplementedError()

_all = (
    FileTxt,
    FileScript,
    FileTres,
    FileTscn,
    FileImportSettings,
    FileProject,
    FileImported,
)
