from __future__ import annotations
from .core import GdResource, GdType, Context, GdClassDef, Collection, PropertyCollection, ClassDbEnforcable, Signal
from typing import Type
from contextlib import contextmanager

import random
import string

class SubresourceCollection[T:GdSubResource](Collection):
    values : list[T]
    values_by_id : dict[str, T]

    def __init__(self):
        self.values = []
        self.values_by_id = {}
        super().__init__()

    def _integrate(self, item:T):
        self.values.append(item)
        srid = item.header_props.get("id", None)
        if not srid:
            srid = item.header_props["id"] = self._generate_unique_id()
        assert(not(srid in self.values_by_id.keys()))
        self.values_by_id[srid] = item

    def _disintegrate(self, item:T):
        self.values.remove(item)
        del self.values_by_id[item.header_props["id"]]

    def __getitem__(self, key)->T:
        if isinstance(key,(str,int)):
            return self.get(key)
        raise KeyError("Could not find key!", key)

    def __iter__(self):
        return self.values.__iter__
    
    def items(self,):
        return self.values_by_id.items()

    def by_gdclass(self, cls:GdClassDef):
        children = cls.children
        for x in self.values:
            if (x.class_def in children) or (x.script_def in children):
                yield x
    def by_instance(self, cls:Type[GdSubResource]):
        for x in self.values:
            if isinstance(x,cls):
                yield x
    def by_restype(self, key:str):
        for x in self.values:
            if x.restype == key:
                yield x
    # def by_headertype(self, _type:str):
    #     for x in self.values:
    #         if x.headertype == _type:
    #             yield x

    def get(self, key, default=None):
        return self.values_by_id.get(key, default)
    
    def _generate_unique_id(self,)->str:
        x = "Resource_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))
        while x in self.values_by_id.keys():
            x = "Resource_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))
        return x

class SubresourceNodeCollection[T:GdSubResourceNode](SubresourceCollection):
    root : GdSubResourceNode

    def build_tree(self):
        ## FUTURE: versions will require a matcher/suplimental/insertable tree for (LibOverrides || GLTF matching || External)
        ## These will need to be collected as external & edit resources *before* tree construction.
        ## ALSO: these incoming nodes will have to be be "generic" placeholder | intermediatary types, or dif owner defined

        temp_namespace = {}
        root : GdSubResourceNode = None
        
        nodes : tuple[GdSubResourceNode] = tuple(self.by_restype("node"))
        assert(len(nodes))
        # raise Exception(nodes)

        ## Assign to temp_namespace
        for node in nodes:
            if (parent := node.header_props.get("parent", None)) is None:
                temp_namespace["."] = node
                root = node
            elif parent == ".":
                temp_namespace[node.name] = node 
            else:
                _fullpath = f"{parent}/{node.name}"
                assert(not(_fullpath in temp_namespace.keys()))
                temp_namespace[_fullpath] = node
        # raise Exception(temp_namespace)
    
        assert(not (root is None))

        for node in nodes:
            if node is root:
                continue
            node.set_owner(root)
            node.set_treecol(self)
            if p:=temp_namespace[node.header_props["parent"]]:
                p.add_child(node)
            else:
                node.header_props["name"] = node.header_props["parent"] + node.header_props["name"]  
                root.add_child(node)

        root._is_root = True
        self.root = root

    def _generate_unique_id(self,)->str:
        n = 9
        x = random.randint(10*(n-1),(10*n)-1)
        while x in self.values_by_id.keys():
            x = random.randint(10*(n-1),(10*n)-1)
        return x

class SubresourceCategoryCollection[T:GdSubResourceNode](SubresourceCollection):
    def _integrate(self, item:T):
        self.values.append(item)
        self.values_by_id[item.label] = item

    def _disintegrate(self, item:T):
        self.values.remove(item)
        del self.values_by_id[item.label]
    

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
    def parse_lark(cls, key:str, tfm, header_props:PropertyCollection, ext_res:list[GdExtResource], sub_res:list[GdSubResource], prim_resource:PropertyCollection):
        self = cls()
        self.properties = prim_resource
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
    def parse_lark(cls, key:str, tfm, header_props:PropertyCollection, ext_res:list[GdExtResource], sub_res:list[GdSubResource], edit_res:list[GdSubResource]):
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
    categories : SubresourceCategoryCollection[GdSubresourseCategory]

    @contextmanager
    def _add_context(self,ctx:Context,):
        with ctx.w("file_resource",self):
            yield

    @classmethod
    def lark_keys(cls):
        return ("file_settings",)

    @classmethod
    def parse_lark(cls, key:str, tfm, header_props:PropertyCollection, *categories:list[GdSubresourseCategory]):
        self = cls()
        self.header_props = header_props
        self.categories.extend(categories)
        return self
    
    def __init__(self):
        self.header_props = PropertyCollection()
        self.categories = SubresourceCategoryCollection()
        super().__init__()


    def get_struct_children(self)->list:
        res = []
        res.extend(self.header_props.values())
        res.extend(self.categories.items())
        return res

