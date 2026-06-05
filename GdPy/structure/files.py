from typing import Type, Callable

from .core import File, GdType, GdClassDef, GdPropertyDef, GdSignalDef, GdParser
from .core.primitives import Context
from .core.core import GdResource
from .standard_parser import gdparser
from .secondary_transformer import SecondaryTransfomer

class FileTres[T:GdResource](File):

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

    class _DefTransformer[I:GdType,T:list[GdClassDef]](SecondaryTransfomer):
        ''' Local transfomer for results of GdPy/tools/godot/class_exporter '''

        def matcher(self, item:GdType)->Callable:
            if ref := item.properties.get("script"):
                if ref.value.path.endswith("class_data.gd"):
                    return self.class_data
                if ref.value.path.endswith("property_data.gd"):
                    return self.property_data
                if ref.value.path.endswith("signal_data.gd"):
                    return self.signal_data
                if ref.value.path.endswith("class_db.gd"):
                    return self.class_db
            return self.__default__
        
        def class_data(self, val:GdResource)->GdClassDef:
            pass
        
        def property_data(self, val:GdResource)->GdPropertyDef:
            pass
        
        def signal_data(self, val:GdResource)->GdSignalDef:
            pass
        
        def class_db(self, val:GdResource)->list[GdClassDef]:
            pass
            
    def get_definitions(self)->list[GdClassDef]:
        assert(self.data)
        transformer = self._DefTransformer() 
        return transformer.transform(self.data)
    
        

files : tuple[Type[File]] = (
    FileClassDefinition,
    )
