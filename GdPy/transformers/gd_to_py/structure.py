from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions, cvar_as
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
from ...core.structure import (
    Promise,
    Properties,
    File,
    Resource,
    NodePath,
    GdSignal,
    Node,
    Settings,
    Category,
)

from copy import copy

from random import sample, randint
from string import ascii_letters

from contextvars import ContextVar
from typing import Generator, Any, Callable
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )
    

class MACROS:
    def default(item, /, default:Any=None, callable = lambda x:x):
        if item is None:
            return default
        return callable(item)

    def default_yield(item, /, default:Any=None, flag:Flag=TRANSFORM_CHILDREN, settings={}):
        if item is None:
            return default
        res = yield flag(item, **settings)
        return res

    def gdtopy_pairs_to_dict(item:list[LarkTree])->Generator[Flag,tuple,dict]:
        res = {}
        for pair in item:
            k,v = yield TRANSFORM_CHILDREN(pair.children)
            res[k] = v
        return res

    def pytogd_dict_to_str(item:dict, seperator="=", join=",")->Generator:
        res = []
        for pair in item.items():
            k,v = yield TRANSFORM_CHILDREN(pair) 
            res.append(k + seperator + v)
        return join.join(res)

class GdToPy_Options(TransformerOptions): 
    def __init__(self, session):
        self.resource = ContextVar("resource", default = None)
        self.subresource = ContextVar("subresource", default = None)
        self.properties = ContextVar("properties", default = None)

        self.fetch_subres = ContextVar("fetch_subres",default = self._fetch_subres)
        self.fetch_subres_reqs = ContextVar("fetch_subres_reqs", default = []) 
        self.fetch_extres = ContextVar("fetch_extres",default = self._fetch_extres)
        self.fetch_extres_reqs = ContextVar("fetch_extres_reqs", default = []) 
        self.fetch_node = ContextVar("fetch_node",default = self._fetch_node)
        self.fetch_node_reqs = ContextVar("fetch_node_reqs", default = []) 

    resource : ContextVar[Resource|None] = None
    subresource : ContextVar[Resource|None] = None
    properties : ContextVar[Properties|None] = None

    def _fetch_subres(self,promise:Promise)->Promise|Resource:
        ''' Override with contextual insertions as req. Default here is to return the input & record to _fetch_requested to push warnings as req'''
        if not (promise in self.fetch_subres_reqs.get()):
            self.fetch_subres_reqs.get().append(promise)
        return promise
    fetch_subres : ContextVar[Callable] = _fetch_subres
    fetch_subres_reqs : ContextVar[None|list] = None 
    
    def _fetch_extres(self,promise:Promise)->Promise|Resource:
        ''' Override with contextual insertions as req. Default here is to return the input & record to _fetch_requested to push warnings as req'''
        if not (promise in self.fetch_subres_reqs.get()):
            self.fetch_subres_reqs.get().append(promise)
        return promise
    fetch_extres : ContextVar[Callable] = _fetch_extres
    fetch_extres_reqs : ContextVar[None|list] = None 
    
    def _fetch_node(self,path:str|NodePath)->NodePath|Node:
        ''' Override with contextual insertions as req. Default here is to return the input & record to _fetch_requested to push warnings as req'''
        if not (path in self.fetch_subres_reqs.get()):
            self.fetch_subres_reqs.get().append(path)
        return path
    fetch_node : ContextVar[Callable] = _fetch_node
    fetch_node_reqs : ContextVar[None|list] = None 

