from __future__ import annotations

from typing import Any, Type
from weakref import ReferenceType as _WeakReferenceType, ref as weakref

from fsspec import AbstractFileSystem

from .context import StructContext as _StructContext
from .collections import Collection, CollectionKey, CollectionRef
from .property_collection import PropertyCollection
from .gdtype import GdType

class StructContext(_StructContext):
    _slots_ = ("project","file","resource","subresource")
    project : Project
    file : File
    resource : Resource
    subresource : Resource

class Project():
    file_system : AbstractFileSystem
    
    file_types : list[Type[File]]

    types : Collection[GdType] #GdType
    files : Collection[File]
    resources : Collection[Resource]

    def __init__(self, file_system, file_types):
        pass

class ResourceRef(CollectionRef): #Key is UID
    def __setup__(self):
        self.context = _StructContext()
        self.context.callback("project", lambda x: self.set_collection(x.resources))

class FileRef(CollectionRef):
    def __setup__(self):
        self.context = _StructContext()
        self.context.callback("project", lambda x: self.set_collection(x.files))

class GdTypeRef(CollectionRef):
    def __setup__(self):
        self.context = _StructContext()
        self.context.callback("project", lambda x: self.set_collection(x.types))


class File():
    ''' Grouping/Ownership for Resources in memory. '''
    _extensions_ : tuple[str]
    context : StructContext    

    is_loaded : bool = False
    
    filepath : CollectionKey[str]
    cached_uid : str|None = None

    meta_properties : PropertyCollection
    
    resource : ResourceRef

    # Cached only during import on context object, then deleted
    # _cached_sub_resource_map : dict[str, DeferedReference[Resource]]
    # _cached_ext_resource_map : dict[str, DeferedReference[Resource]]
    
    def __setup__(self):
        self.filepath=CollectionKey()
        self.context = StructContext(file=self)
        self.resource = ResourceRef(context=self.context)
        self.meta_properties = PropertyCollection(context=self.context)

    def __init__(self, filepath:str):
        self.__setup__()
        self.filepath.set(filepath)

class Resource():
    ''' Any object that *can* be converted to and from disk '''
    context : StructContext

    uid : CollectionKey[str]
    file : FileRef|None = None
    ## Resource id, None if SubResource (Ie without file) or removed from resources

    ## Subresource id *only* for r/w dif stability & instance overlays. Changed on duplication
    id : str|int = None
    
    type : GdTypeRef
    script_type : GdTypeRef

    properties : PropertyCollection

    instance : ResourceRef|None = None
    instance_is_editable : bool = False
    overlay : Resource|None = None
    # overlay being thin means no changes have been made locally to properties
    # overlayed objects that are not an instance cannot change anything but their properties, and add children.


    def set_overlay(self, overlay:Resource|None, thin:bool=True):
        raise NotImplementedError()

    def set_instance(self, file:FileRef, editable:bool=False):
        raise NotImplementedError()
    
    def set_type(self, type:GdTypeRef):
        raise NotImplementedError()

    def set_script_type(self, script_type:GdTypeRef):
        raise NotImplementedError()

    def __setup__(self,):
        self.context = StructContext()
        self.uid = CollectionKey(self)
        self.properties = PropertyCollection(context=self.context)
        self.type = GdTypeRef(context=self.context)
        self.script_type = GdTypeRef(context=self.context)

    def __init__(self):
        self.__setup__()

    @classmethod
    def construct(cls, /, id:str=None, uid:str=None, file:File=None, type:str|GdType=None, script_type:str|GdType=None, properties:dict|None=None, instance:ResourceRef=None, inst_editable:bool=None, overlay:Resource=None):
        self = cls()
        self.context.callback("resource", lambda x: setattr(self, "owner", x) )

        if id:
            self.id = id
        
        if uid:
            self.uid.set(uid)
        
        if isinstance(file, str):
            self.file.store_key(file)
        elif isinstance(file, File):
            self.file.store_obj(file)
        else:
            raise Exception()

        if type:
            self.set_type(type)

        if script_type:
            self.set_script_type(script_type)
        
        if instance:
            assert not (inst_editable is None)
            self.set_instance(instance, inst_editable)
        elif overlay:
            self.set_overlay(overaly)

        if properties:
            self.properties.update(properties)
        
        return self


class Node(Resource):
    owner : Node|None
    
    parent : Node|None
    name : CollectionKey[str]
    children : Collection[Node]
    
    def __setup__(self):
        super().__setup__()
        self.name = CollectionKey(self)
        self.children = Collection("name", context=self.context)

    @classmethod
    def construct(cls, /, name:str=None, id:int = None, uid = None, file = None, type = None, script_type = None, properties = None, instance = None, inst_editable = None, overlay = None, _parent:str|Node=None, _index:int|None=None, _children:list[Node]=None, _defer_nodetree=True):
        self = super().construct(id, uid, file, type, script_type, properties, instance, inst_editable, overlay)

        self.context.callback("resource", lambda x: setattr(self,"owner",x) )

        if not(name is None):
            self.name.set(name)
        elif not(type is None):
            self.name.set(type.name)
        else:
            self.name.set("Node")

        if _defer_nodetree:
            if not(_parent is None):
                if isinstance(_parent, str):
                    self.context.callback("resource", lambda x: x.get_node(_parent).append(self,_index) )
                else:
                    self.context.callback("resource", lambda x: _parent.append_child(self, _index) )
            if not(_children is None):
                    self.context.callback("resource", lambda x: self.extend_children(_children) )
        else:
            if not(_parent is None):
                assert not isinstance(_parent,str)
                _parent.append_child(self, _index)
            if not(_children is None):
                self.extend_children(_children)

        return self