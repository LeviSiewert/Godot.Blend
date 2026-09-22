from __future__ import annotations
from typing import Any

from .structure import _Resource, StructContext, GdType
from .resources import SubResource, SubResourceCollection, SubResourceRef, ExtResource, ExtResourceRef, ExtResourceCollection

from .property_collection import PropertyCollection
from .collections import Collection, CollectionKey
from .values import NodePath 
from .signals import Signal

from . import transformer as _T


class EditFlag():
    path : str = None

    def __init__(self, path:str):
        assert isinstance(path,str)
        self.path = path

    def __eq__(self, value):
        if isinstance(value, EditFlag):
            return value.path == self.path
        return self.path == value

    def __repr__(self):
        return f"EditFlag({self.path})"

class EditFlagCollection(Collection):
    unique_keys = ("path",)
    _type = EditFlag

class SignalNotation():
    ##TODO: switch fr, to into nodes and attach to node during construction

    context : StructContext ##NOTE: Attached when added to a collection

    signal : str
    method : str
    fr : CollectionKey #Node
    to : CollectionKey #Node

    def __setup__(self):
        self.context = StructContext(signal=self)
        self.fr = CollectionKey(self, "nodepath", None)
        self.to = CollectionKey(self, "nodepath", None)
    
    def __init__(self, signal:str, method:str, fr:str, to:str):
        self.__setup__()
        self.signal = signal
        self.method = method
        self.fr.set(fr)
        self.to.set(to)

    def __hash__(self):
        return hash( (self.signal, self.method, self.fr.addr, self.to.addr) )
    
    def __repr__(self,):
        return f"{self.__class__.__name__}(signal='{self.signal}' method='{self.method}' fr='{self.fr.addr}' to='{self.to.addr}')"
    
    def __eq__(self,value):
        if isinstance(value, SignalNotation):
            return all((
                value.signal == self.signal,
                value.method == self.method,
                value.fr.addr == self.fr.addr,
                value.to.addr == self.to.addr,
               ) )
        return super().__eq__(value)
        pass

class SignalNotationCollection(Collection):
    # shared_keys = ("signal", "method", "fr", "to")
    _type = Signal

class ResourceScene(_Resource):
    uid : CollectionKey[str]

    type : GdType|None|str
    format : int

    script : str #TEMP! resolve to from typing eventually w/a
    script_class : str #TEMP! resolve to from typing eventually w/a

    properties : PropertyCollection
    ext_resources : ExtResourceCollection # Contextual re-mapping, req stability for diffing, export should trim based on ref count.
    sub_resources : SubResourceCollection
    edit_flags : EditFlagCollection
    nodes : NodeCollection
    
    root : Node = None

    @classmethod
    def construct(cls, uid:str=None, /, nodes:list=None, ext_resources:list=None, sub_resources:list=None, edit_flags:list=None, properties:dict=None, _construct_tree:bool=True, _load_instances:bool=True, _strict:bool=False, **kwargs,):
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

        if _construct_tree:
            self.construct_tree(load_instances=_load_instances, _strict=_strict)

        return self

    def __setup__(self):
        self.uid = CollectionKey(self,"uid", None)
        
        self.context = StructContext(_identifier=self,resource=self)

        self.properties = PropertyCollection(context=self.context)
        self.ext_resources = ExtResourceCollection(context=self.context)
        self.sub_resources = SubResourceCollection(context=self.context)
        self.edit_flags = EditFlagCollection(context=self.context)
        self.nodes = NodeCollection(context=self.context)

    def __init__(self, uid:str=None, format:int=4):
        self.__setup__()
        self.format = format
        self.uid.set(uid)

    def __repr__(self,):
        return f"ResourceScene({self.uid.get()} :: {self.file})"
    
    def construct_tree(self, load_instances:bool=True, _strict:bool=False,):
        ## REMINDER: Godot Node trees are additive only!! :D

        root : Node|None = self.root
        
        namespace : dict[str, Node] = {}
        directly_assigned : list[Node] = []
        overlay_namespace : dict[str,Node] = {}        


        for n in self.nodes:
            if n._parent:
                directly_assigned.append(n)
            elif not (p:=getattr(n, "_defered_parent", None)) is None:
                if p == "":
                    p = "."
                elif not p.startswith("./"):
                    p = "./" + p
                path = (p + "/" + n.name)
                namespace[path] = n 
            else:
                assert (root is None) or (root is n)
                root = n
        assert(root)
        namespace["."] = root


        _namespace = {v:k for (k,v) in namespace.items()}

        def _recur(node:Node)->str:
            if res:=_namespace.get(node, None):
                if isinstance(res, list):
                    raise Exception(node, _namespace)
                return res 
            
            if node is root:
                return "."
            
            if node._parent is None:
                raise Exception(node, _namespace, namespace)
            
            path = _recur(node._parent) + "/" + node.name
            
            _namespace[node] = path
            namespace[path] = node

            return path
            
        for n in directly_assigned:
            _recur(n)
            

        ## Iter through parents until name is found, then assign locally
        ## In this, all directly assigned chains must have a parent asc w/ the namespace (Root is always in namespace)

        if load_instances:
            #TODO:
            for n in self.nodes:
                n : Node
                if not n.instance:
                    continue
                overlay_namespace.update( n.instance.get().nodepath_space(localize=namespace[n]) )
        
        res_namespace : dict[str, list[Node|None, Node|None]] = {}

        for k,v in namespace.items():
            res_namespace[k] = v

        for k,v in overlay_namespace.items():
            if not k in res_namespace.keys():
                res_namespace[k] = Node.construct_thin(v)
            else:
                res_namespace[k].set_overlay(v)
        
        ## TODO: Namespace can be sorted alphabetically for signals

        unresolved = []

        for k, node in res_namespace.items():
            if k == ".":
                assert (node is root)
                continue
            parent = res_namespace.get(k.rsplit("/",1)[0], None)
            if parent is None:
                unresolved.append((k,node))
                continue
            else:
                if node._parent is None:
                    parent.add_child(node)
                else:
                    assert node._parent is parent

        
        if _strict and unresolved:
            raise Exception(unresolved)
        
        for k,node in unresolved:
            # Produce "virtual path" that should be able to be written back unharmed
            node.name = "$" + (k.replace("/","#") + "#" + node.name).strip(".")
            root.add_child(node)

        # # Behavior note for GdPy:
        # ## Orphaned children 
        #     # will not be removed (missing refs or not)
        #     # Virtual Paths should be respected in traversal of Nodepaths (via central handling)
        #     # Virtual paths are nodes under root with "#" replacing "/" and starting with "$"
        # ## Empty NodePath references should be accomidated w/ missing or non-loaded instances.
        # ## Instances loaded later will need to construct/attach virtual paths.

        return root


