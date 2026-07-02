from __future__ import annotations
from enum import Enum
from typing import Type, Any

# from ...GdPy.structure.core.transformer_v2 import Transformer
# from .GdPy.structure.core.primitives import (
#     MultiKeyCollection as Collection,
# )

from .transformer import Transformer
from .collections import CollectionKey, Collection

class PropertyCollection(dict):
    overlay : PropertyCollection|None = None
    pinned : list[str]
    def __missing_key__(self, key)->Any:
        if not self.overlay is None:
            return self.overlay[key]
        raise KeyError

class Project():
    path : str
    settings : ResourceSettings
    resources : ResourceCollection
    files : FileCollection


class _File[T:_Resource]():
    path : str
    data : T
    _uid : str #Cached

    def __new__(cls):
        self = super().__new__(cls)
        self._uid = CollectionKey(self, "uid", unique=True)
        self._filepath = CollectionKey(self, "filepath", unique=True)
        return self
    
class FileLocal(_File):
    transformer : Transformer

class FileForeign(_File):
    import_file : _File[ResourceSettings]
    transformer : Transformer

class FileCollection(Collection):
    unique_keys = ("_uid", "path")
    _type = _File 

class _Resource():
    project : Project|None = None
    uid : CollectionKey[str]

    file : _File|None = None
    
    def __new__(cls):
        self = super().__new__(cls)
        self.uid = CollectionKey(self, "uid")
        self.file = CollectionKey(self, "file")
        return self
    
    def __init__(self, format:int=4, uid:str=None, file:_File=None):
        self.uid.set(uid)
        self.format = format
        
        self.file.set(file.filepath)

class ResourceCollection(Collection):
    unique_keys = ("uid", "file")
    _type = _Resource

class ResourceSettings(_Resource):
    properties : PropertyCollection
    cat_resources : CategoryCollection

    def __new__(cls):
        self = super().__new__(cls)
        self.properties = PropertyCollection()
        self.cat_resources = CategoryCollection()
        return self

class ResourceTres(_Resource):
    type : GdType|None|str
    format : int
    script : str #TEMP! resolve to from typing eventually w/a
    script_class : str #TEMP! resolve to from typing eventually w/a
    
    properties : PropertyCollection

    ext_references : ExtReferenceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection

    def __new__(cls):
        self = super().__new__(cls)

        self.properties = PropertyCollection()
        self.ext_references = ExtReferenceCollection()
        self.sub_resources = SubResourceCollection()
        return self
    
    def __init__(self, type, format, uid, script_class:str=None):
        self.type = type
        self.script_class = script_class
        super().__init__(format=format, uid=uid)

class ResourceScene(ResourceTres):
    properties : PropertyCollection

    node_res : NodeCollection
    signals : SignalCollection

    def __new__(cls):
        self = super().__new__(cls)
        self.node_res = NodeCollection()
        self.signals = SignalCollection()
        return self

    def __init__(self, format:int=4, uid:str=None):
        self.format = format
        self.uid.set(uid)

class Signal():
    signal : str
    method : str
    fr : Node
    to : Node

class SignalCollection(Collection):
    shared_keys = ("signal", "method", "fr", "to")
    _type = Signal

class TypePropDef():
    ''' Contains property definitions '''

class TypeSignalDef():
    ''' Contains signal definitions '''

class GdType():
    location : str # "script" | "internal"
    class_name : CollectionKey[str] # script_class in sub_res header
    file : CollectionKey[str]
    uid : CollectionKey[str]

    extends : GdType|None
    signals : dict[str, TypeSignalDef]
    properties : dict[str, TypePropDef]

    def __new__(cls):
        self = super().__new__(cls)
        self.signals = {}
        self.properties = {}
        self.class_name = CollectionKey(self, "class_name", None)
        self.file = CollectionKey(self, "file", None)
        self.uid = CollectionKey(self, "uid", None)
        return self
    
    def __init__(self, location:str, class_name:str=None, file:str=None, uid:str=None):
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
    _type = GdType

class GdTypeValue(Enum):
    VARIANT = 0
    NULL = 1
    ...

class Typing():
    prim : GdType|GdTypeValue|Type|None = None
    contents : tuple[Typing|GdType|GdTypeValue]|None = None


class ExtReference():
    type : CollectionKey[str]
    uid : CollectionKey[str]
    path : CollectionKey[str]
    id : CollectionKey[int]

    def __new__(cls):
        self = super().__new__()
        self.type = CollectionKey(self, "type", None)
        self.uid = CollectionKey(self, "uid", None)
        self.path = CollectionKey(self, "path", None)
        self.id = CollectionKey(self, "id", None)
    
    def __init__(self, type:str, uid:str, path:str, id:int,):
        self.type.set(type)
        self.uid.set(uid)
        self.path.set(path)
        self.id.set(id)

class ExtReferenceCollection(Collection):
    unique_keys = ("uid","path","id")
    shared_keys = ("type",)


class EditFlag():
    path : str
    def __init__(self, path):
        self.path = path

class EditFlagCollection():
    unique_keys = ("path")
    _type = EditFlag


class SubResource():
    owner : _Resource|None = None
    unique_id : CollectionKey[str]
    type : GdType|None = None
    
    instance : _Resource
    instance_editable : bool = False

    overlay : SubResource|None = None
    overlay_is_thin : bool = False
    
    properties : PropertyCollection

    def __new__(cls):
        self = super().__new__(cls)
        self.unique_id = CollectionKey(self, "unique_id", None)
        self.properties = PropertyCollection()
        return self

    def __init__(self, /, owner:_Resource|None=None, overlay:SubResource=None, type:Type=None, instance:ResourceScene=None, instance_editable:bool=False, unique_id:Any=None):
        if not (unique_id is None):
            self.unique_id.set(unique_id)

        self.set_owner(owner)
        self.set_type(type)
        
        if instance:
            assert(overlay is None)
            self.set_overlay(instance.data.root)
            self.instance = instance
            self.instance_editable = instance_editable
        elif overlay:
            self.set_overlay(overlay)

class SubResourceCollection(Collection):
    unique_keys = ("unique_id",)
    _type = SubResource

class Node(SubResource):
    unique_id : CollectionKey[int]

    overlay : Node
    
    name : str #property, return overlay.name if overlay 
    parent : Node
    children : list[Node]

    def __new__(cls):
        self = super().__new__(cls)
        self.children = []
        self.unique_id = CollectionKey(self, "unique_id", None)
        return self

    def __init__(self, /, owner:_Resource|None=None, overlay:SubResource=None, type:Type=None, instance:ResourceScene=None, instance_editable:bool=False,  name:str=None, parent:Node=None, unique_id:int=None):
        self.name = name
        
        super().__init__(owner=owner, overlay=overlay, type=type, instance=instance, instance_editable=instance_editable, unique_id=unique_id)

        if not (parent is None):
            parent.add_child(self)


class NodeCollection(Collection):
    unique_keys = ("unique_id",)
    _type = Node


class Category():
    name : str
    properties : PropertyCollection
    def __new__(cls):
        self = super().__new__(cls)
        self.properties = PropertyCollection()
        return self

class CategoryCollection(Collection):
    unique_keys = ("name",)
    _type = Category


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

