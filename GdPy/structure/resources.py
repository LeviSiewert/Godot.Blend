from .core import GdResource
from .sub_resources import *
from .sub_resource_collections import *

class _GdResource(GdResource):
    header : PropertyCollection

    def __init__(self, _construct:bool=False):
        if not _construct:
            self.setup()
        super().__init__()

    @abstractmethod
    def setup(self,):
        pass

class GdResourceFileTres(GdResource, ClassDbEnforcable):
    ext_resources : CollectionExtRes 
    sub_resources : CollectionSubRes

    @classmethod
    def lark_keys(cls):
        return ("file_resource")
    
    @classmethod
    def parse_lark(cls, key, tfrm, header:PropertyCollection, ext_res:CollectionExtRes, sub_res:CollectionSubRes, prim_res:PropertyCollection):
        self = cls(True)
        for k,v in header.items():
            assert(hasattr(k,v))
            setattr(self,k,v)
        self.properties = prim_res
        self.ext_resources = ext_res
        self.sub_resources = sub_res
        return self

    def setup(self,):
        self.ext_resources=CollectionExtRes()
        self.sub_resources=CollectionSubRes()
        
class GdResourceFileScene(GdResource, ClassDbEnforcable):
    ext_resources : CollectionExtRes
    sub_resources : CollectionSubRes
    node_resources : CollectionNodeRes
    edit_resources : CollectionEditRes

    @classmethod
    def lark_keys(cls):
        return ("file_tscn")

    @classmethod
    def parse_lark(cls, key, tfrm, header:PropertyCollection, ext_res:CollectionExtRes, sub_res:CollectionSubRes, node_res:CollectionNodeRes, edit_res:CollectionEditRes):
        self = cls(True)
        for k,v in header.items():
            assert(hasattr(k,v))
            setattr(self,k,v)
        self.ext_resources = ext_res
        self.sub_resources = sub_res
        self.node_resources = node_res
        self.edit_resources = edit_res
        return self

    def setup(self,):
        self.ext_resources = CollectionExtRes()
        self.sub_resources = CollectionSubRes()
        self.node_resources = CollectionNodeRes()
        self.edit_resources = CollectionEditRes()

class GdResourceFileImport(GdResource):
    ext_resources : CollectionExtRes
    cat_resources : CollectionCatRes

    @classmethod
    def lark_keys(cls):
        return ("file_settings")

    def setup(self,):
        self.ext_resources = CollectionExtRes()
        self.cat_resources = CollectionCatRes()

    @classmethod
    def parse_lark(cls, key, tfrm, ext_res:CollectionExtRes, cat_res:CollectionCatRes):
        self = cls(True)
        self.ext_resources = ext_res
        self.cat_resources = cat_res
        return self

_all = (
    GdResourceFileTres,
    GdResourceFileScene,
    GdResourceFileImport,
)