class PyToGd_Options(TransformerOptions): 
    def __init__(self, session):
        self.resource = ContextVar("resource", default = None)
        self.subresource = ContextVar("subresource", default = None)
        self.properties = ContextVar("properties", default = None)

        self.declare_edit = ContextVar("declare_edit", default=self._declare_edit)
        self.declare_edit_requests = ContextVar("declare_edit_requests", default = [])
        self.declare_signal = ContextVar("declare_signal", default=self._declare_signal)
        self.declare_signal_requests = ContextVar("declare_signal_requests", default = [])
        self.declare_subres = ContextVar("declare_subres", default=self._declare_subres)
        self.declare_subres_requests = ContextVar("declare_subres_requests", default = [])
        self.declare_extres = ContextVar("declare_extres", default=self._declare_extres)
        self.declare_extres_requests = ContextVar("declare_extres_requests", default = [])

    resource : ContextVar[Resource|None] = None
    subresource : ContextVar[Resource|None] = None
    properties : ContextVar[Properties|None] = None

    def _declare_edit(self, _node:str)->None:
        ''' Override with contextual insertions as req. record to _declared to push warnings as req
        Used by session to push warning as req '''
        if not (_node in self.declare_edit_requests.get()):
            self.declare_edit_requests.get().append(_node)
        return
    declare_edit : ContextVar[Callable] = _declare_edit
    declare_edit_requests : ContextVar[list] = None
        
    def _declare_signal(self, signal:GdSignal)->None:
        ''' Override with contextual insertions as req. record to _declared to push warnings as req
        Used by session to push warning as req '''
        return
    declare_signal : ContextVar[Callable] = _declare_signal
    declare_signal_requests : ContextVar[list] = None

    def _declare_subres(self, object:Resource|Promise)->Promise:
        ''' Override with contextual insertions as req. Default return a promise with the ID
        Used by session to push warning as req '''
        if isinstance(object, Promise):
            return object
        return Promise(object.name, Promise.Type.SUB_RESOURCE)
    declare_subres : ContextVar[Callable] = _declare_subres
    declare_subres_requests : ContextVar[list] = None

    def _declare_extres(self, value:File|Resource|Promise)->Promise:
        ''' Override with contextual insertions as req. Default return a promise of the value.uid or value.path.
        Used by session to push warning as req '''
        ## TODO: Consider procedural session mappings
        if isinstance(value, Promise):
            if value.p_type is Promise.Type.EXT_RESOURCE_DIRECT:
                return Promise
            elif value.p_type is Promise.Type.EXT_RESOURCE:
                return Promise(value.key.get("id", value.key["uid"]), Promise.Type.EXT_RESOURCE)
            else:
                return Promise(value.key, Promise.Type.EXT_RESOURCE)
        elif isinstance(value, Resource):
            if value.uid is None:
                value.uid = "".join(sample(ascii_letters, 9))
            return Promise(value.uid, Promise.Type.EXT_RESOURCE)
        elif isinstance(value, File):
            if value.path is None:
                raise Exception()
            return Promise(value.path, Promise.Type.FILE)
        else:
            raise TypeError()
    declare_extres : ContextVar[Callable] = _declare_extres
    declare_extres_requests : ContextVar[list] = None

class _Properties():
    class GdToPy(GdToPy_Transformer):
        keys = ["properties"]
        def transform(self, session, node:LarkTree):
            res = yield MACROS.gdtopy_pairs_to_dict(node.children)
            return Properties(res)

    class PyToGd(PyToGd_Transformer):
        _types = [Properties]
        def transform(self, session, node:Properties):
            t = session.options["structure"].properties.set(node)
            res = yield MACROS.pytogd_dict_to_str(node, join = "\n")
            session.options["structure"].properties.reset(t)
            return res


class _Promise():
    class GdToPy(GdToPy_Transformer):
        keys = ["ref_subresource","ref_extresource","ref_resource"]
        def transform(self, session, node:LarkTree):
            ## Promises will fullfill themselves at earliest context when applied to any structure object. No need to callback stuff here
            match node.value:
                case "ref_subresource":
                    return Promise(str(node.children[0]), Promise.Type.SUB_RESOURCE)
                case "ref_extresource":
                    return Promise(str(node.children[0]), Promise.Type.EXT_RESOURCE_DIRECT)
                case "ref_resource":
                    return Promise(str(node.children[0]), Promise.Type.RESOURCE).split("uid://")[-1]
            raise NotImplementedError()

    class PyToGd(GdToPy_Transformer):
        types = [Promise] 
        def transform(self, session, node:Promise):
            match node.p_type:
                case Promise.Type.RESOURCE:
                    session.options["structure"].declare_rid.get()(node)
                    return f'RID("uid://{node.key}")'
                
                case Promise.Type.SUB_RESOURCE:
                    session.options["structure"].declare_subres.get()(node)
                    return f'SubResource("{node.key}")'
                    
                case Promise.Type.EXT_RESOURCE_DIRECT:
                    session.options["structure"].declare_extres.get()(node)
                    return f'ExtResource("{node.key}")'
                
                case Promise.Type.EXT_RESOURCE:
                    pr = session.options["structure"].declare_extres.get()(node)
                    return f'ExtResource({pr})'
                    
                case Promise.Type.FILE:
                    raise Exception("Unknown how to render, as string, or as res:// filepath?")
            
            raise TypeError()
                    

