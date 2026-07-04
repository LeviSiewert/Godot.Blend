from __future__ import annotations
from enum import Enum
from typing import Type, Any

from .transformer import Transformer
from .context import StructContext as _StructContext
from .collections import CollectionKey, CollectionReferenceUnique, Collection
from .property_collection import PropertyCollection
from .signals import Signal

from pathlib import Path as _Path

class StructContext(_StructContext):
    ''' Structural object, via extends '''
    _slots_ = ["_extends","project","file","resource","sub_resource"]

    project : Project = None 
    file: _File = None 
    resource: _Resource = None 
    sub_resource: SubResource = None

class GdValue():
    ...

class Project():
    context : StructContext

    path : str
    settings : ResourceSettings
    resources : ResourceCollection
    files : FileCollection

    def __setup__(self):
        self.context = StructContext(project=self)
        self.settings = ResourceSettings(context_extends=self.context)
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
        self.path = CollectionKey(self, "filepath", unique=True)
        self._uid = CollectionKey(self, "uid", unique=True)

        return self
    
    def __init__(self, path:_Path, resource:_Resource=None):
        self.__setup__()
    
class FileLocal(_File):
    transformer : Transformer

class FileForeign(_File):
    import_file : _File[ResourceSettings]
    transformer : Transformer

class FileCollection(Collection):
    unique_keys = ("_uid", "path")
    _type = _File 

class _Resource():
    context : StructContext ##NOTE: Attached when added to a collection

    project : Project|None = None
    uid : CollectionKey[str]

    file : _File|None = None
    
    def __setup__(self):
        self.context = StructContext(resource=self)
        self.uid = CollectionKey(self, "uid")
        self.file = CollectionKey(self, "file")
        return self
    
    def __init__(self, format:int=4, uid:str=None, file:_File=None, filepath:str=None):
        self.__setup__()

        self.format = format
        
        self.uid.set(uid)
        
        if file:
            self.file.set(file.filepath)
        elif filepath:
            self.file.set(filepath)

class ResourceCollection(Collection):
    unique_keys = ("uid", "file")
    _type = _Resource

class ResourceSettings(_Resource):
    
    properties : PropertyCollection
    cat_resources : CategoryCollection

    def __setup__(self):
        super().__setup__()
        self.properties = PropertyCollection()
        self.cat_resources = CategoryCollection()

class ResourceTres(_Resource):
    type : GdType|None|str
    format : int
    script : str #TEMP! resolve to from typing eventually w/a
    script_class : str #TEMP! resolve to from typing eventually w/a
    
    properties : PropertyCollection

    ext_references : ExtReferenceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection

    def __setup__(self):

        self.properties = PropertyCollection()
        self.ext_references = ExtReferenceCollection()
        self.sub_resources = SubResourceCollection()
        return self
    
    def __init__(self, type, format, uid, script_class:str=None):
        self.type = type
        self.script_class = script_class
        super().__init__(format=format, uid=uid)

class ResourceScript(ResourceTres):
    pass

class ResourceScene(ResourceTres):
    properties : PropertyCollection

    node_res : NodeCollection

    def __setup__(self):
        super().__setup__()
        self.node_res = NodeCollection()

    def __init__(self, format:int=4, uid:str=None):
        self.format = format
        self.uid.set(uid)

class SignalNotation():
    ##TODO: switch fr, to into nodes and attach to node during construction

    context : StructContext ##NOTE: Attached when added to a collection

    signal : str
    method : str
    fr : CollectionKey #Node
    to : CollectionKey #Node

    def __setup__(self):
        self.context = StructContext(signal=self)
        self.fr = CollectionKey(self, "nodepath", )
        self.to = CollectionKey(self, "nodepath", )
    
    def __init__(self, signal:str, method:str, fr:str, to:str):
        self.__setup__()
        self.signal = signal
        self.method = method
        self.fr.set_address(fr)
        self.to.set_address(to)

    def __hash__(self):
        # raise Exception(self.signal, self.method, self.fr, self.to)
        return hash( (self.signal, self.method, self.fr, self.to) )

class SignalNotationCollection(Collection):
    # shared_keys = ("signal", "method", "fr", "to")
    _type = Signal

class TypePropDef():
    ''' Contains property definitions '''

class TypeSignalDef():
    ''' Contains signal definitions '''

