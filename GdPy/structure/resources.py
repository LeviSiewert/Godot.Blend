from .core import GdResource, GdType, Context, GdClassDef, Collection
from typing import Type

class GdResourceFile(GdResource):
    sub_resources : Collection[GdResource]
    
    script_class : str
    format       : str
    type         : str
    uid          : str

    def __init__(self,
            type         : str,
            script_class : str,
            format       : str,
            uid          : str,
            properties : dict = None,
            sub_resources : Collection = None,
            ):
        self.type = type
        self.script_class = script_class
        self.format = format
        self.uid = uid
        super().__init__(properties)
        if self.sub_resources is None:
            self.sub_resources = Collection()
        else:
            self.sub_resources = sub_resources

    def attach_definition(self, context:Context):
        script = self.properties.get("script",None)
        if not script: return
        context.project.get().class_db[script]
        self.set_definition()

    def set_definition(self, class_def:GdClassDef):
        self.definition = class_def
        self.definition_updated(class_def)

class GdSubResource(GdResource):
    type : str
    id   : str

    def __init__(
            self,
            type : str,
            id   : str,
            properties : dict = None,
            ):
        self.type = type 
        self.id   = id
        super().__init__(properties)
   

    def attach_definition(self, context:Context):
        script = self.properties.get("script",None)
        if not script: return
        context.project.get().class_db[script]
        self.set_definition()

    def set_definition(self, class_def:GdClassDef):
        self.definition = class_def
        self.definition_updated(class_def)

class GdExtResource(GdResource):
    type : str
    uid  : str
    path : str
    id   : str

    def __init__(
            self,
            type : str,
            uid  : str,
            path : str,
            id   : str,
            properties : dict = None,
            ):
        self.type = type 
        self.uid  = uid  
        self.path = path 
        self.id   = id   
        super().__init__(properties)


class GdEditResource(GdResource):
    pass

_all : tuple[Type] = (
    GdResourceFile,
    GdSubResource,
    GdExtResource,
    GdEditResource,
)