class _ExtResource():
    class GdToPy(GdToPy_Transformer):
        keys = ["ext_resource"]
        def transform(self, session, node):
            _options = node.children[0]
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            return Promise(options, Promise.Type.EXT_RESOURCE)

    # class PyToGd(PyToGd_Transformer): ## Handled by _Promise

class _Resource():
    class GdToPy(GdToPy_Transformer):
        keys = ["sub_resource"]
        def transform(self, session, node):
            _options, _properties = node.children
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)
            return Resource(**options, properties = properties)

    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_resource"]
        def transform(self, session, node):
            _options, _ext_resources, _sub_resources, _properties = node.children

            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            ext_resources : tuple[Promise] = yield TRANSFORM_CHILDREN(_ext_resources)
            sub_resources : tuple[Resource] = yield TRANSFORM_CHILDREN(_sub_resources)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)

            return Resource(**options, ext_resources=ext_resources, sub_resources=sub_resources, properties = properties)
        
    class PyToGd(PyToGd_Transformer):
        types = [Resource]

        def transform(self, session, node:Resource):
            if not (session.options["structure"].properties.get() is None):
                ## Operating within properties, declare dependencies and return a references
                if node.file or node.uid:
                    res = yield TRANSFORM(session.options["structure"].declare_extres.get()(self)) # -> promise -> rendered
                    return res
                else:
                    res = yield TRANSFORM(session.options["structure"].declare_subres.get()(self)) # -> promise -> rendered
                    return res

