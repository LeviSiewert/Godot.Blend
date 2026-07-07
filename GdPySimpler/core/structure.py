from __future__ import annotations
from enum import Enum
from typing import Type, Any

from .transformer import Transformer
from .context import StructContext as _StructContext
from .collections import Key, Reference, Collection
from .property_collection import PropertyCollection
from .signals import Signal

from pathlib import Path as _Path

class StructContext(_StructContext):
    ''' Structural object, via extends '''
    _slots_ = ("project", "file", "resource", "sub_resource")

    project : Project | None
    file: _File | None
    resource: _Resource | None
    sub_resource: Any | None

class GdValue():
    ...

class Project():
    context : StructContext

    path : str
    settings : _File
    resources : ResourceCollection
    files : FileCollection

    def __setup__(self):
        self.context = StructContext(project=self)
        self.resources = ResourceCollection(context_extends=self.context)
        self.files = FileCollection(context_extends=self.context)
        return self
    
    def __init__(self):
        self.__setup__()

class _File[T:_Resource]():
    context : StructContext ##NOTE: Attached when added to a collection

    path : str
    data : T
    _uid : str #Cached

    def __setup__(self):
        self.context = StructContext(file=self)
        self.path = Key(self, "filepath", unique=True)
        self._uid = Key(self, "uid", unique=True)
    
    def __init__(self, path:_Path, resource:_Resource=None):
        self.__setup__()

class FileCollection(Collection):
    unique_keys = ("_uid", "path")

class FileRef(Reference, GdValue):
    ''' File Reference '''
    key_categories = ("path",)

    def __init__(self, address = None, /, key_id = None, cached_value = None, collection=None):
        super().__init__(key_id, address, cached_value, collection)

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.context.callback("project", self._on_context_updated)
        
    def _on_context_updated(self, value:Any):
        if value is None:
            self.set_collection(None)
        else:
            value : Project
            self.set_collection(value.files)

class FileLocal(_File):
    transformer : Transformer

class FileForeign(_File):
    import_file : _File
    transformer : Transformer



class _Resource():
    context : StructContext ##NOTE: Attached when added to a collection

    format : int = 4

    uid : Key[str]
    file : FileRef
    
    def __setup__(self):
        self.context = StructContext(resource=self)
        self.uid = Key(self, "uid")
        self.file = FileRef(None)
        return self
    
    def __init__(self, format:int=None, uid:str=None, file:_File|str=None):
        self.__setup__()

        if format:
            self.format = format
        
        self.uid.set(uid)
        
        if isinstance(file, _File):
            self.file.store_addr(file.filepath)
            self.file.store_value(file)
        elif isinstance(file, str):
            self.file.cached_addr = file

class ResourceCollection(Collection):
    unique_keys = ("uid", "file")

class RID(Reference, GdValue):
    ''' Resource reference '''
    key_categories = ("uid",)
    typing : GdType

    def __init__(self, address = None, /, key_id = None, cached_value = None, collection=None, typing=None):
        super().__init__(key_id, address, cached_value, collection)
        self.typing = typing

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.context.callback("project", self._on_context_updated)
        
    def _on_context_updated(self, value:Any):
        if value is None:
            self.set_collection(None)
        else:
            value : Project
            self.set_collection(value.resources)


class ResourceScript(_Resource):
    pass



class TypePropDef():
    ''' Contains property definitions '''

class TypeSignalDef():
    ''' Contains signal definitions '''

class GdType():
    context : StructContext
    location : str # "script" | "internal"
    class_name : Key[str] # script_class in sub_res header
    file : Key[str]
    uid : Key[str]

    extends : GdType|None
    signals : dict[str, TypeSignalDef]
    properties : dict[str, TypePropDef]

    def __setup__(self):
        self.context = StructContext()
        self.signals = {}
        self.properties = {}
        self.class_name = Key(self, "class_name", None)
        self.file = Key(self, "file", None)
        self.uid = Key(self, "uid", None)
        return self
    
    def __init__(self, location:str, class_name:str=None, file:str=None, uid:str=None):
        self.__setup__()
        self.location = location
        assert(any([ class_name, file, uid ]))
        self.class_name.set(class_name)
        self.file.set(file)
        self.uid.set(uid)

class GdTypeValueSet():
    def __init__(*args):
        pass

class GdTypeCollection(Collection):
    unique_keys = ("class_name", "file", "uid")
    # _type = GdType

class GdTypeValue(Enum):
    VARIANT = 0
    NULL = 1
    ...

class Typing():
    prim : GdType|GdTypeValue|Type|None = None
    contents : tuple[Typing|GdType|GdTypeValue]|None = None


class ExtResource():
    context : StructContext

    type : Key[str]
    uid : Key[str]
    path : Key[str]
    id : Key[int]

    def __setup__(self):
        self.context = StructContext()
        self.type = Key(self, "type", None)
        self.uid = Key(self, "uid", None)
        self.path = Key(self, "path", None)
        self.id = Key(self, "id", None)
    
    def __init__(self, type:str, uid:str, path:str, id:int,):
        self.__setup__()
        self.type.set(type)
        self.uid.set(uid)
        self.path.set(path)
        self.id.set(id)

    def __colkeys__(self,):
        return (
            self.uid,
            self.path,
            self.id,
            # self.type
            )
    def __repr__(self):
        return f"{self.__class__.__name__}({self.type},{self.id},{self.path},{self.id})"

    def __eq__(self, value):
        if isinstance(value, ExtResource):
            return all((
                self.type == value.type,
                self.uid == value.uid,
                self.path == value.path,
                self.id == value.id
            ))
        return super().__eq__(value)