## SubResources:


class GdSubResource(GdResource, ClassDbEnforcable):
    header_props : PropertyCollection
    properties : PropertyCollection

    class_def : GdClassDef
    script_def : GdClassDef

    restype : str = "sub_resource"

    @classmethod
    def parse_lark(cls, key, header_props:PropertyCollection, resource_body:PropertyCollection):
        self = cls(_constructing = True)
        self.header_props = header_props
        self.properties = resource_body
        return self
    
    @classmethod
    def lark_keys(cls):
        return ("sub_resource",)
   
    def __init__(self, _constructing:bool=False):
        if not _constructing:
            self.header_props = PropertyCollection()
            self.properties = PropertyCollection()
        super().__init__()

    @contextmanager
    def _add_context(self, ctx:Context):
        with ctx.w("sub_resource",self):
            yield

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

    def get_struct_children(self):
        return (*self.header_props.values(), *self.properties.values())

class GdExtResource(GdSubResource):
    restype = "ext"
    @classmethod
    def lark_keys(cls):
        return ("ext_resource",)

class GdEditResource(GdSubResource):
    restype = "edit"
    @classmethod
    def lark_keys(cls):
        return ("edit_resource",)

class GdSubResourceNode(GdSubResource):
    restype = "node"
    _cache_layers = ("postload_node",)

    _treecol : SubresourceNodeCollection
    _is_root : bool = False
    _owner : GdSubResourceNode = None
    _parent : GdSubResourceNode = None
    _children : list[GdSubResourceNode] = None

    def __init__(self, _constructing = False):
        if not _constructing:
            self._children = []
        super().__init__(_constructing)


    @classmethod
    def new(cls, name, path):
        res = cls()
        res.header_props["name"] = name
        res.header_props["parent"] = path
        return res

    @classmethod
    def lark_keys(cls):
        return ("node_resource",)



    @property
    def name(self):
        val = self.header_props.get("name", None)
        if val is None:
            self.header_props["name"] = self.header_props.get("type", "Node")
        return self.header_props["name"]

    @name.setter
    def name(self, value):
        if self._parent:
            assert(not (value in self._parent.get_childnames()))
        self.header_props["name"] = value

    def set_owner(self, owner:GdSubResourceNode):
        self._owner = owner

    def set_treecol(self, treecol:SubresourceNodeCollection):
        self._treecol = treecol

    # def duplicate(self,):
    #     assert(not(self._parent is None))
    #     assert(not(self._is_root))
    #     raise Exception("not implimented yet!")

    def add_child(self,node):
        assert(node._parent is None)
        _names = self.get_childnames()
        if node.name in _names:
            name = node.name
            index = 2
            while node.name in _names:
                node.name = name + str(index)
                index = index + 2
        self._children.append(node)
    
    def remove_child(self,node):
        assert(node._parent is self)
        self._children.remove(node)
        node._parent = None
   
    def get_child(self, name, default=None):
        for x in self._children:
            if x.name == name:
                return x
        return None

    def get_childnames(self)->list[str]:
        res = []
        for x in self._children:
            res.append(x.name)
        return res
        # raise KeyError("Could not find child", name)
    
    def get_children(self)->tuple[GdSubResourceNode]:
        return tuple(self._children)
    
    def get_node(self,path:str):
        return self._get_node_iter(path.split("/")) 
    
    def _get_node_iter(self, path:list[str])->GdSubResourceNode|None: 
        if len(path)==0:
            return self
        val = path.pop()
        match val:
            case ".": return self._get_node_iter(path)
            case "..": return self._parent._get_node_iter(path)
            case _: return self.get_child(val)._get_node_iter(path)
    
    def get_path(self,)->str:
        ## Get an "absolute" path
        if self._is_root: 
            return "."
        if self._parent is None:
            parentpath = self.header_props.get("parent", None)
            return f"'{parentpath}'/" + self.name
        return self._parent.get_path() + "/" + self.name

    def get_path_to(self, node)->str:
        if self.is_anscestor(node):
            return node.get_path()[len(self.get_path()):]
        return self._parent.get_path_to(node) + "/.."

    def is_anscestor(self, node)->bool:
        return node.get_path().startswith(self.get_path())
    
    def __repr__(self,):
        return f"Node({self.get_path()})"
        

## Helper classes :

class GdSubresourseCategory(GdSubResource):
    """Utility class best served as an instance in the parser"""

    label : str
    properties : PropertyCollection

    @classmethod
    def lark_keys(cls):
        return ("prim_subcategory",)
    
    @classmethod
    def parse_lark(cls, _key, tfm, key, resource_body):
        return cls(key, resource_body)

    def __init__(self, label, properties):
        self.label = label
        self.properties = properties


_all : tuple[Type] = (
    GdResourceFileTres,
    GdResourceFileScene,
    GdResourceFileImport,
    GdSubresourseCategory,
    GdSubResource,
    GdExtResource,
    GdEditResource,
    GdSubResourceNode,
)