class Node():
    name : str
    context : StructContext = None

    unique_id : CollectionKey[int]
    properties : PropertyCollection
    type : str = ""
    script_type : str = ""
    
    # Should be accessed through get/set:
    _parent : Node = None 
    _defered_parent : str # TEMP! TODO: determine better method

    _children: list[Node]
    _type : GdType|None = None

    # node_paths : list[NodePath] ## Ignored in favor of context fetch during export

    owner : _Resource|None = None
    
    instance : ExtResource = None
    instance_editable : bool = False
    index : int = None

    overlay : Node|None = None
    overlay_is_thin : bool = False


    @classmethod
    def construct_thin(cls, overlay:Node):
        self = cls(overlay.name, overlay.type)
        self.set_overlay(overlay, thin = True)
        return self

    @classmethod
    def construct(cls, name:str="Node", /, unique_id:int=None, type:GdType=None, properties:dict=None, _defered_apply_owner:bool=False, _defered_parent:str=None, parent:Node=None, instance:str|ResourceScene|ExtResource|None=None, children:list=None, **kwargs):
        ''' Construction within an specific context, before being extended/appended into a Scene 
        _defered_apply_owner: set owner to constructed scene. Default False
        '''
        self = cls(name=name, type=type)
        
        if properties:
            self.properties.update(properties)

        if children:
            for c in children:
                self.add_child(c)

        if unique_id:
            self.unique_id.set(unique_id)

        if isinstance(parent, Node):
            #TODO: Swap to defered reference?
            parent.add_child(self)
        elif parent:
            self._defered_parent = parent
        elif not (_defered_parent is None):
            assert (not parent)
            self._defered_parent = _defered_parent 

        if _defered_apply_owner:
            def set_owner_callback(scene:ResourceScene):
                if scene:
                    self.owner = scene
                    return Signal.REMOVE
            ##TODO: Verify this is only being called once.
            self.context.callback(key="resource", once=False, local_only=True, callback=set_owner_callback)
            
        if isinstance(instance,str):
            self.instance = ExtResourceRef(address=instance)
        elif isinstance(instance,ExtResourceRef):
            self.instance = instance
        elif isinstance(instance,ExtResource):
            self.instance = ExtResourceRef(cached_value=ExtResourceRef)
        # elif isinstance(instance,ResourceScene):
            ## Will have to attach dep to resource !
            # self.instance = ExtResourceRef(key_id="uid", cached_value=instance)
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
        
        self.unique_id = CollectionKey(self, "unique_id", None)

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
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self,value:Node|Any):
        if not isinstance(value, Node):
            return super().__eq__(value)
        
        return all((
            value.name == self.name,
            value.properties == self.properties,
            value.instance == self.instance,
        ))

class NodeCollection(Collection):
    unique_keys = ("unique_id",)
    _type = Node
    _promised_parents : list[str,Node]

    def __setup__(self,):
        self._promised_parents = [] 
        return super().__setup__()