class _Node():
    class GdToPy(GdToPy_Transformer):
        keys = ["node_resource"]
        def transform(self, session, node):
            _options, _properties = node.children
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)

            options["id"] = options.pop["unique_id"]
            _parent = options.pop("parent")

            res = Node(**options, properties = properties)
            res._parent = _parent

    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_scene"]

        def transform(self, session, node):
            ''' Process is: 
            - Determine format ## FOR LATER
            - Convert(ExtRes) -> "Buffer"
            - Convert(EditFlags) -> "Buffer"
            - Convert(Subresources, Step=Initial) -> "Buffer"
            - Set "find" closures of (ExtRes|EditFlags|Subresources) to context
            - Convert(SubResources, Step=Complete)
            - Convert(Nodes, Step=Initial)
                -> Assign to Access "Buffer" of _tree_namespace
            - Create Tree structure via .children.append(...)
            - Convert Connections
            - Assign Connections to tree
                - remainder unclaimed
            - Assign Edits to tree
                - remainder unclaimed
            - Return tree root
            '''

            _options, _ext_resources, _sub_resources, _node_resources, _edit_flags, _connections = node.children
            assert len(_node_resources.children) > 0

            options = yield MACROS.gdtopy_pairs_to_dict(_options.children)

            t = session.options["FORMAT"].format.set(options.get("format", 4))

            t0 = session.options["structure"].resource.set(node)
            t1 = session.options["structure"].subresource.set(node)
            
            ext_resources = yield TRANSFORM_CHILDREN(_ext_resources) 
            ext_resources : dict[Promise] = {x.key["id"]:x for x in sub_resources}
            _ext_resources_used = dict({k:False for k in ext_resources.keys()})

            sub_resources = yield TRANSFORM_CHILDREN(_sub_resources, step="INITIAL")
            sub_resources : dict[Resource] = dict({x.name:x for x in sub_resources})
            _sub_resources_used = dict({k:False for k in sub_resources.keys()})

            def fetch_subres(self, promise:Promise)->Promise|Resource:
                ''' Return subres or original promise, mark as used so as to not cache '''
                if not ((res:=sub_resources.get(promise.key, None)) is None):
                    _sub_resources_used[promise.key] = True
                    return res
                return promise 
                
            def fetch_extres(self, promise:Promise)->Promise|Resource:
                ''' Return copy in full promise, mark as used so as to not cache '''
                if not ((res:=ext_resources.get(promise.key, None)) is None):
                    _ext_resources_used[promise.key] = True
                    return res
                return promise 

            t2 = session.options["structure"].fetch_subres.set(fetch_subres)
            t3 = session.options["structure"].fetch_extres.set(fetch_extres)

            yield TRANSFORM_CHILDREN(_sub_resources) ## Complete transforming subresources. Should *not* be dependent on node tree.
            ## -> Mutates _..._used
            
            ## Intial transformation for tree creation:
            root_node = yield TRANSFORM(_node_resources[0], step="INITIAL")
            root_node.uid = options["uid"]

            node_resources = yield TRANSFORM_CHILDREN(_node_resources[1:], step="INITIAL")
            # node_resources = sorted(node_resources, lambda x: x._parent ) ## Consider for ensuring load orde??

            _tree_namespace = {"":root_node}
            _unclaimed_nodes = {}
            for n in node_resources:
                ## Build tree structure
                p_path = n._parent
                del n._parent
                fullpath : str|None = None

                if p_path == ".":
                    root_node.children.append(n)
                    fullpath = n.name.key
                    _tree_namespace[fullpath] = n
                else:
                    fullpath = (p_path + "/" + n.name.key)
                    if p_path in _tree_namespace.keys():
                        _tree_namespace[p_path].children.append(n)
                        _tree_namespace[fullpath] = n
                    else:
                        ## Instance-Overlay edited, reconstructed later
                        _unclaimed_nodes[fullpath] = n

            def fetch_node(self, path:str|NodePath)->NodePath|Node:
                ''' Return node from scene path '''
                return _tree_namespace.get(path, path)

            t4 = session.options["structure"].fetch_node.set(fetch_node)

            connections = yield TRANSFORM_CHILDREN(_connections)
            _unclaimed_connections = []

            for c in connections:
                if isinstance(c.fr,Node) and isinstance(c.to,Node):
                    c.fr.signals.append(c)
                else:
                    _unclaimed_connections.append(c)

            edit_flags = yield TRANSFORM_CHILDREN(_edit_flags)
            _edit_flags_used = [False*len(edit_flags)] 

            for k,i in enumerate(edit_flags):
                if n:=_tree_namespace.get(k,None):
                    n.instance_editable = True
                    _edit_flags_used[i] = True
                elif n:=_unclaimed_nodes.get(k,None):
                    n.instance_editable = True
                    _edit_flags_used[i] = True

            yield TRANSFORM_CHILDREN(_node_resources)  ## Complete node loading, all properties, promises, references, ect
            ## -> Mutates _..._used

            root_node.unclaimed_extres = dict({k:v for (k,v),b in zip(ext_resources.items(), _ext_resources_used) if b})
            root_node.unclaimed_subres = dict({k:v for (k,v),b in zip(sub_resources.items(), _sub_resources_used) if b})
            root_node.unclaimed_edits = list([v for v,b in zip(edit_flags,_edit_flags_used) if (b)])
            root_node.unclaimed_nodes = _unclaimed_nodes
            root_node.unclaimed_signals = _unclaimed_connections

            session.options["FORMAT"].format.reset(t)
            session.options["structure"].resource.reset(t0)
            session.options["structure"].subresource.reset(t1)
            session.options["structure"].fetch_subres.reset(t2)
            session.options["structure"].fetch_extres.reset(t3)
            session.options["structure"].fetch_node.reset(t4)

            
            return root_node

        
    class PyToGd(PyToGd_Transformer):
        types = [Node]

        def transform(self, session, node:Node):
            if not (session.options["structure"].properties.get() is None):
                ## Operating within properties, declare dependencies and return a references
                if node.file or node.uid:
                    res = yield TRANSFORM(session.options["structure"].declare_extres.get()(self)) ## -> promise -> rendered
                    return res
                elif p_node:=session.options["structure"].node():
                    res = yield TRANSFORM(p_node.get_path(node)) # -> path -> rendered
                    return res 
                else:
                    raise Exception() ## Non-normalized structure, non-rectifiable with current info. Consider cached nodepath as bullwark? What is another method?

            if node.file or node.uid:
                res = yield from self.transform_scene(session, node)
                return res
            else:
                res = yield from self.transform_node(session, node)
                return res

        def transform_node(self, session, node:Node):
            ''' Transform this node, do not yield node children
            Declare subresources, ect to options
            Yield Properties
            '''

            t = session.options["structure"].subresource.set(self)

            if not node.unique_id:
                node.unique_id = randint(1000000, 10000000)

            header_props = {
                "name":f'"{node.name}"',
                "type":f'"{node.gdtype}"' if node.gdtype else "Node",
                "script":f'"{node.gdscript}"' if node.gdscript else None,
                "unique_id":node.unique_id,
            }

            if scene:=session.options["structure"].resource.get() and (not (scene is node)): 
                header_props["parent"] = f'"{scene.get_path(self, get_rendering_parent=True)}"'
            else:
                header_props["parent"] = f'"{node._parent}"' 
                ## Cached value

            #edge cases should be taken care of by default structure options' closures
            if node.instance:
                header_props["instance"] = yield TRANSFORM(session.options["structure"].declare_extres(node.instance))
            if node.instance_editable:
                session.options["structure"].declare_edit(scene.get_path(self))

            for signal in node.signals:
                signal : GdSignal
                session.options["structure"].declare_signal(signal)

            txt_header = f'[node {" ".join([f'{k}={v}' for k,v in header_props.items() if not (v is None)])}]'
            txt_options = yield TRANSFORM(node.properties)

            session.options["structure"].subresource.reset(t)

            return "\n".join(
                txt_header,
                txt_options,
            )
            

        def transform_scene(self, session, node:Node):
            ''' Process is:
            Create dependency declaration values, closures, set closures to context vars
            Process (Self) -> Calls (extres|subres|edit|signal) declaration closures
            Process (Explored (Nodes | Unclaimed nodes)) -> Calls (extres|subres|edit|signal) declaration closures
            Process (Explored (Subresources | Unclaimed Subres)) -> Calls (extres|subres|edit|signal) declaration closures
            Process (ExtRes)
            Process (Signals)
            Process (Edits)
            '''

            t0 = session.options["structure"].resource.set(node)
            t1 = session.options["structure"].subresource.set(node)

            ## DEPENDENCY DECLARATION AND UNCLAIMED INTEGRATION CLOSURES ##
            unclaimed_nodes = node.unclaimed_nodes if (not (node.unclaimed_nodes is None)) else {}
            def trim_unclaimed_nodes(tree:list[Node])->list:
                ''' Unclaimed nodes '''
                tree_by_path = {node.path_to(x):x for x in tree}
                _add = {}
                for k,_node in unclaimed_nodes.items():
                    if k in tree_by_path.keys():
                        continue
                    _add[k] = _node 
                unclaimed_nodes.update(_add)

            unclaimed_edits = node.unclaimed_edits if node.unclaimed_edits else {}
            declared_edits = []
            def _declare_edit(_node:str)->None:
                ''' Append str (Nodepath) to edits '''
                if not (_node in declared_edits):
                    declared_edits.append(_node)
            def integrate_unclaimed_edits():
                ''' evaluate cached nodes for edits, declare, same with unclaimed edits. '''
                for k,_node in unclaimed_nodes.items():
                    _node:Node
                    if (_node.instance and _node.instance_editable):
                        _declare_edit(k)
                for k in unclaimed_edits:
                    _declare_edit(k)

            unclaimed_signals = node.unclaimed_signals if (not (node.unclaimed_signals is None)) else tuple()
            declared_signals = []
            def _declare_signal(signal:GdSignal)->None:
                ''' Append signal if __eq__ not already present '''
                for k in declared_signals:
                    if k == signal:
                        return
                declared_signals.append(signal)
            def integrate_unclaimed_signals():
                ''' append unclaimed signals to declared signals (unclaimed signals which should only exist on partially constructed trees)'''
                for x in unclaimed_signals:
                    _declare_signal(x)

            unclaimed_subres = node.unclaimed_subres if (not (node.unclaimed_subres is None)) else {}
            declared_subres = {}
            def _declare_subres(x)->Promise:
                if not (x in declared_subres.values()):
                    if (x.name is None) or (x.name in declared_subres.keys()):
                        ## Key collission, alter object. Object is altered instead of just session dict-key due to desire for stability.
                        x.name = x.type+"_"+"".join(sample(ascii_letters, 9))
                    declared_subres[x.name] = x
                return Promise(x.name, Promise.Type.SUB_RESOURCE)

            unclaimed_extres = node.unclaimed_extres if (not (node.unclaimed_extres is None)) else tuple()
            _required_extres = [] ## Cache-check deps.
            extres_by_id = {}
            declared_extres = {} ## By UID
            def _declare_extres(value:File|Resource|Promise)->Promise:
                ''' Declare a node into this session, returns an ascociated direct promise from the mapped namespace, prioritized by uid '''
                if isinstance(value, (Resource,File)):
                    if value.uid in declared_extres():
                        return
                    value = value.as_extres_promise()

                if isinstance(value, Promise) and (value.p_type is Promise.Type.EXT_RESOURCE):
                    uid = value.key["uid"]
                    path = value.key["path"]
                    type = value.key["type"]

                    if p:=declared_extres.get(uid,None): ## Return cached
                        # return p.value["id"]
                        return Promise(p.value["id"], Promise.Type.EXT_RESOURCE_DIRECT)

                    id = value.key.get("id", None)
                    if (id is None):
                        id = "".join(sample(ascii_letters, 5)) ## Generate non-matching
                        value.key["id"] = id 
                         
                    declared_extres[uid] = value
                    extres_by_id[id] = value
                    return Promise(id, Promise.Type.EXT_RESOURCE_DIRECT)

                elif isinstance(value, Promise) and (value.p_type is Promise.Type.EXT_RESOURCE_DIRECT):
                    _required_extres.append(value.key)
                    return value
                
                raise TypeError()
            
            def integrate_unclaimed_extres():
                ''' Append unclaimed_extres to declared_extres, only after all tree extres have been found'''
                for x in unclaimed_extres: 
                    _declare_extres(x)

            t2 = session.options["structure"].declare_extres.set(_declare_extres)
            t3 = session.options["structure"].declare_subres.set(_declare_subres)
            t4 = session.options["structure"].declare_signal.set(_declare_signal)
            t4 = session.options["structure"].declare_editable.set(_declare_edit)



            ## TRAVERSAL TOOLS ##
            def traverse_nodes(_node:Node):
                ''' Iterate over node tree, inclusive termination at (n.instance and not n.instance_editable) '''
                yield _node
                if (not _node.instance) or ((_node.instance) and (_node.instance_editable)):
                    for c in _node.children:
                        yield from traverse_nodes(c)

            def mutating_unyielded_generator(yielded:dict[str,Resource], unyielded_src:dict[str,Resource]):
                ''' mutates yielded in place, yield anything not already yielded by dict key
                unyielded_src is being added to during yield intermission via tree traversal discovery
                '''
                unyielded = {k:v for k,v in unyielded_src.items() if not (k in yielded.keys())}
                while len(unyielded.values()) > 0:
                    yield from unyielded.values()
                    yielded.update(unyielded)
                    unyielded = {k:v for k,v in unyielded_src.items() if not (k in yielded.keys())}


            ## EXECUTION ###
            txt_node_root = self.transform_node(session, self)

            # Nodes
            node_tree = {node.get_path(v):v for v in traverse_nodes(self)[1:]}
            _yielded_nodes = copy(node_tree)
            txt_node_tree = yield TRANSFORM_CHILDREN(node_tree.values()) ## Consider: need to sort by name for tree when unclaimed is not none?
            txt_node_tree_unclaimed = yield TRANSFORM_CHILDREN(mutating_unyielded_generator(_yielded_nodes,unclaimed_nodes))
            del _yielded_subres
            
            # Subres
            _yielded_subres = {} #Mutated in place by Subres Generator
            txt_subres = yield TRANSFORM_CHILDREN(mutating_unyielded_generator(_yielded_subres, declared_subres,))
            txt_subres_unclaimed = yield TRANSFORM_CHILDREN(mutating_unyielded_generator(_yielded_subres, unclaimed_subres))
            del _yielded_subres

            # Subres
            integrate_unclaimed_extres() #-> Mutates declared_extres
            txt_extres = yield TRANSFORM_CHILDREN(declared_extres)

            integrate_unclaimed_signals() #-> Mutates declared_signals
            txt_signals = yield TRANSFORM_CHILDREN(declared_signals)
            
            integrate_unclaimed_edits() #-> Mutates declared_edits
            txt_edits = yield TRANSFORM_CHILDREN(declared_edits)
            
            result = "\n".join([
                f'[gd_scene format=4 uid="{node.uid}"]',
                txt_node_root,
                "\n".join(txt_extres),
                "\n".join(txt_subres),
                "\n".join(txt_subres_unclaimed),
                "\n".join(txt_node_tree),
                "\n".join(txt_node_tree_unclaimed),
                "\n".join(txt_signals),
                "\n".join(txt_edits),
            ])

            t0 = session.options["structure"].resource.reset(t0)
            t1 = session.options["structure"].subresource.reset(t1)
            t2 = session.options["structure"].declare_extres.reset(t2)
            t3 = session.options["structure"].declare_subres.reset(t3)
            t4 = session.options["structure"].declare_signal.reset(t4)
            t4 = session.options["structure"].declare_editable.reset(t4)

            return result

