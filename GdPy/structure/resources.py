from __future__ import annotations
from .core import GdResource, GdProperty, GdType, Context, GdClassDef, Collection, PropertyCollection, ClassDbEnforcable
from typing import Type
from contextlib import contextmanager

class SubresourceCollection[T:GdSubResource](Collection):
    items = []
    def __init__(self):
        self.items = []
        super().__init__()
    def _integrate(self, item:T):
        self.items.append(item)
    def _disintegrate(self, item:T):
        self.items.remove(item)
    def __getitem__(self, key)->T:
        return None
    def __setitem__(self, key)->T:
        return None

## Resource (File) Types:

class GdResourceFileTres(GdResource, ClassDbEnforcable):
    class_def : GdClassDef
    script_def : GdClassDef

    header_props : PropertyCollection
    properties : PropertyCollection
    sub_resources : SubresourceCollection[GdResource]
    ext_resources : SubresourceCollection[GdExtResource]

    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_resource",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_resource",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:dict[str,GdProperty], ext_res:list[GdExtResource], sub_res:list[GdSubResource], prim_resource:_GdResourceFileBody):
        self = cls()
        self.properties = _GdResourceFileBody.value
        self.header_props = header_props
        self.sub_resources.extend(sub_res)
        self.ext_resources.extend(ext_res)
        return self

    def __init__(self):
        self.header_props = PropertyCollection()
        self.properties = PropertyCollection()
        self.sub_resources = SubresourceCollection()
        self.ext_resources = SubresourceCollection()
        super().__init__()

    def get_struct_children(self)->list:
        res = []
        res.extend(self.header_props.values())
        res.extend(self.properties.values())
        res.extend(self.sub_resources.values())
        res.extend(self.ext_resources.values())
        return res


class GdResourceFileScene(GdResource):
    header_props : PropertyCollection
    properties : PropertyCollection
    ext_resources : SubresourceCollection[GdExtResource]
    sub_resources : SubresourceCollection[GdSubResource|GdSubResourceNode]
    edit_resources : SubresourceCollection[GdEditResource]
    
    root : GdSubResourceNode

    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_resource",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_scene",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:dict[str,GdProperty], ext_res:list[GdExtResource], sub_res:list[GdSubResource], edit_res:list[GdSubResource]):
        self = cls()
        self.header_props = header_props
        self.ext_resources.extend(ext_res)
        self.sub_resources.extend(sub_res)
        self.edit_resources.extend(edit_res)
        return self

    def __init__(self):
        self.header_props = PropertyCollection()
        self.properties = PropertyCollection()
        self.sub_resources = SubresourceCollection()
        self.ext_resources = SubresourceCollection()
        self.edit_resources = SubresourceCollection()
        super().__init__()

    def get_struct_children(self)->list:
        res = []
        res.extend(self.header_props.values())
        res.extend(self.properties.values())
        res.extend(self.sub_resources.values())
        res.extend(self.ext_resources.values())
        res.extend(self.edit_resources.values())
        return res


class GdResourceFileImport(GdResource):
    header_props : PropertyCollection
    categories : SubresourceCollection[_GdResourseSubcategory]

    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_resource",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_settings",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:dict[str,GdProperty], categories:list[_GdResourseSubcategory]):
        self = cls()
        for k,v in header_props:
            setattr(self,k,v)
        self.categories.extend(categories)
        return self
    
    def __init__(self):
        self.header_props = PropertyCollection()
        self.categories = SubresourceCollection()
        super().__init__()


    def get_struct_children(self)->list:
        res = []
        res.extend(self.header_props.values())
        res.extend(self.categories.values())
        return res

## SubResources:


class GdSubResource(GdResource, ClassDbEnforcable):
    header_props : PropertyCollection
    properties : PropertyCollection

    class_def : GdClassDef
    script_def : GdClassDef

    key : str

    def set_class_def(self, definition:GdClassDef):
        self.header_props.set_class_def(definition)
        self.class_def = definition
        self.defintion_updated()

    def set_script_def(self, definition:GdClassDef):
        self.header_props.set_script_def(definition)
        self.script_def = definition
        self.defintion_updated()

    def validate(self):
        self.header_props.validate()
        self.properties.validate()

    @classmethod
    def lark_keys(cls):
        return ("sub_resource",)

    @classmethod
    def parse_lark(cls, key, resource_header, resource_body):
        self = cls()
        self.key = resource_header[0:]
        _hprops = resource_header[1:]
        self.header_props.extend(_hprops)
        self.properties.extend(resource_body)
        return self
   
    @contextmanager
    def _add_context(self, ctx:Context):
        with ctx.w("sub_resource",self):
            yield

    def __init__(self):
        self.header_props = PropertyCollection()
        self.properties = PropertyCollection()
        super().__init__()

class GdExtResource(GdSubResource):
    @classmethod
    def lark_keys(cls):
        return ("ext_resource",)

class GdEditResource(GdSubResource):
    @classmethod
    def lark_keys(cls):
        return ("edit_resource",)

class GdSubResourceNode(GdSubResource):
    _cache_layers = ("postload_node",)
    @classmethod
    def lark_keys(cls):
        return ("node_resource",)


## Helper classes :


class _GdResourceFileBody(GdSubResource):
    """Utility class best served as an instance in the parser"""

    value : list

    @classmethod
    def lark_keys(cls):
        return ("prim_resource",)
    
    @classmethod
    def parse_lark(cls, key, tfm, resource_body):
        return cls(resource_body)

    def __init__(self, key, value):
        self.value = value

class _GdResourseSubcategory(GdSubResource):
    """Utility class best served as an instance in the parser"""

    value : list
    key : str

    @classmethod
    def lark_keys(cls):
        return ("prim_subcategory",)
    
    @classmethod
    def parse_lark(cls, _key, tfm, key, resource_body):
        return cls(key, resource_body)

    def __init__(self, key, value):
        self.key = key
        self.value = value


_all : tuple[Type] = (
    GdResourceFileTres,
    GdResourceFileScene,
    GdResourceFileImport,
    _GdResourceFileBody,
    _GdResourseSubcategory,
    GdSubResource,
    GdExtResource,
    GdEditResource,
    GdSubResourceNode,
)
