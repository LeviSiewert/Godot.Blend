from __future__ import annotations

from contextvars import ContextVar
from contextlib import contextmanager

from typing import Type, Any
from enum import Enum

from fsspec import AbstractFileSystem

from .context import StructContext as _StructContext
from .signals import Signal

from .collections import (
    Key, 
    Collection as _Collection, 
    Reference as _Reference,
)

class StructContext(_StructContext):
    _slots_ = ("project", "file", "resource", "sub_resource")
    project : Project | None
    file : _File | None
    resource : _Resource | None
    sub_resource : Any | None

class GdValue():
    ''' Base class for all writeable atomic values, prim for isinstance checking '''

class _ContextualReference(_Reference, GdValue):
    _context_target : str
    _collection_key : str

    def __setup__(self):
        self.context = StructContext()
        self.context.callback(self._context_target, self._on_context_updated)

    def __init__(self, address = None, /, context:StructContext=None, key_id = None, cached_value = None, collection=None):
        super().__init__(key_id, address, cached_value, collection)
        self.context.set_extends(context)

    def _on_context_updated(self, ctx_obj:object):
        if ctx_obj is None:
            self.set_collection(None)
        else:
            self.set_collection(getattr(ctx_obj, self._collection_key))


class Project():
    context : StructContext
    files : FileCollection
    resources : ResourceCollection

    file_system : AbstractFileSystem

    disc_file_created : Signal[str]
    disc_file_deleted : Signal[str]
    disc_file_updated : Signal[str]
    disc_file_moved : Signal[str,str]

    def __setup__(self):
        self.context = StructContext(project=self)
        self.files = FileCollection(self.context)
        self.resources = ResourceCollection(self.context)
        
        self.disc_file_created = Signal(self)
        self.disc_file_deleted = Signal(self)
        self.disc_file_updated = Signal(self)
        self.disc_file_moved = Signal(self)

    def __init__(self, file_system:AbstractFileSystem, file_types:list[Type[_File]], search:bool=True):
        self.__setup__()
        self.file_system = file_system
        self.file_types = file_types
        if search:
            self.search()

    @classmethod
    def construct(cls, file_system:AbstractFileSystem=None, file_types:list[Type[_File]]=tuple(), search:bool=False, **kwargs):
        self = cls(file_system, file_types, search=False)

        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise AttributeError(obj=self, name=k)
            setattr(self, v)

        if search:
            self.search()

        return self

    def search(self):
        # search file_system, populate self.files, update all uid paths on files.
        raise NotImplementedError()

    def match_filetype(self, filepath:str)->Type[_File]:
        ## find first match from self.file_types and return
        raise NotImplementedError()

    def filter_folder(self, folder:list[str])->list[str]:
        ## pass folder through all self.file_types
        raise NotImplementedError()


class _FileMetadata():
    __slots__ = tuple()
    file : _File = None

    last_imported : int|None
    last_exported : int|None

    def __init__(self, file:_File):
        self.file = file