class ExtResourceCollection(Collection):
    unique_keys = ("uid","path","id")
    # shared_keys = ("type",)

    def key_matcher(self, addr:str):
        if addr.startswith("res://"):
            return "path"
        if addr.startswith("uid://"):
            return "uid"
        return "id"



class ExtResourceRef(Reference, GdValue): 
    ''' Routed reference ID '''
    key_categories = ("id",)
    typing : GdType

    def __init__(self, address=None, cached_value=None, typing=None):
        self.typing = typing
        super().__init__(key_id="id", address=address, cached_value=cached_value)

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.context.callback("resource",self._on_context_updated)
        
    def _on_context_updated(self, value:Any):
        if value is None:
            self.set_collection(None)
        else:
            value : _Resource
            self.set_collection(value.ext_resources)




# def transformer(self, c, node:BlAny)->Node: #NODESET???
#     res = Node(owner = c.tscn.get())

#     if is_instance(node):
#         ensure_file(c, node.ref_filepath, defer_export=True, add_reference=True)
#         res.instance = c.files.get()[node.ref_filepath]
         
#         yield {
#             "children" : local_only_filtered(node.children), ## Getting additive children
#             "properties" : (node.properties),
#         }
        
#         res.properties = c.children.get()["properties"] - res.instance.data_streamed().root.properties
#         for n in c.children.get()["children"]:
#             res.add_child(n)

#         # return res
    
#     if is_instance_overrided(node):
#         ## children would be a dif against existing, as a series of nodes w/ matching names (and root construction..) 

#         res = Node(owner = c.tscn.get())
#         ensure_file(c, node.ref_filepath, defer_export=False, add_reference=True)
#             #Will create file and set owner.
#         inst_file : _File = c.files.get()[node.ref_filepath]
#         res.overlay = inst_file.data.root
#         res.instance = inst_file

#         yield {
#             # "children" : node.children, 
#             "properties" : node.properties
#         }

#         generate_dif_structure(c, self, inst_file.data.root)
#             # Generates dif via two different exports, compares, stores as nodes, ect
#             # It is required that the rulesets being used are identical
#             # File context/Owner is indeterminate, will be set to none for self.children
#             # Prevents double unneeded export comparison w/a, as shouldnt expand defered exports.
#         res.properties = c.children.get()["properties"] - res.instance.data_streamed().root.properties

#     else:
#         yield {
#             "children" : node.children, 
#             "properties" : node.properties
#         }

#         res.properties = c.children.get()["properties"]
#         for n in c.children.get()["children"]:
#             res.add_child(n)


#     res.name = ...
#     ## Also attach position, ect
#     res.properties["position"] = ...
#     res.properties["ect"] = ...
#     ...

#     ## Considering:
#     ## Materials, not bundles as children as they are in different places
#     ## Standard constructor of properties.

#     ## parent-child relationships are rendered at export

#     ## Multitree - children will have to be fetched differently, as owner matters...
#     ## IE node -> (tscn_A, tscn_B, tscn_C) 
#     ## Files do have to be declared, but...

#     ## The only way to fix this is to append to parent parent within the context of the session
#     c.tscn.get().parent.set_child(res)

#     ## OR to:
#     for n in c.children.get()["children"]:
#         if n.owner == c.tscn.get():
#             res.add_child(n)
#     ## BUT:
#     ## I want a multilayer structure w/ multiple files 
#     ## The important thing is that all nodes have an owner file for export
#     ## Thankfully, godot's tscns are update-additive only currently (but I will strive to allow remove within structure)

#     ## The resulting structure from this transformer shouldnt be req to be a completed tree, but an overlayed enough one that allows for exports
#     ## IE
#     ## res.instance = file
#     ## res.instance_loaded = False !! 
#     ## Does not incorperate file's children, waits until required.
    
#     ## When editing a non-local child, it must have a duplicate node created and edited.
#     ## Consider function for Node(owner=...,overlay=other_node)
#     ## Also; interface for files may have an allowence for these overlays, ie a,b = c.files.overlay(Tscn, Gltf_Proxy)
#     ## Then just return A, as A is just an overlay of B and overlay could have access to Res by key or simialar.
#     ## At that point, yes adding just needs to be done contextually (c.file.parent.get()) during walk.

#     ## What about optionally returning a node set (dict[file,Node]) that can be incorperated as reuqied?
#     ## that way I can node_set.set_parent(node_set) ???
#     ## That would just array the operations...
#     ## Could also do new_node_set.set_parent(context.files.parent.get())

#     ## All NodeSet Operations should be vectorized as required
#     ## NodeSets(A0,A1,A2).add_child(NodeSet(B0,B1,B2))
#     ## Consider: Doing this to the source tscn node (B0) and just propigating parentage automatically via mapping.
#     ## A1,A2 may be just thin representations,
#     ## Simple mapping not viable due to multiple instances of A0 being allowed

#     ## A restriction in godot that simplifies things a lot is that:
#     ## Inherited nodes cannot be renamed (root can be, but that's an instance)
#     ## Inherited nodes cannot be repathed to a different part of the tree
#     ## Root nodes act as an additive dif by default (allowing script changes)

#     ## FUTURE:
#     ## Blender's L.O. allows for structure changes. Defer accomidations for this allowence

#     ## Instead of making nodes "thin", it's better to allow them to be layerable and signal on change
#     ## When changed locally, toggle to turn off thin
#     ## By default, all values will be ported from an overlay, and all value writes will be toward local
#     ## When constructing a tree with dependencies, the tree will have to be traversed to "zip" the two or otherwise alter if zip fails.

#     ## So:
#     ## Lex
#     ## Parse
#     ## Set References
#     ## Traverse/Construct tree, Zip/set_overlays

#     return res

