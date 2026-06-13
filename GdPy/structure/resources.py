from .core import GdResource
from .sub_resources import *
from .sub_resource_collections import *

class _GdResource(GdResource):

    def __init__(self, _construct:bool=False):
        if not _construct:
            self.setup()
        super().__init__()

    @abstractmethod
    def setup(self,):
        pass

class GdResourceFileTres(_GdResource, ClassDbEnforcable):
    ext_resources : CollectionExtRes 
    sub_resources : CollectionSubRes

    @classmethod
    def lark_keys(cls):
        return ("file_resource")
    
    @classmethod
    def parse_lark(cls, key, tfrm, header:PropertyCollection, ext_res:CollectionExtRes, sub_res:CollectionSubRes, prim_res:PropertyCollection):
        self = cls(True)
        for k,v in header.items.items():
            if not hasattr(self,k):
                raise KeyError("Requires predefition of header attribute:", self,k)
            setattr(self,k,v)
        self.properties = prim_res
        self.ext_resources = ext_res
        self.sub_resources = sub_res
        return self

    def setup(self,):
        self.ext_resources=CollectionExtRes()
        self.sub_resources=CollectionSubRes()

    def get_struct_children(self):
        return (self.ext_resources, self.sub_resources)
        
class GdResourceFileScene(_GdResource): #, ClassDbEnforcable):
    format : int = None
    uid : str = None

    ext_resources : CollectionExtRes
    sub_resources : CollectionSubRes
    node_resources : CollectionNodeRes
    edit_resources : CollectionEditRes

    @classmethod
    def lark_keys(cls):
        return ("file_tscn",)

    @classmethod
    def parse_lark(cls, key, tfrm, header:PropertyCollection, ext_res:CollectionExtRes, sub_res:CollectionSubRes, node_res:CollectionNodeRes, edit_res:CollectionEditRes):
        self = cls(True)
        # raise Exception(header.items)
        for k,v in header.items.items():
            if not hasattr(self,k):
                raise KeyError("Requires predefition of header attribute:", self,k)
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

    def get_struct_children(self):
        return (self.ext_resources,self.sub_resources,self.node_resources,self.edit_resources)

class GdResourceFileImport(_GdResource):
    cat_resources : CollectionCatRes
    config_version : int = None

    @classmethod
    def lark_keys(cls):
        return ("file_settings",)

    def setup(self,):
        self.cat_resources = CollectionCatRes()

    @classmethod
    def parse_lark(cls, key, tfrm, properties:PropertyCollection, cat_res:CollectionCatRes):
        self = cls(True)
        for k,v in properties.items.items():
            if not hasattr(self,k):
                raise KeyError("Requires predefition of header attribute:", self,k)
            setattr(self,k,v)
        self.cat_resources = cat_res
        return self

    def get_struct_children(self):
        return (self.cat_resources)

_all = (
    GdResourceFileTres,
    GdResourceFileScene,
    GdResourceFileImport,
)