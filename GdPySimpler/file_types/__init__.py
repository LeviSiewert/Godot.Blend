from ..core.structure import _Resource, _File, _ResourceFile, Reference, FileRef

from ..core.settings import ResourceSettings

from ..transformers.tscn import( 
    gd_to_py_transformer, 
    GdToPyContext,
    py_to_gd_transformer, 
    PyToGdContext,
)

class FileGodot(_ResourceFile):
    extensions = ("tscn","tres","import","godot")
    
    def convert_fr_disk(self, data:str):
        c = GdToPyContext()
        return gd_to_py_transformer(c, data)
    
    def convert_to_disk(self, data):
        c = PyToGdContext()
        return py_to_gd_transformer(c, data)


class FileTxt(_File):
    ''' string container '''
    extensions = ("uid","txt","md")

    def convert_fr_disk(self, data:str):
        return data

    def convert_to_disk(self, data):
        return data


class FileScriptModule(_File):
    ''' Resource Tranformer extension script, keyed to an env_id by "*" 
    Plan: 
    - Key to UID/Class_ID/Script via;
        - filepath
        - contents (when loaded)
    - Defer load until explicitly requested
        - In user Env: Hash contents and raise/req when changed?
        - Security should be respected, but there *are* scripts.
    - Contents provide modules that give TransformerRulesets for the env (and other env hooks)
    '''

    extensions = (".gd.*.py",) 
    uid_file : Reference[str, FileTxt]

    def __setup__(self):
        super().__setup__()
        self.uid_file = FileRef(None)

class FileScript(_File):
    extensions = ("gd", "py") 
    uid_file : Reference[str, FileTxt]
    
    def __setup__(self):
        super().__setup__()
        self.uid_file = FileRef(None)
    
    def __init__(self, path):
        super().__init__(path)
        self.uid_file.store_address(path+".uid")

    def get_uid():
        pass

class FileGeneric(_ResourceFile):
    @classmethod
    def matches_filepath(cls, filepath):
        return True

    def convert_fr_disk(self, data):
        return data
    
    def convert_to_disk(self, data):
        return data

class _FileForeign(_ResourceFile):
    ''' If used: generic placeholder
    File type that is imported at runtime into a resource format. Raise error for the moment 
    '''
    extensions = (
        *("gltf","glb","dae","obj","fbx","blend"),
        *("bmp","dds","ktx","exr","hdr","jpg","png","tga","webp"),
        *("svg"),
        *("wav","ogg","mp3"),
    )
    import_file : _ResourceFile[FileGodot]

    def convert_fr_disk(self, data:str):
        raise NotImplementedError("unsupported FileForeign Resource:", self.path.addr)
    
    def convert_to_disk(self, data):
        raise NotImplementedError("unsupported FileForeign Resource:", self.path.addr)
    

_all = (
    FileGodot,
    FileTxt,
    FileScriptModule,
    FileScript,
    FileGeneric,
    _FileForeign,
)