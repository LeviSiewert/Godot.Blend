import re
from typing import Type, Callable

from .core import File, GdType, GdClassDef, GdPropertyDef, GdSignalDef, GdParser, FsEvent
from .core.primitives import Context, CacheTreeNode
from .core import GdResource
from ._standard_parser import gdparser


class FileUnsupported(File):
    _file_match_priority = 10
    _file_match_extensions = ("*",)
    def get_uid(self, c):
        if str(self.path).endswith(".import") or str(self.path).endswith(".uid"):
            return None
        if file := c.file_db.get().get_file(str(self.path) + ".import", ensure=True, null_ok=True):
            return file.rep_uid()
        if file := c.file_db.get().get_file(str(self.path) + ".uid", ensure=True, null_ok=True):
            return file.rep_uid()
        return None
    def load(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def save(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def dump(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def delete(self, c:Context):
        raise Exception("file type not supported,", self.path)
        
    def fsevent_bundle(self, c:Context, event:FsEvent, is_reaction:bool)->tuple[File]:
        if is_reaction: return tuple()
        return (str(self.path)+".import", str(self.path)+".uid")


class FileTres[T:GdResource](File):
    _file_match_priority = 0
    _file_match_extensions = ("tres",)
    _gd_parser_start_key : str = "file_resource"    
    cache_tree : CacheTreeNode = None

    def get_uid(self, c):
        if not (self.data is None):
            return self.data.uid
        with open(self.path) as f:
            for ln in f:
                return re.search('uid="([^"]+|$)"', ln).group(1)
            return None

    def load(self, context:Context):

        with context.w("file", self):
            self.cache_tree = CacheTreeNode(self, self._cache_layers)
            assert(self.path.exists())
            text = self.path.read_text()
            self.data = gdparser.parse(context, text, cache_tree=self.cache_tree, start=self._gd_parser_start_key)
            self.cache_tree.call("postload_extresource", "postload", context)
            self.cache_tree.call("postload_nodepath", "postload", context)
            self.cache_tree.call("postload_subresource", "postload", context)
            self.cache_tree.call("postload_rid", "postload", context)
            self.data_loaded()

    def save(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def dump(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def delete(self, c:Context):
        raise Exception("file type not supported,", self.path)

class FileTscn(FileTres):
    _file_match_priority = 0
    _file_match_extensions = ("tscn","escn")
    _gd_parser_start_key = "file_tscn"

    def load(self, context:Context):
        with context.w("file", self):
            res = super().load(context)
            self.cache_tree.call("nodes", "tree", context)


class FileClassDefinition(FileTres):
    _file_match_priority = -1
    _file_match_extensions = ("class_definitions.tres")
    _gd_parser_start_key = "file_resource"
  
    def get_definitions(self)->list[GdClassDef]:
        if self.data is None:
            self.load()
        return []

    
class FileGodotProject(FileTres):
    _file_match_priority = 0
    _file_match_extensions = ("godot",)
    _gd_parser_start_key = "file_settings"

    def get_uid(self, c:Context)->str:
        return None
    
    def load(self, context):
        return super().load(context)
    

class FileImport(FileTres):
    _file_match_priority = 0
    _file_match_extensions = ("import",)
    _gd_parser_start_key = "file_settings"

    def get_uid(self, c:Context)->str:
        return None
    
    def rep_uid(self,)->str:
        if not (self.data is None):
            return self.data.uid
        with open(self.path) as f:
            for ln in f:
                if group := re.search('uid="([^"]+|$)"', ln):
                    return group.group(1)
        return None


class FileUid[T:str](File):
    _file_match_priority = 0
    _file_match_extensions = ("uid",)
    
    def get_uid(self, c:Context)->str:
        return None
    
    def rep_uid(self,)->str:
        return self.path.read_text().strip()
    
    def load(self, context:Context):
        self.data = self.path.read_text()
    def save(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def dump(self, c:Context):
        raise Exception("file type not supported,", self.path)
    def delete(self, c:Context):
        raise Exception("file type not supported,", self.path)


files = (
    FileUnsupported,
    FileTres,
    FileTscn,
    FileUid,
    FileImport
    )