class GdType():
    context : StructContext
    location : str # "script" | "internal"
    class_name : CollectionKey[str] # script_class in sub_res header
    file : CollectionKey[str]
    uid : CollectionKey[str]

    extends : GdType|None
    signals : dict[str, TypeSignalDef]
    properties : dict[str, TypePropDef]

    def __setup__(self):
        self.context = StructContext()
        self.signals = {}
        self.properties = {}
        self.class_name = CollectionKey(self, "class_name", None)
        self.file = CollectionKey(self, "file", None)
        self.uid = CollectionKey(self, "uid", None)
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
    _type = GdType

class GdTypeValue(Enum):
    VARIANT = 0
    NULL = 1
    ...

class Typing():
    prim : GdType|GdTypeValue|Type|None = None
    contents : tuple[Typing|GdType|GdTypeValue]|None = None


class ExtReference():
    context : StructContext

    type : CollectionKey[str]
    uid : CollectionKey[str]
    path : CollectionKey[str]
    id : CollectionKey[int]

    def __setup__(self):
        self = super().__setup__()
        self.context = StructContext()
        self.type = CollectionKey(self, "type", None)
        self.uid = CollectionKey(self, "uid", None)
        self.path = CollectionKey(self, "path", None)
        self.id = CollectionKey(self, "id", None)
    
    def __init__(self, type:str, uid:str, path:str, id:int,):
        self.__setup__()
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
    context : StructContext
    owner : _Resource|None = None
    unique_id : CollectionKey[str]
    type : GdType|None = None
    
    instance : _Resource
    instance_editable : bool = False

    overlay : SubResource|None = None
    overlay_is_thin : bool = False
    
    properties : PropertyCollection

    def __setup__(self):
        self.context = StructContext(sub_resource=self)
        self.unique_id = CollectionKey(self, "unique_id", None)
        self.properties = PropertyCollection()
        return self

    def __init__(self, /, owner:_Resource|None=None, overlay:SubResource=None, type:Type=None, instance:ResourceScene=None, instance_editable:bool=False, unique_id:Any=None):
        self.__setup__()
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
    
    signals : SignalNotationCollection

    def __setup__(self):
        super().__setup__()
        self.children = []
        self.unique_id = CollectionKey(self, "unique_id", None)
        self.signals = SignalNotationCollection()

    def __init__(self, /, owner:_Resource|None=None, overlay:SubResource=None, type:Type=None, instance:ResourceScene=None, instance_editable:bool=False,  name:str=None, parent:Node=None, unique_id:int=None):
        self.__setup__()
        self.name = name
        
        super().__init__(owner=owner, overlay=overlay, type=type, instance=instance, instance_editable=instance_editable, unique_id=unique_id)

        if not (parent is None):
            parent.add_child(self)


class NodeCollection(Collection):
    unique_keys = ("unique_id",)
    _type = Node


class Category():
    context : StructContext
    name : str
    properties : PropertyCollection
    def __setup__(self):
        self.context = StructContext()
        self.properties = PropertyCollection()
        return self

    def __init__(self, name, properties:dict):
        self.__setup__()
        self.name = name
        self.properties.update(properties)

class CategoryCollection(Collection):
    unique_keys = ("name",)
    _type = Category


class _ContextualRef(CollectionReferenceUnique, GdValue):
    context : StructContext

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.context.value_updated.connect(self._on_context_updated)

    def _on_context_updated(self, key:str, value:Any|None):
        pass

class SubResourceRef(_ContextualRef): 
    key_categories = ("id",)
    _type = SubResource

    def _on_context_updated(self, key:str, value:Any):
        if key != "resource":
            return
        if value is None:
            self.set_collection(None)
        else:
            value : ResourceTres
            self.set_collection(value.sub_resources)

class ExtResourceRef(_ContextualRef): 
    ''' Routed reference ID '''
    key_categories = ("id",)
    _type = _Resource

    def _on_context_updated(self, key:str, value:Any):
        if key != "resource":
            return
        if value is None:
            self.set_collection(None)
        else:
            value : ResourceTres
            self.set_collection(value.ext_resources)

class RID(_ContextualRef):
    ''' Universal ID '''
    key_categories = ("uid",)
    _type = _Resource

    def _on_context_updated(self, key:str, value:Any):
        if key != "project":
            return
        if value is None:
            self.set_collection(None)
        else:
            value:Project
            self.set_collection(value.resources)


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

