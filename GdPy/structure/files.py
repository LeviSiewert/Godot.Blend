from typing import Type, Callable

from .core import File, GdType, GdClassDef, GdPropertyDef, GdSignalDef, GdParser
from .core.primitives import Context, CacheTreeNode
from .core.core import GdResource
from .standard_parser import gdparser

from .secondary_transformer import SecondaryTransfomer


class FileTres[T:GdResource](File):
    cache_tree : CacheTreeNode

    def load(self, context:Context, *args, **kwargs):
        with context.w("file", self):
            self.cache_tree = CacheTreeNode(self, self._cache_layers)
            assert(self.path.exists())
            text = self.path.read_text()
            self.data = gdparser.parse(context, text, cache_tree=self.cache_tree, start="file_resource")
            self.cache_tree.call("references","attach",context)
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
    
    @classmethod
    def matches_file(cls, abs_path, rel_path):
        return rel_path == ".PyGd/class_definitions.tres"

    class _DefTransformer[I:GdType,T:list[GdClassDef]](SecondaryTransfomer):
        ''' Modified transfomer for results of GdPy/tools/godot/class_exporter '''

        def transform(self, root:I|GdType, *args, **kwargs)->T:
            if not isinstance(root, GdType): 
                raise TypeError()
            res = self.matcher(root)(root, *args, **kwargs)
            return res
    
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
            p = val.properties
            res = GdClassDef.construct(
                name        = p["name"],
                path        = p["path"],
                c_extends   = p["c_extends"],
                properties  = self.transform_each(p["properties"]) ,
                signals     = self.transform_each(p["signals"]) ,
                is_abstract = p["is_abstract"],
                language    = p["language"],
            )
            return res
        
        def property_data(self, val:GdResource)->GdPropertyDef:
            p = val.properties
            res = GdPropertyDef.construct(
                default_value = p["default_value"],
                cls_name      = p["cls_name"],
                _type         = p["type"],
                hint_type     = p["hint_type"],
                hint_str      = p["hint_str"],
                usage         = p["usage"],
            )
            return res
        
        def signal_data(self, val:GdResource)->GdSignalDef:
            p = val.properties
            res = GdSignalDef.construct(
                args         = p["args"], 
                default_args = p["default_args"], 
                flags        = p["flags"], 
                _id          = p["_id"], 
                name         = p["name"], 
            )
            return res
        
        def class_db(self, val:GdResource)->list[GdClassDef]:
            return self.transform_each(val.properties["classes"])
            
    def get_definitions(self)->list[GdClassDef]:
        assert(self.data)
        transformer = self._DefTransformer() 
        return transformer.transform(self.data)
    
        

files : tuple[Type[File]] = (
    FileClassDefinition,
    )
