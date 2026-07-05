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
    
    root : Node

    @classmethod
    def construct(cls, uid:str=None, /, nodes:list=None, ext_references:list=None, sub_resources:list=None, edit_flags:list=None, properties:dict=None, **kwargs,):
        self = cls(uid=uid)
        if nodes:
            self.nodes.extend(nodes)
        if ext_references:
            self.ext_references.extend(ext_references)
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
        self.uid = Key(self,"uid", None)
        
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

    def __repr__(self,):
        return f"ResourceScene({self.uid.get()} :: {self.file})"
    
    def construct_tree(self, load_instances:bool=True):
        ## Complete construction of the tree by:
        ## - Loading required trees TODO
        ## - Iterating over all nodes, 
        #       - applying to namespace w/a (Defered namespace!)
        #       - 
        ## - Iterating over all nodes, applying to parent w/a

        namespace_children : dict[str,list[Node]] = {}
        unresolved_namespace : list[(Node,Node)] #Nodes set as parent w/out path (must resolve for namespace to work!)
        no_namespace : list[Node] #Only one should exist, root.
        root = self.root
        ## Root can be: ("" / None)
        ## Root must have owner set, BUT order of operations may prevent that from being visible here

        def fetch_from_defered(node:Node, default=None):
            for o,p in self._defered_namespace:
                if o is node:
                    return p
            return default

        def fetch_from_unresolved(parent_node:Node, default=None):
            for p,c in self.unresolved_namespace:
                if p is parent_node:
                    yield c

        for node in self.nodes:
            node : Node
            if def_path := fetch_from_defered(Node):
                ##TODO: Determine if there is a symbol for root.
                if not  def_path in namespace_children.keys():
                     namespace_children = []
                namespace_children[def_path].append(node)
            elif parent:=node.get_parent():
                ## Direct parent, must resolve namespace
                unresolved_namespace.append((parent, node))
            else:
                # Root does not have a parent declared
                no_namespace.append(node)

        if (len(no_namespace) > 1) and (self.root is None):
            raise Exception("Multiple nodes do not have any parent (defered or direct) declared!", unresolved_namespace)
        elif (self.root is None):
            self.root = no_namespace[0]
        del no_namespace

        ## Now construct w/ knowledge of unresolved namespaces via recursive traversal constructing namespace?

        ## UNKNOWNS:
        ## Correct resolution ofall, pop known, 
        ## Construction of instanced scenes, zipping of those structures

        path = "" #Root
        node = root
        def recur(path:str, node:Node, is_root=False):
            for c in namespace_children.get(path,tuple()):
                node.add_child(c)
                
            for c in list(fetch_from_unresolved(node)):
                if not path in namespace_children.keys():
                     namespace_children[path] = []
                namespace_children[path].append(c)
            
            for c in namespace_children.get(path,tuple()):
                if is_root:
                    recur(path+"/"+node.name, node)
                else:
                    recur(node.name, node)
            
            

class Node():
    name : str
    context : StructContext = None
    
    unique_id : Key[str]
    properties : PropertyCollection
    
    # Should be accessed through get/set:
    _parent : Node = None 
    _children: list[Node]
    _type : GdType|None = None

    owner : _Resource|None = None
    
    instance : ExtResourceRef = None
    instance_editable : bool = False

    overlay : Node|None = None
    overlay_is_thin : bool = False

    @classmethod
    def construct(cls, name:str="Node", /, type:GdType=None, properties:dict=None, _defered_apply_owner:bool=False, _defered_parent:str=None, parent:Node=None, instance:str|ResourceScene|ExtResourceRef|None=None, children:list=None, **kwargs):
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
            parent.add_child(self)

        if children:
            self._children.extend(children)

        ## Reminder to self: python namespaces can suck. 
        ## Multiple lamdas and multiple functions w/ the same name can be merge overwrite in specific scenarios

        if _defered_parent:
            assert(parent is None)
            def set_parent_callback(scene:ResourceScene):
                scene.nodes._promised_parents.append((self,_defered_parent))
            self.context.callback(key="resource", once=True, callback=set_parent_callback)

        if _defered_apply_owner:
            def set_owner_callback(scene:ResourceScene):
                if scene:
                    self.owner = scene
                    return Signal.REMOVE
            ##TODO: Verify this is only being called once.
            self.context.callback(key="resource", once=False, local_only=True, callback=set_owner_callback)
            
        if isinstance(instance,str):
            self.instance = ExtResourceRef(key_id="uid", address=instance)
        elif isinstance(instance,ExtResourceRef):
            self.instance = instance
        elif isinstance(instance,ResourceScene):
            self.instance = ExtResourceRef(key_id="uid", cached_value=instance)
        elif not (instance is None):
            raise Exception(instance)

        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
            else:
                raise KeyError(self,k,v)
        
        return self

    def __setup__(self):
        self._children = []
        
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
    
    def get_parent(self,):
        return self._parent 

    def set_parent(self, new_parent, **kwargs):
        raise NotImplementedError() 

    def add_child(self, item:Node):
        assert(item._parent == None)
        self._children.append(self)
        item._parent = self

    def remove_child(self, item:Node):
        assert(item._parent is self)
        assert(item in self._children)
        item._parent = None
        self._children.remove(item)

    def get_children(self,)->tuple[Node]:
        return tuple(self._children)

class NodeCollection(Collection):
    unique_keys = ("unique_id",)
    _type = Node
    _promised_parents : list[str,Node]

    
    def __setup__(self,):
        self._promised_parents = [] 
        return super().__setup__()