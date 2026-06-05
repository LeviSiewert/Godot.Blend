from .core import File, GdClassDef, GdPropertyDef, GdSignalDef, GdParser
from .core.primitives import Context
from .standard import gdparser

from typing import Type

class FileTres(File):
    def load(self, context:Context, *args, **kwargs):
        with context.w("file", self):
            assert(self.path.exists())
            text = self.path.read()
            self.data = gdparser(context, text, start="tres")
            self.data_loaded()
        
    def save(self, context:Context, *args, **kwargs):
        with context.w("file", self):
            raise Exception("Not programmed in yet!")

    def dump(self, context:Context):
        del self.data
        self.data_dumped()

    def delete(self, context:Context):
        raise Exception("Not programmed in yet!")
    

class FileClassDefinition(FileTres):
    ## TODO: Load and transform

    def get_definitions(self)->list[GdClassDef]:
        assert(self.data)
        

files : tuple[Type[File]] = (
    FileClassDefinition,
    )
