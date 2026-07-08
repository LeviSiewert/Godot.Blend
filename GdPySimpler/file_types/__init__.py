from ..core.structure import _File

# from ..core.settings import ResourceSettings
# from ..core.resources import
# from ..core.nodes import

# from ..transformers.tscn import( 
#     gd_to_py_transformer, 
#     GdToPyContext,
#     py_to_gd_transformer, 
#     PyToGdContext,
# )



class FileTxt(_File):
    ''' string container '''
    extensions = ("uid","txt","md")
    data : str = None

    def read(self, force=False):
        fs = self.get_file_system()
        if self.lock and (not force):
            raise Exception("Contextually locked file cannot have data read into! (Lock declares Python data priority)")
        with self.locked(update_meta=True):
            self.data = fs.read_text(self.path.addr)

    def write(self):
        fs = self.get_file_system()
        with self.locked(update_meta=True):
            fs.write_text(self.path.addr, self.data)

    def move(self, to):
        fs = self.get_file_system()
        raise NotImplementedError()

    def delete(self):
        fs = self.get_file_system()
        raise NotImplementedError()

class FileScript(_File):
    pass

_all = (
    FileTxt,
    FileScript,
)

# class FileGodot(_FileResource):
#     extensions = ("tscn","tres","import","godot")
    
#     def convert_fr_disk(self, data:str):
#         c = GdToPyContext()
#         return gd_to_py_transformer(c, data)
    
#     def convert_to_disk(self, data):
#         c = PyToGdContext()
#         return py_to_gd_transformer(c, data)


# class FileTxt(_File):
#     ''' string container '''
#     extensions = ("uid","txt","md")
#     data : str = None

#     def load_data(self,):
#         fs = self.context.project.file_system 
#         return self.data
#         #TODO:
#         return self.convert_fr_disk(fs.read_text(self.path.addr))

#     def write_data(self,):
#         fs = self.context.project.file_system 
#         return fs.write_text(self.path.addr, self.convert_to_disk(self.data))

#     def convert_fr_disk(self, data:str)->str:
#         return data

#     def convert_to_disk(self, data:str)->str:
#         return data


# class FileScriptModule(_File):
#     ''' Resource Tranformer extension script, keyed to an env_id by "*" 
#     Plan: 
#     - Key to UID/Class_ID/Script via;
#         - filepath
#         - contents (when loaded)
#     - Defer load until explicitly requested
#         - In user Env: Hash contents and raise/req when changed?
#         - Security should be respected, but there *are* scripts.
#     - Contents provide modules that give TransformerRulesets for the env (and other env hooks)
#     '''

#     extensions = (".gd.*.py",) 
#     uid_file : Reference[str, FileTxt]

#     def __setup__(self):
#         super().__setup__()
#         self.uid_file = FileRef(None, context=self.context)

# class FileScript(_FileResource):
#     extensions = ("gd", "py") 
#     uid_file : Reference[str, FileTxt]
    
#     def __setup__(self):
#         super().__setup__()
#         self.uid_file = FileRef(None, context=self.context)
    
#     def __init__(self, path):
#         super().__init__(path)
#         self.uid_file.store_address(path+".uid")

#     def get_uid(self,)->str|None:
#         if file:=self.uid_file.get():
#             file:FileTxt
#             return file.load_data()
#         return None

# class FileGeneric(_FileResource):
#     @classmethod
#     def matches_filepath(cls, filepath):
#         return True

#     def convert_fr_disk(self, data):
#         return data
    
#     def convert_to_disk(self, data):
#         return data

# class _FileForeign(_FileResource):
#     ''' If used: generic placeholder
#     File type that is imported at runtime into a resource format. Raise error for the moment 
#     '''
#     extensions = (
#         *("gltf","glb","dae","obj","fbx","blend"),
#         *("bmp","dds","ktx","exr","hdr","jpg","png","tga","webp"),
#         *("svg"),
#         *("wav","ogg","mp3"),
#     )
#     import_file : _FileResource[FileGodot]

#     def convert_fr_disk(self, data:str):
#         raise NotImplementedError("unsupported FileForeign Resource:", self.path.addr)
    
#     def convert_to_disk(self, data):
#         raise NotImplementedError("unsupported FileForeign Resource:", self.path.addr)
    

# _all = (
#     FileGodot,
#     FileTxt,
#     FileScriptModule,
#     FileScript,
#     FileGeneric,
#     _FileForeign,
# )