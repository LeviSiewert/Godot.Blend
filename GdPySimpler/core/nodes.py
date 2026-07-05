from __future__ import annotations

from .structure import _Resource, SubResource, SubResourceCollection, SignalNotationCollection, ExtReferenceCollection, EditFlagCollection, StructContext, GdType, ExtResourceRef, ExtResourceRef, _File

from .property_collection import PropertyCollection
from .collections import Collection, Key
from .values import NodePath 
from .signals import Signal

from . import transformer as _T


## Tree constructor is a Transformer w/ particular settings:

class _Context(_T.Context):
    path : _T.ContextVar[str]
    root : Node
    load_instances : bool
    namespace_parent_asc : dict[str, list[Node]]
    namespace : dict[str, Node]
    def __init__(self, root, load_instances, namespace_parent_asc, namespace):
        self.path = _T.ContextVar("nodepath", default=".")
        self.root = root
        self.load_instances = load_instances
        self.namespace_parent_asc = namespace_parent_asc
        self.namespace = namespace
        super().__init__()

class _TransformerModule(_T.TransformerModule):
    _keys = (_T.DEFAULT,)

    def transform(self, c:_Context, node:tuple[Node,Node]):
        local, overlay = node

        if local is None:
            local = Node.construct_thin(overlay)
        
        elif (local.instance) and (c.load_instances.get()):
            assert (local.instance.get())
            ## ASSUMPTION: an thin node cannot be an instance

            instance : ResourceScene = local.instance.get()
            instance.ensure_loaded()
            instance.ensure_constructed(load_instances=True)

            local.overlay = instance.root
            overlay = instance.root

        if not (c.root is local):
            path = c.path.get() + "/" + local.name
        else:
            path = "."
        c.namespace[path] = local

        defered_children = c.namespace_parent_asc.get(path, tuple())
        if path in c.namespace_parent_asc.keys():
            del c.namespace_parent_asc[path]

        local_children = (*defered_children, *local._children)
        
        t = c.path.set(path)

        if overlay:
            yield self.match_and_order(local_children, overlay._children)
        else:
            yield self.match_and_order(local_children, tuple())

        c.path.reset(t)

        for c in c.children.get():
            local.add_child(c)

        return local

    @staticmethod
    def match_and_order(local_children, overlay_children):
        ##TODO: Ordering!!
        ##TODO: Current ordering is incorrect as well!!

        overlay = {}
        local = {}

        for n in overlay_children:
            overlay[n.name] = [None,n]

        for n in local_children:
            if o:=overlay.get(n.name,None):
                local[n.name] = [n,o]
                del overlay[n.name]
        
        yield from local.values()
        yield from overlay.values()

_Transformer = _T.Transformer(_T.TransformerRuleset("DEFAULT",[_TransformerModule]), identifier="TREE_CONSTRUCTION")

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
    
    root : Node = None

    @classmethod
    def construct(cls, uid:str=None, /, nodes:list=None, ext_references:list=None, sub_resources:list=None, edit_flags:list=None, properties:dict=None, _construct_tree:bool=True, _load_instances:bool=True, _strict:bool=False, **kwargs,):
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

        if _construct_tree:
            self.construct_tree(load_instances=_load_instances, _strict=_strict)

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
    
    def construct_tree(self, load_instances:bool=True, _strict:bool=False,):
        root = self.root

        namespace_parent_asc : dict[str, list[Node]] = {}
        namespace : dict[str, Node] = {}
        unassigned : list[Node] = []

        for n in self.nodes:
            n : Node

            if n._parent:
                # Known parent, ignore. 
                # Later incorperated & ordered in transformer
                pass 

            elif not (p:=getattr(n, "_defered_parent", None)) is None:
                ## Make path styles explicit.
                if p == "":
                    p = "."
                elif not p.startswith("./"):
                    p = "./" + p

                if not p in namespace_parent_asc.keys():
                    namespace_parent_asc[p] = []
                namespace_parent_asc[p].append(n)

            else:
                unassigned.append(n)


        if (len(unassigned) == 1):
            if root:
                assert unassigned[0] == root
            else:
                root = unassigned[0]
        elif len(unassigned):
            #Multiple nodes do not have an assigned parent!, Only one node (root) should populate unassigned
            raise Exception("(len(unassigned)>1) :: ", unassigned)

        del unassigned

        namespace["."] = root
        
        c = _Context(root, load_instances, namespace_parent_asc, namespace)
        _Transformer.transform_tree(c, (root,None))

        #Missing parents:

        if _strict and namespace_parent_asc:
            raise Exception(namespace_parent_asc)
        
        for p_path, ns in namespace_parent_asc.items():
            for n in ns:
                n.name = (p_path.replace("/","#") + "#" + n.name).strip(".")
                root.add_child(n)

        # Behavior note for GdPy:
        ## Orphaned children 
            # will not be removed (missing refs or not)
            # Virtual Paths should be respected in traversal of Nodepaths (via central handling)
            # Virtual paths are nodes under root with "#" replacing "/"
        ## Empty NodePath references should be accomidated w/ missing or non-loaded instances.
        ## Instances loaded later will need to construct/attach virtual paths.

        return root


class Node():
    name : str
    context : StructContext = None
    
    unique_id : Key[str]
    properties : PropertyCollection
    
    # Should be accessed through get/set:
    _parent : Node = None 
    _defered_parent : str # TEMP! TODO: determine better method

    _children: list[Node]
    _type : GdType|None = None

    owner : _Resource|None = None
    
    instance : ExtResourceRef = None
    instance_editable : bool = False

    overlay : Node|None = None
    overlay_is_thin : bool = False

    @classmethod
    def construct_thin(cls, overlay:Node):
        self = cls(overlay.name, overlay.type)
        self.set_overlay(overlay, thin = True)
        return self

    @classmethod
    def construct(cls, name:str="Node", /, type:GdType=None, properties:dict=None, _defered_apply_owner:bool=False, _defered_parent:str=None, parent:Node=None, instance:str|ResourceScene|ExtResourceRef|None=None, children:list=None, **kwargs):
        ''' Construction within an specific context, before being extended/appended into a Scene 
        _defered_apply_owner: set owner to constructed scene. Default False
        '''
        self = cls(name=name, type=type)
        
        if properties:
            self.properties.update(properties)

        if children:
            for c in children:
                self.add_child(c)

        if parent:
            #TODO: Swap to defered reference?
            parent.add_child(self)
        elif not (_defered_parent is None):
            self._defered_parent = _defered_parent 

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