class _File():
    context : StructContext
    metadata : _FileMetadata

    path : Key[str]
    data : Any|None

    lock : ContextVar[bool]
        # If locked, do not interpret input signals.

    cached_uid : str = None 



    def __setup__(self):
        self.context = StructContext(file=self)
        self.context.callback("project", self._on_project_updated)

        self.lock = ContextVar("locked", default=False)
        self.metadata = _FileMetadata(self)
        self.path = Key(self, "path", None)
        self.data = None

    _project_cached : Project = None

    def _on_project_updated(self, project:Project|None):
        if self._project_cached:
            self._project_cached.disc_file_created.disconnect(self._on_disc_created_filter)
            self._project_cached.disc_file_deleted.disconnect(self._on_disc_deleted_filter)
            self._project_cached.disc_file_updated.disconnect(self._on_disc_updated_filter)
            self._project_cached.disc_file_moved.disconnect(self._on_disc_moved_filter)
        
        self._project_cached = project
        if project:
            self._project_cached.disc_file_created.connect(self._on_disc_created_filter)
            self._project_cached.disc_file_deleted.connect(self._on_disc_deleted_filter)
            self._project_cached.disc_file_updated.connect(self._on_disc_updated_filter)
            self._project_cached.disc_file_moved.connect(self._on_disc_moved_filter)
        

    def __init__(self, path:str, data:Any=None):
        self.__setup__()
        self.path.set(path)
        self.data = data

    def __colkeys__(self,):
        return (self.path, )

    def get_file_system(self):
        return self.context.project.file_system

    @contextmanager
    def locked(self, lock=True, update_meta=False):
        t = self.lock.set(lock)
        yield
        if update_meta:
            self.update_metadata()
        t = self.lock.reset(t)

    def update_cached_uid(self,)->str:
        ''' Fetch the UID from disc, or fetch from res if locked '''
        #TODO Trigger from file write!
        raise NotImplementedError()

    def update_metadata(self):
        ''' Update metadata, assuming just written or changes accepted '''
        fs = self.get_file_system()
        #TODO
        raise NotImplementedError()


    def read(self, force=False):
        fs = self.get_file_system()
        raise NotImplementedError()
        self.update_metadata()

    def write(self):
        assert not (self.data is None)
        fs = self.get_file_system()
        raise NotImplementedError()

    def move(self):
        fs = self.get_file_system()
        raise NotImplementedError()

    def _on_disc_created_filter(self, fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_created_filter(fp, *args)
    def _on_disc_created(self, fp):
        fs = self.get_file_system()
        raise NotImplementedError()
            

    def _on_disc_updated_filter(self,fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_updated_filter(fp, *args)
    def _on_disc_updated(self, fp):
        fs = self.get_file_system()
        raise NotImplementedError()
    

    def _on_disc_moved_filter(self,fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_moved_filter(fp, *args)
    def _on_disc_moved(self, fr:str, to:str):
        fs = self.get_file_system()
        raise NotImplementedError()

    def _on_disc_deleted_filter(self,fp:str,*args):
        if (fp != self.filepath.addr): 
            return
        self._on_disc_deleted_filter(fp, *args)
    def _on_disc_deleted(self,fp):
        fs = self.get_file_system()
        raise NotImplementedError()


    @classmethod
    def construct(cls, path, /, data:Any=None, _defered_write:bool=False, _defered_write_data:Any=None, _defered_import:bool=False, **kwargs):
        self = cls(path)

        if not (data is None):
            self.data = data

        for k,v in kwargs.items():
            if not hasattr(self,k):
                raise AttributeError(obj=self, name=k)
            setattr(self, v)

        if _defered_import:
            ## TODO VERIFY: Test order of ops!
            self.context.callback("project", self.read, once=True)

        if _defered_write:
            def _write(prj):
                if _defered_write_data:
                    fs = self.get_file_system()
                    fs.write_text(self.path.add, _defered_write_data)
                    return
                self.write()
            self.context.callback("project", _write, once=True)

        return self
        

class _FileResource(_File):
    context : StructContext
    path : Key[str]
    data : _Reference[str, _Resource]

    def __init__(self, path:str, defer_fetch_uid:bool=True):
        self.__setup__()
        self.path.set(path)
        
        if defer_fetch_uid:
            def _update():
                # Attach disc uid when added to the project, if otherwise not set (usually by function construct)
                if self.data.get():
                    return
                self.update_cached_uid()
                if self.cached_uid:
                    self.data.store_address(self.cached_uid)
            self.context.callback("project", _update, once=True)

    @classmethod
    def construct(cls, path, /, data_or_uid:_Resource|str=None, defer_fetch_uid:bool=True, _defered_write:bool=False, _defered_write_data:Any=None, **kwargs):
        self = super().construct(path, data=None, _defered_write=_defered_write, _defered_write_data=_defered_write_data)
        
        if isinstance(data_or_uid, str):
            self.data.store_address(data_or_uid)
            self.cached_uid = data_or_uid
        elif isinstance(data_or_uid, _Resource):
            self.data.store_value(data_or_uid)
            if data_or_uid.uid.addr:
                self.cached_uid = data_or_uid

        return self

class FileCollection(_Collection):
    unique_keys = ("path",)

    def key_matcher(self, addr):
        return "path"
    
    def get_cached_uid(self, uid:str):
        raise NotImplementedError()
    
    def key_unique_collision_handle(self, left_obj, left_key, right_obj, right_key):
        raise KeyError("Files cannot be procedurally pathed, rename before appending or otherwise ensure file names do not overlap", left_key.addr, left_obj, right_obj)

class FileRef(_ContextualReference):
    _context_target : str = "project"
    _collection_key : str = "files"


class _Resource():
    context : StructContext
    uid : Key[str, _FileResource]
    file : _Reference[str, _FileResource]
    
    def __setup__(self):
        self.uid = Key(self, "uid", None)
        self.context = StructContext(file=self)
        self.data = ResourceRef(context=self.context)

    def __init__(self, uid=None):
        self.__setup__()
        self.uid.set(uid)

    @classmethod
    def construct(cls,):
        raise NotImplementedError()

    def __colkeys__(self,):
        return (self.uid, )

    def write(self):
        assert self.file.get()
        raise NotImplementedError()
    
    def _on_disc_created(self):
        ## TODO: Signal forwarding from file.
        ## Uncertain behavior here as
        raise NotImplementedError()
    
    def write_update(self,):
        assert self.file.get()
        raise NotImplementedError()

    def _on_disc_updated(self,):
        ## TODO: Signal forwarding from file.
        ## File lock will prevent this from being forwarded
        ## Import-dif.
        raise NotImplementedError()
    
    def _on_disc_moved(self,):
        ## TODO: Signal forwarding from file.
        ## File lock will prevent this from being forwared
        ## Disc moving should not impact local
        raise NotImplementedError()
    
    def _on_disc_deleted(self,):
        ## TODO: Signal forwarding from file.
        ## File lock will prevent this from being forwared
        ## Unknown desired behavior. Perhaps removal and cleanup of self?
        raise NotImplementedError()

class ResourceCollection(_Collection):
    unique_keys = ("uid",)

    def key_matcher(self, addr):
        return "uid"

class ResourceRef(_ContextualReference):
    _context_target : str = "project"
    _collection_key : str = "resources"


class RID(ResourceRef):
    ''' Resource reference with typing, use as GdValue '''
    _context_target : str = "project"
    _collection_key : str = "resources"
    typing : GdType

    def __init__(self, address=None, /, typing=None, context = None, key_id=None, cached_value=None, collection=None):
        super().__init__(address, context, key_id, cached_value, collection)
        self.typing = typing


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

class GdTypeCollection(_Collection):
    unique_keys = ("class_name", "file", "uid")
    # _type = GdType

class GdTypeValue(Enum):
    VARIANT = 0
    NULL = 1
    ...

class Typing():
    prim : GdType|GdTypeValue|Type|None = None
    contents : tuple[Typing|GdType|GdTypeValue]|None = None





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