class _Settings():
    class GdToPy(GdToPy_Transformer):
        keys = ["file_settings"]
        def transform(self, session, node):
            _properties, _categories = node.children
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)
            categories : tuple[Category] = yield from TRANSFORM_CHILDREN(_categories)
            return Settings(properties=properties, categories=categories)

    class PyToGd(PyToGd_Transformer):
        types = [Settings]

class _Category():
    class GdToPy(GdToPy_Transformer):
        keys = ["category"]
        def transform(self, session, node):
            _name, _properties = node.children
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)
            return Category(str(_name), properties=properties)

    class PyToGd(PyToGd_Transformer):
        types = [Category]
        
class _GdSignal():
    class GdToPy(GdToPy_Transformer):
        keys = ["connection"]
        def transform(self, session, node):
            _options = node.children[0]
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            options["fr"] = options["from"]
            del options["from"]
            return GdSignal(**options)

    class PyToGd(PyToGd_Transformer):
        types = [GdSignal]



gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    _ExtResource.GdToPy,
    _Resource.GdToPy,
    _Resource.GdToPy_File,
    _GdSignal.GdToPy,
    _Promise.GdToPy,
    _Node.GdToPy,
    _Node.GdToPy_File,
    _Settings.GdToPy,
    _Category.GdToPy,
    _Properties.GdToPy,
], 
options = {"structure":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::structure.py", [
    # _ExtResource.PyToGd,
    _Resource.PyToGd,
    _GdSignal.PyToGd,
    _Promise.PyToGd,
    _Node.PyToGd,
    _Settings.PyToGd,
    _Category.PyToGd,
    _Properties.PyToGd,
], 
options = {"structure":PyToGd_Options} 
)