import re
from typing import Type, Callable

from .core import File, GdType, GdClassDef, GdPropertyDef, GdSignalDef, GdParser, FsEvent
from .core.primitives import Context, CacheTreeNode
from .core.core import GdResource
from .standard_parser import gdparser


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

# class FileTres[T:GdResource](File):
#     cache_tree : CacheTreeNode

#     def get_uid()

#     @classmethod
#     def matches_file(cls, abs_path, rel_path):
#         return abs_path.endswith(".tres")

#     def load(self, context:Context, *args, **kwargs):
#         with context.w("file", self):
#             self.cache_tree = CacheTreeNode(self, self._cache_layers)
#             assert(self.path.exists())
#             text = self.path.read_text()
#             self.data = gdparser.parse(context, text, cache_tree=self.cache_tree, start="file_resource")
#             self.cache_tree.call("references","attach",context)
#             self.data_loaded()
        
#     def save(self, context:Context, *args, **kwargs):
#         with context.w("file", self):
#             raise Exception("Not programmed in yet!")

#     def dump(self, context:Context):
#         del self.data
#         self.data_dumped()

#     def delete(self, context:Context):
#         raise Exception("Not programmed in yet!")

# class FileTscn[T:GdResource](FileTres):
#     @classmethod
#     def matches_file(cls, abs_path, rel_path):
#         return abs_path.endswith(".tscn")

# class FileImport(FileTres):
#     def internal_uid(self,):
#         pass

#     def load(self, context:Context, *args, **kwargs):
#         pass

#     def save(self, context:Context, *args, **kwargs):
#         pass

#     def dump(self, context:Context):
#         pass

#     def delete(self, context:Context):
#         pass

# class FileUid(File):
#     def internal_uid(self,):
#         pass

# class FileClassDefinition(FileTres):
    
#     @classmethod
#     def matches_file(cls, abs_path, rel_path):
#         return False
#     #     return rel_path == ".PyGd/class_definitions.tres"


#     class _DefTransformer[I:GdType,T:list[GdClassDef]](SecondaryTransfomer):
#         ''' Modified transfomer for results of GdPy/tools/godot/class_exporter '''

#         def transform(self, root:I|GdType, *args, **kwargs)->T:
#             if not isinstance(root, GdType): 
#                 raise TypeError()
#             res = self.matcher(root)(root, *args, **kwargs)
#             return res
    
#         def matcher(self, item:GdType)->Callable:
#             if ref := item.properties.get("script"):
#                 if ref.value.path.endswith("class_data.gd"):
#                     return self.class_data
#                 if ref.value.path.endswith("property_data.gd"):
#                     return self.property_data
#                 if ref.value.path.endswith("signal_data.gd"):
#                     return self.signal_data
#                 if ref.value.path.endswith("class_db.gd"):
#                     return self.class_db
#             return self.__default__
        
#         def class_data(self, val:GdResource)->GdClassDef:
#             p = val.properties
#             res = GdClassDef.construct(
#                 name        = p["name"],
#                 path        = p["path"],
#                 c_extends   = p["c_extends"],
#                 properties  = self.transform_each(p["properties"]) ,
#                 signals     = self.transform_each(p["signals"]) ,
#                 is_abstract = p["is_abstract"],
#                 language    = p["language"],
#             )
#             return res
        
#         def property_data(self, val:GdResource)->GdPropertyDef:
#             p = val.properties
#             res = GdPropertyDef.construct(
#                 default_value = p["default_value"],
#                 cls_name      = p["cls_name"],
#                 _type         = p["type"],
#                 hint_type     = p["hint_type"],
#                 hint_str      = p["hint_str"],
#                 usage         = p["usage"],
#             )
#             return res
        
#         def signal_data(self, val:GdResource)->GdSignalDef:
#             p = val.properties
#             res = GdSignalDef.construct(
#                 args         = p["args"], 
#                 default_args = p["default_args"], 
#                 flags        = p["flags"], 
#                 _id          = p["_id"], 
#                 name         = p["name"], 
#             )
#             return res
        
#         def class_db(self, val:GdResource)->list[GdClassDef]:
#             return self.transform_each(val.properties["classes"])
            
#     def get_definitions(self)->list[GdClassDef]:
#         assert(self.data)
#         transformer = self._DefTransformer() 
#         return transformer.transform(self.data)
    
        

# files : tuple[Type[File]] = (
#     FileUnsupported,
#     FileClassDefinition,
#     )
