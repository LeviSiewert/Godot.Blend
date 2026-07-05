from __future__ import annotations

from .structure import _Resource, SubResource, SubResourceCollection, SignalNotationCollection, ExtReferenceCollection, EditFlagCollection, StructContext, GdType, ExtResourceRef, ExtResourceRef

from .property_collection import PropertyCollection
from .collections import Collection, Key
from .values import NodePath 
from .signals import Signal

class ResourceScene(_Resource):
    uid : Key[str]

    type : GdType|None|str
    format : int

    script : str #TEMP! resolve to from typing eventually w/a
    script_class : str #TEMP! resolve to from typing eventually w/a

    properties : PropertyCollection
    ext_references : ExtReferenceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection
    edit_flags : EditFlagCollection
    nodes : NodeCollection

    @classmethod
    def construct(cls, uid:str=None, /, nodes:list=None, ext_resources:list=None, sub_resources:list=None, edit_flags:list=None, properties:dict=None, **kwargs,):
        self = cls(uid=uid)
        if nodes:
            self.nodes.extend(nodes)
        if ext_resources:
            self.ext_resources.extend(ext_resources)
        if sub_resources:
            self.sub_resources.extend(sub_resources)
        if edit_flags:
            self.edit_flags.extend(edit_flags)
        if properties:
            self.properties.update(properties)
        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
        return self

    def __setup__(self):
        self.uid = Key(self,None,"uid")
        
        self.context = StructContext(_identifier=self,resource=self)

        self.properties = PropertyCollection(context=self.context)
        self.ext_references = ExtReferenceCollection(context=self.context)
        self.sub_resources = SubResourceCollection(context=self.context)
        self.edit_flags = EditFlagCollection(context=self.context)
        self.nodes = NodeCollection(context=self.context)

    def __init__(self, uid:str=None, format:int=4):
        self.__setup__()
        self.format = format
        self.uid.set(uid)

class Node():
    name : str
    context : StructContext = None
    
    unique_id : Key[str]
    properties : PropertyCollection
    
    parent : Node = None
    children: list[Node]

    owner : _Resource|None = None
    type : GdType|None = None
    
    instance : ExtResourceRef = None
    instance_editable : bool = False

    overlay : Node|None = None
    overlay_is_thin : bool = False

    @classmethod
    def construct(cls, name:str="Node", /, type:GdType=None, properties:dict=None, _defered_apply_owner:bool=False, _defered_parent:str=None, parent:Node=None, instance:str|ResourceScene|ExtResourceRef|None=None, **kwargs):
        ''' Construction within an specific context, before being extended/appended into a Scene
        _defered_parent && _defered_children are absolute paths, and context callbacks are used to assign them.
        ## TODO : Assign them as promises/similar to References instead 
            - could prevents ordering issues, 
            - promises w/out fullfillemt can be reacted to/raise errors 
            - Abs path must still be constructed
        '''
        self = cls(name=name, type=type)
        
        if properties:
            self.properties.update(properties)
        
        if parent:
            parent.set_child(self)

        if _defered_parent:
            assert(parent is None)
            ## Reminder to self: python namespaces can suck. Multiple lamdas and multiple functions w/ the same name can be swap references in specific scenarios
            def set_parent_callback(scene:ResourceScene):
                scene.nodes.promise("nodepath", _defered_parent, lambda val: val.add_child(self), )
                ## Promise fail case? scene.root.add_child(self), defered/keep offset parent??
                
            self.context.callback(key="resource", once=True, callback=set_parent_callback)

        if _defered_apply_owner:
            def set_owner_callback(scene:ResourceScene):
                if scene:
                    self.owner = scene
                    return Signal.REMOVE
            self.context.callback(key="resource", once=False, local_only=True, callback=set_owner_callback)
            
        if isinstance(instance,str):
            self.instance = ExtResourceRef(address=instance)
        elif isinstance(instance,ExtResourceRef):
            self.instance = instance
        elif isinstance(instance,ResourceScene):
            self.instance = ExtResourceRef(cached_value=instance)
        elif not (instance is None):
            raise Exception()

        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
            else:
                raise KeyError(self,k,v)
        
        return self

    def __setup__(self):
        self.children = []
        
        self.unique_id = Key(self, "unique_id", None)

        self.context = StructContext(_identifier=self, sub_resource=self)
        self.properties = PropertyCollection(context=self.context)

    def __init__(self, name:str=None, type:GdType=None):
        ## TODO: Behavior around name generation
        self.__setup__()

        if (name is None) and (type is None):
            raise Exception()
        elif (name is None):
            name = type.class_name
        
        self.name = name
        self.type = type
    
    def __colkeys__(self,):
        return (self.unique_id,)

    def __repr__(self):
        return f"Node({self.name})"

class NodeCollection(Collection):
    unique_keys = ("unique_id",)
    _type = Node