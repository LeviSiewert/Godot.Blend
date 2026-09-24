from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions, cvar_as
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
from ...core.structure import (
    Promise,
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
from typing import Generator, Any
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

class GdToPy_Options(TransformerOptions): ... ## Instanciated at session creation.
class PyToGd_Options(TransformerOptions): ...



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
            _options, _ext_resources, _sub_resources, _node_resources, _edit_flags, _connections = node.children
            # _options, _ext_resources, _sub_resources, _properties = node.children
            assert len(_node_resources.children) > 0
            result : Node = yield TRANSFORM(_node_resources.children[0])


            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            result.__setup_file__(uid=options["uid"])
            result.format= options["format"]

            ext_resources : tuple[Promise] = yield TRANSFORM_CHILDREN(_ext_resources.children)
            sub_resources : tuple[Resource] = yield TRANSFORM_CHILDREN(_sub_resources.children)

            edit_flags = [] 
            for n in _edit_flags.children:
                edit_flags.append(NodePath(n.children[0][0]))

            ## Prepare tree dependencies:
            result.ext_resources.extend(ext_resources)
            result.sub_resources.extend(sub_resources)

            node_namespace = {".": result}
            nodes_unclaimed = {}
            node_resources : tuple[Node] = yield TRANSFORM_CHILDREN(_node_resources.children[1:], as_generator=True)

            for n in node_resources:
                ## Construct node structure from paths, remove temp variable from node.
                p_path = n._parent
                del n._parent
                fullpath : str|None = None

                if p_path == ".":
                    result.children.append(n)
                    fullpath = n.name.key
                    node_namespace[fullpath] = n
                else:
                    fullpath = (p_path + "/" + n.name.key)
                    if p_path in node_namespace.keys():
                        node_namespace[p_path].children.append(n)
                        node_namespace[fullpath] = n
                    else:
                        ## Instance-Overlay edited 
                        nodes_unclaimed[fullpath] = n

                if fullpath in edit_flags:
                    edit_flags.remove(fullpath)
                    n.instance_editable = True

            result.nodes_unclaimed = nodes_unclaimed
            result.edits_unclaimed = edit_flags

            return result
        
    class PyToGd(PyToGd_Transformer):
        types = [Node]

        def transform(self, session, node:Node):
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
            def _declare_subres(x)->str:
                if not (x in declared_subres.values()):
                    if (x.name is None) or (x.name in declared_subres.keys()):
                        ## Key collission, alter object. Object is altered instead of just session dict-key due to desire for stability.
                        x.name = x.type+"_"+"".join(sample(ascii_letters, 9))
                    declared_subres[x.name] = x
                return x.name

            unclaimed_extres = node.unclaimed_extres if (not (node.unclaimed_extres is None)) else tuple()
            _required_extres = [] ## Cache-check deps.
            extres_by_id = {}
            declared_extres = {} ## By UID
            def _declare_extres(value:Resource|Promise)->str:
                ''' Declare a node into this session, returns an ascociated ID from the mapped namespace, prioritized by uid '''
                if isinstance(value, (Resource,File)):
                    if value.uid in declared_extres():
                        return
                    value = value.as_extres_promise()

                if isinstance(value, Promise) and (value.p_type is Promise.Type.EXT_RESOURCE):
                    uid = value.key["uid"]
                    path = value.key["path"]
                    type = value.key["type"]

                    if p:=declared_extres.get(uid,None): ## Return cached
                        return p.value["id"]

                    id = value.key.get("id", None)
                    if (id is None):
                        id = "".join(sample(ascii_letters, 5)) ## Generate non-matching
                        value.key["id"] = id 
                         
                    declared_extres[uid] = value
                    extres_by_id[id] = value
                    return id

                elif isinstance(value, Promise) and (value.p_type is Promise.Type.EXT_RESOURCE_DIRECT):
                    _required_extres.append(value.key)
                    return value.key
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
], 
options = {"structure":PyToGd_Options} 
)