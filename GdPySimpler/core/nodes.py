from __future__ import annotations

from .structure import _Resource, SubResource, SubResourceCollection, SignalNotationCollection, ExtReferenceCollection, EditFlagCollection, StructContext, GdType, ExtResourceRef

from .property_collection import PropertyCollection
from .collections import Collection, Key
from .values import NodePath 

class ResourceScene(_Resource):
    type : GdType|None|str
    format : int

    script : str #TEMP! resolve to from typing eventually w/a
    script_class : str #TEMP! resolve to from typing eventually w/a

    properties : PropertyCollection
    ext_references : ExtReferenceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection
    edit_flags : EditFlagCollection
    node_res : NodeCollection

    def __setup__(self):
        self.context = StructContext(resource=self)
        self.properties = PropertyCollection(self.context)
        self.ext_references = ExtReferenceCollection(self.context)
        self.sub_resources = SubResourceCollection(self.context)
        self.edit_flags = EditFlagCollection(self.context)
        self.node_res = NodeCollection(self.context)

    def __init__(self, format:int=4, uid:str=None):
        self.__setup__()
        self.format = format
        self.uid.set(uid)

class Node():
    context : StructContext
    owner : _Resource|None = None
    unique_id : Key[str]
    type : GdType|None = None
    
    instance : ExtResourceRef
    instance_editable : bool = False

    overlay : Node|None = None
    overlay_is_thin : bool = False
    
    properties : PropertyCollection

    parent : Node
    _defered_parent : str = None

    children: list[Node]
    _defered_children : list[str] = None

    @classmethod
    def construct(cls, name:str="Node", /, type:GdType=None, properties:dict=None, _defered_parent:str=None, parent:Node=None, **kwargs):
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
        
        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
        
        if parent:
            parent.set_child(self)

        if _defered_parent:
            assert(parent is None)
            def callback(resource:ResourceScene):
                resource.nodes.get(_defered_parent)
            self.context.callback(key="resource", once=True, callback=callback)

        # if _defered_children:
        #     def callback(resource:ResourceScene):
        #         for k in _defered_children:
        #             resource.nodes.get(k).set_parent(self)
        #     self.context.callback(key="resource", once=True, callback=callback)

        return self

    def __setup__(self):
        self.children = []
        
        self.unique_id = Key(self, "unique_id", None)

        self.context = StructContext(sub_resource=self)
        self.properties = PropertyCollection(context=self.context)

    def __init__(self, name:str="Node", type:GdType=None):
        ## TODO: Behavior around name generation
        
        pass
            

        self.__setup__()
    # def __init__(self, /, owner:ResourceScene|None=None, overlay:SubResource=None, type:Type=None, instance:ResourceScene=None, instance_editable:bool=False,  name:str=None, parent:Node=None, unique_id:int=None):
    #     self.__setup__()
    #     self.name = name        
    #     super().__init__(owner=owner, overlay=overlay, type=type, instance=instance, instance_editable=instance_editable, unique_id=unique_id)
    #     if not (parent is None):
    #         parent.add_child(self)

class NodeCollection(Collection):
    unique_keys = ("unique_id",)
    _type = Node