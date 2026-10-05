from typing import Generator, Any, Callable, Iterable
from random import sample, randint
from contextvars import ContextVar
from copy import copy
from string import ascii_letters
from lark import ( Token as LarkToken, Tree as LarkTree )

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

EMPTY_DICT = {}
# EMPTY_DICT.__setitem__ = None


class OPTIONS_GdToPy(TransformerOptions):
    def __init__(self, session):
        self.resource = ContextVar("subresource", default = None)
        self.subresource = ContextVar("subresource", default = None)
        self.properties = ContextVar("properties", default = None)
        
        self.find_extres = ContextVar("find_extres", default = self._find_extres)
        self.find_subres = ContextVar("find_subres", default = self._find_subres)
    resource : ContextVar[Resource|None] = None
    subresource : ContextVar[Resource|None] = None
    properties : ContextVar[Properties|bool|None] = None

    find_extres : ContextVar[Callable] = None
    def _find_extres(self, promise:Promise|str):
        return promise

    find_subres : ContextVar[Callable] = None
    def _find_subres(self, promise:Promise|str):
        return promise
    
class MACROS_GdToPy:
    def pairs_to_dict(session, obj:Iterable):
        r = {}
        for pair in obj: 
            k,v = yield TRANSFORM_CHILDREN(pair.children)
            r[k] = v
        return r

class MACROS:
    def Default(value, default:Any=None, flag:Any=TRANSFORM_CHILDREN, conditional:Callable=lambda x: not (x is None), kwargs:dict=EMPTY_DICT):
        if not conditional(value):
            return value
        res = yield flag(value, **kwargs)
        return res

class OPTIONS_PyToGd(TransformerOptions):
    def __init__(self, session):
        self.resource = ContextVar("subresource", default = None)
        self.subresource = ContextVar("subresource", default = None)
        self.properties = ContextVar("properties", default = None)
        
        self.declare_extres = ContextVar("declare_extres", default = self._declare_extres)
        self.declare_subres = ContextVar("declare_subres", default = self._declare_subres)
        self.declare_editable = ContextVar("declare_editable", default = self._declare_editable)
        self.declare_node = ContextVar("declare_editable", default = self._declare_node)
        self.declare_signal = ContextVar("declare_editable", default = self._declare_signal)
        self.test_flag = ContextVar("test_flag", default = False)
    resource : ContextVar[Resource|None] = None
    subresource : ContextVar[Resource|None] = None
    properties : ContextVar[Properties|bool|None] = None
    test_flag : ContextVar[Any] = None

    declare_extres : ContextVar[Callable] = None
    def _declare_extres(self, promise:Resource|Promise|str)->Promise:
        return None

    declare_subres : ContextVar[Callable] = None
    def _declare_subres(self, promise:Resource|Promise|str)->Promise:
        return promise

    def get_id_contributer(self, session, obj):
    # def get_id_contributer(self, session, obj):
        if not isinstance(obj, Resource):
            return 0

        return hash ((
            not (self.resource.get() is None),
            not (self.subresource.get() is None),
            not (self.properties.get() is None),
        ))

    declare_editable : ContextVar[Callable] = None
    def _declare_editable(self, promise:Node)->None:
        pass

    declare_node : ContextVar[Callable] = None
    def _declare_node(self, promise:Promise|Node)->None:
        ''' return string path of parent, consider seperating that to a dif call'''
        # if isinstance(promise, Promise):
        #     return promise
        return None

    declare_signal : ContextVar[Callable] = None
    def _declare_signal(self, promise:Promise|Node)->None:
        ''' return string path of parent, consider seperating that to a dif call'''
        # if isinstance(promise, Promise):
        #     return promise
        return None
        

    
class MACROS_PyToGd:
    def dict_to_str(session, obj:dict, strip_key:bool=True, pair_join:str="=", entry_join:str=", ", leading:str="", sort_func = lambda kv: kv[0]):
        key_gen = yield TRANSFORM_CHILDREN(obj.keys(),   as_generator=True)
        obj_gen = yield TRANSFORM_CHILDREN(obj.values(), as_generator=True)
        
        if strip_key:
            pairs = sorted([(k.strip('"'),v) for k,v in  zip(key_gen, obj_gen)], key = sort_func)
            res = entry_join.join(f"{k}{pair_join}{v}" for k,v in pairs)
        else:
            pairs = sorted([(k,v) for k,v in  zip(key_gen, obj_gen)], key = sort_func)
            res = entry_join.join(f"{k}{pair_join}{v}" for k,v in pairs)
    
        if res != "":
            return leading + res
        return res


class _GdSignal():
    class GdToPy(GdToPy_Transformer):
        keys = ["connection"]
        def transform(self, session, node:LarkTree):
            _options = node.children[0].children
            options = yield from MACROS_GdToPy.pairs_to_dict(session, _options)
            options["fr"] = options.pop("from")
            return GdSignal(**options)

    class PyToGd(PyToGd_Transformer):
        types = [GdSignal]        
        key_order = (
            "signal",
            "from",
            "to",
            "method",
            "flags",
            "unbinds",
            "binds",
        )
        def transform(self, session, node:GdSignal):
            _options = copy(node.kwargs)
            _options["from"] = _options.pop("fr")
            options : str = yield from MACROS_PyToGd.dict_to_str(session, _options, pair_join="=", entry_join=" ", leading=" ", sort_func=lambda kv: self.key_order.index(kv[0]))
            return f'[connection{options}]'

class _ExtResource():
    class GdToPy(GdToPy_Transformer):
        keys = ["ext_resource"]
        def transform(self, session, node:LarkTree)->Generator[Any,Any,Promise]:
            _options = node.children[0].children
            options : dict = yield from MACROS_GdToPy.pairs_to_dict(session, _options)
            return Promise(options, Promise.Type.EXT_RESOURCE)
    # class PyToGd(PyToGd_Transformer):... ## Using _Promise

class _Promise():
    class GdToPy(GdToPy_Transformer):
        keys = ["ref_subresource","ref_extresource","ref_resource"]
        def transform(self, session, node:LarkTree)->Generator:
            match node.data:
                case "ref_subresource":
                    typing = yield from MACROS.Default(node.children[0])
                    key = yield TRANSFORM(node.children[1])
                    return session.options["structure"].find_subres.get()(Promise(key, Promise.Type.SUB_RESOURCE, typing=typing))
                case "ref_extresource":
                    typing = yield from MACROS.Default(node.children[0])
                    key = yield TRANSFORM(node.children[1])
                    return session.options["structure"].find_extres.get()(Promise(key, Promise.Type.EXT_RESOURCE_DIRECT, typing=typing))
                case "ref_resource":
                    raise NotImplementedError()
    class PyToGd(PyToGd_Transformer):
        memoized = False ##TODO: Determine root of bug that's causing this to be a fix
        types = [Promise]
        extres_options_order = ("type","uid","path","id")
        def transform(self, session, node:Promise):
            match node.p_type:
                case Promise.Type.EXT_RESOURCE_DIRECT:
                    return f'ExtResource("{node.key}")'
                case Promise.Type.EXT_RESOURCE:
                    if not (session.options["structure"].properties.get() is None):
                        session.options["structure"].declare_extres.get()(node)
                        return f'ExtResource("{node.key["id"]}")'
                    options = yield from MACROS_PyToGd.dict_to_str(session, node.key, pair_join="=", entry_join=" ", sort_func=lambda kv:self.extres_options_order.index(kv[0])) 
                    return f'[ext_resource {options}]'
                case Promise.Type.SUB_RESOURCE:
                    session.options["structure"].declare_subres.get()(node)
                    return f'SubResource("{node.key}")'
                case Promise.Type.RESOURCE:
                    raise NotImplementedError()
                case Promise.Type.FILE:
                    raise NotImplementedError()
            return super().transform(session, node)
class _SubResource():
    class GdToPy(GdToPy_Transformer):
        keys = ["sub_resource"]
        def transform(self, session, node:LarkTree):
            _options, _properties = node.children
            options : dict = yield from MACROS_GdToPy.pairs_to_dict(session, _options.children)

            res = Resource(**options)
            yield STEP("INITIAL", res)

            # if not (res.instance is None):
            #     res.instance = session.options["structure"].find_extres.get()(res.instance)
                ## find_editable is tempting, but better suited to the file level.
            
            properties : Properties = yield TRANSFORM(_properties)
            # raise Exception(res.name, properties)
            res.properties.update(properties)
            return res
    
    class PyToGd(PyToGd_Transformer):
        header_order = (
            "type",
            "script",
            "instance",
            "id",
        )
        def match(self, session, node):
            ''' Match only Non-Node SubResource '''
            if (not isinstance(node,Resource)) or isinstance(node,Node):
                return False
            
            return all([
                node.uid is None,
                node.file is None,
            ])
            
        def transform(self, session, node:Resource)->Generator[Any,Any,str]:

            # Contextually a Promise #
            if not (session.options["structure"].properties.get() is None):
                # Escape to promise if within context of properties #
                p : Promise = session.options["structure"].declare_subres.get()(node)
                r : str = yield TRANSFORM(p)
                return r

            t0 = session.options["structure"].subresource.set(node)
            # Ensure #
            self.ensure_fmt(node)

            # Header #
            header = {k:v for k,v in {
                "type" : node.gdtype if node.gdtype else "Resource",
                "script" : node.gdscript,
                "instance" : node.instance,
                "id" : node.name,
            }.items() if (not (v is None))}

            t = session.options["structure"].properties.set(True)
            txt_header_options = yield from MACROS_PyToGd.dict_to_str(session, header , leading=" ", entry_join=" ", sort_func=lambda kv: self.header_order.index(kv[0]))
            session.options["structure"].properties.reset(t)
            
            # Properties #
            txt_properties = yield TRANSFORM(node.properties)

            # Context Declarations #
            if node.instance_editable and (not (node.instance is None)):
                session.options["structure"].declare_editable.get()(node)

            # Compile #
            result = f"[sub_resource{txt_header_options}]"+"\n"+txt_properties
            
            # Reset Context #
            session.options["structure"].subresource.reset(t0)

            # Return #
            return result

        def ensure_fmt(self, node:Resource)->None:
            if node.name is None:
                node.name = "".join(sample(ascii_letters, 9))

class _Resource():
    class GdToPy(GdToPy_Transformer):
        keys = ["file_resource"]

        def transform(self, session, node):
            ''' Process is:
            - Convert Extres
            - Convert SubRes INITIAL
            - set structure.find_...
            - Convert Properties
            - Create Result
            - Convert SubRes complete
            - Gather unclaimed, set to result
            - return result
            '''

            t0 = session.options["structure"].resource.set(node)
            t1 = session.options["structure"].subresource.set(node)

            _options, _ext_resources, _sub_resources, _properties = node.children

            _ext_resources_gen = yield TRANSFORM_CHILDREN(_ext_resources.children, as_generator=True)
            ext_resources : dict[str, Promise] = dict({v.key["id"]:v for v in _ext_resources_gen}) 
            ext_resources_missing : list[Promise] = []
            ext_resources_claimed : list[str] = []
            
            def find_extres(promise:Promise)->Promise|Promise:
                r = ext_resources.get(promise.key,None)
                if r is None:
                    ext_resources_missing.append(promise)
                    return r
                ext_resources_claimed.append(promise.key)
                return r
            
            t2 = session.options["structure"].find_extres.set(find_extres)
            
            sub_resources = {}
            # sub_resources : dict[str, Resource] = dict({v.name:v for v in _sub_resources_gen})
            sub_resources_missing : list[Promise] = []
            sub_resources_claimed : list[str] = []

            def find_subres(promise:Promise)->Promise|Resource:
                r = sub_resources.get(promise.key,None)
                if r is None:
                    sub_resources_missing.append(promise)
                    return promise
                sub_resources_claimed.append(promise.key)
                return r
                
            t3 = session.options["structure"].find_subres.set(find_subres)
            
            _sub_resources_gen = yield TRANSFORM_CHILDREN(_sub_resources.children, step="INITIAL", as_generator=True)
            ## WARNING: Initial transform sets the context and does not *currently* allow mutation, thus
            ## t3 is set before accessing and updating 
            sub_resources.update({v.name:v for v in _sub_resources_gen})
            
            yield TRANSFORM_CHILDREN(_sub_resources.children)
        
            t = session.options["structure"].properties.set(True)
            options = yield from MACROS_GdToPy.pairs_to_dict(session, _options.children)
            properties = yield TRANSFORM(_properties)
            session.options["structure"].properties.reset(t)

            res = Resource(**options, 
                properties=properties,
                unclaimed_extres=dict({k:v for k,v in ext_resources.items() if not (k in ext_resources_claimed)}), 
                unclaimed_subres=dict({k:v for k,v in sub_resources.items() if not (k in sub_resources_claimed)}), 
            )

            session.options["structure"].resource.reset(t0)
            session.options["structure"].subresource.reset(t1)
            session.options["structure"].find_extres.reset(t2)
            session.options["structure"].find_subres.reset(t3)


            return res

    class PyToGd(PyToGd_Transformer):
        header_order = (
            "type",
            "format",
            "script",
            "instance",
            "uid",
        )
        def match(self, session, node):
            ''' Match only Non-Node SubResource '''
            if (not isinstance(node,Resource)) or isinstance(node,Node):
                return False
            return any([
                not (node.uid is None),
                not (node.file is None),
            ])


        def transform(self, session, node:Resource):
            ''' Discovery during transformation requires context escape. declare_extres, declare_subres, declare_edit, ect are that method 
            For FUCKING SANITY, we are assuming the structure is somewhat normalized.
            later I'll consider implications of non-normalized a bit more. 
            '''

            # Contextually a Promise #
            if not (session.options["structure"].resource.get() is None):
                # Escape to promise if within context of properties #
                p : Promise = session.options["structure"].declare_extres(node)
                r : str = yield TRANSFORM(p)
                return r

            t0 = session.options["structure"].resource.set(node)
            t1 = session.options["structure"].subresource.set(node)

            _declared_subres : dict[str, Resource] = node.unclaimed_subres if node.unclaimed_subres else {} ## By Id 
            _promised_subres : dict[str, Promise] = dict({k:Promise(k, Promise.Type.SUB_RESOURCE) for k,_ in _declared_subres.items()})

            _declared_extres : dict[str, Promise|Resource] = node.unclaimed_extres if node.unclaimed_extres else {} ## By Uid
            _promised_extres : dict[str, Promise] = {}
            for v in _declared_extres.values():
                if isinstance(v, Promise):
                    _promised_extres[v.key["id"]] = Promise(v.key["id"], Promise.Type.EXT_RESOURCE_DIRECT)
                else:
                    _promised_extres[v.key["id"]] = Promise(v.uid, Promise.Type.EXT_RESOURCE_DIRECT)
            
            def declare_subres(obj:Resource|Promise)->Promise:
                if isinstance(obj,Promise):
                    _promised_subres[obj.key] = obj
                    return obj
                elif not isinstance(obj, Resource):
                    raise TypeError(obj)

                # Ensure Format #
                if obj.name is None:
                    obj.name = "".join(sample(ascii_letters,9))

                # Declare Subres # 
                _declared_subres[obj.name] = obj

                # Create and store promise #
                promise = Promise(obj.name, Promise.Type.SUB_RESOURCE)
                _promised_subres[obj.name] = promise

                return promise

            def declare_extres(obj:Resource|Promise)->Promise:
                ''' Declare Extres into local scope and return an escape (Promise.Type.EXT_RESOURCE_DIRECT)'''
                
                if isinstance(obj, Resource):
                    ## Convert object reference to promise
                    if obj.uid is None:
                        obj.uid = "".join(sample(ascii_letters, 9))
                    
                    if (res:=_declared_extres.get(obj.uid, None)) is None:
                        ## DEFER TODO:  If a tree is fully  constructed or partly constructed and this is found first, IDs are regerenated. Cache them on obj?
                        i = "".join(sample(ascii_letters, 5))

                        promise : Promise
                        if isinstance(obj,Node):
                            promise = Promise({"uid":obj.uid, "path":obj.path, "id":i, "type":"PackedScene"}, Promise.Type.EXT_RESOURCE)
                        # elif isinstance(obj, GdScript): ## TODO
                        #     p.key["type"] = "Script"
                        else: # isinstance(obj,Resource):
                            promise = Promise({"uid":obj.uid, "path":obj.path, "id":i, "type":"Resource"}, Promise.Type.EXT_RESOURCE)

                        promise_direct = Promise(i, Promise.Type.EXT_RESOURCE_DIRECT)
                        
                        _declared_extres[obj.uid] = promise
                        _promised_extres[i] = promise_direct
                        return promise_direct
                    else:
                        return _promised_extres[res.key["id"]]

                if isinstance(obj,Promise) and (obj.p_type is Promise.Type.EXT_RESOURCE_DIRECT):
                    ## Store in sanity check for later, return
                    _promised_extres[obj.key] = obj
                    return obj

                if isinstance(obj,Promise) and (obj.p_type is Promise.Type.EXT_RESOURCE):
                    if (res:=_declared_extres.get(obj.key["uid"], None)) is None:
                        ## Assign and generate returned promise

                        ## Ensure it has an id
                        k = obj.key.get("id",None)
                        if (k is None) or (k in _promised_extres.keys()):
                            obj.key["id"] = "".join(sample(ascii_letters,9))

                        p = Promise(obj.key["id"], Promise.Type.EXT_RESOURCE_DIRECT)

                        _declared_extres[obj.key["uid"]] = obj
                        _promised_extres[obj.key["id"]] = p
                        return p
                        
                    else:
                        ## If it does exist, return the promise that references this promise
                        return _promised_extres[obj.key["id"]]

                raise TypeError(obj)

            from collections import OrderedDict
            def yield_mutating_dict(di:dict, keys:list, flag=TRANSFORM_CHILDREN, kwargs:dict=EMPTY_DICT):
                result = []
                to_yield = OrderedDict((k,v) for k,v in di.items() if not (k in keys))
                while len(to_yield) > 0:
                    res = yield flag(to_yield.values(), **kwargs)
                    result.extend(res)
                    keys.extend(to_yield.keys())
                    to_yield = OrderedDict((k,v) for k,v in di.items() if not (k in keys))
                return result

            # Header #
            header = {k:v for k,v in {
                "type" : node.gdtype if node.gdtype else "Resource",
                "format" : node.format if node.format else 4,
                "script" : node.gdscript,
                "instance" : node.instance,
                "uid" : "uid://"+node.uid,
            }.items() if (not (v is None))}
        
            _yielded_subres = []
            _yielded_extres = []


            t2 = session.options["structure"].declare_subres.set(declare_subres)
            t3 = session.options["structure"].declare_extres.set(declare_extres)

            t4 = session.options["structure"].properties.set(True)
            txt_header_options = yield from MACROS_PyToGd.dict_to_str(session, header , leading=" ", entry_join=" ", sort_func=lambda kv: self.header_order.index(kv[0]))
            session.options["structure"].properties.reset(t4)

            txt_properties  : str = yield TRANSFORM(node.properties)
            txt_subresource : list = yield from yield_mutating_dict(_declared_subres, _yielded_subres)
            txt_extresource : list = yield from yield_mutating_dict(_declared_extres, _yielded_extres)

            # if len(_declared_extres)>0:
            #     # raise Exception(_declared_extres)
            #     raise Exception(session.memo[session.get_id(_declared_extres["cjkvk7qbv5oby"])])

            session.options["structure"].resource.reset(t0)
            session.options["structure"].subresource.reset(t1)
            session.options["structure"].declare_subres.reset(t2)
            session.options["structure"].declare_extres.reset(t3)

            return "\n".join([
                f"[gd_resource{txt_header_options}]\n",
                *reversed(txt_extresource),
                *reversed(txt_subresource),
                "[resource]\n"+txt_properties if len(node.properties) else ""
            ])

class _Properties():
    class PyToGd(PyToGd_Transformer):
        types = [Properties]
        def transform(self, session, node):
            t = session.options["structure"].properties.set(node)

            res = yield from MACROS_PyToGd.dict_to_str(session, node.data, entry_join="\n")

            session.options["structure"].properties.reset(t) 
            return res

    class GdToPy(GdToPy_Transformer):
        keys = ["properties"]
        def transform(self, session, node:Properties):
            t = session.options["structure"].properties.set(node)

            data = yield from MACROS_GdToPy.pairs_to_dict(session, node.children)
            res = Properties(data)

            session.options["structure"].properties.reset(t) 
            return res

class _Node():
    class GdToPy(GdToPy_Transformer):
        keys = ["node_resource"]
        def transform(self, session, node:LarkTree):
            _options, _properties = node.children
            options : dict = yield from MACROS_GdToPy.pairs_to_dict(session, _options.children)

            if "nodepaths" in options.keys():
                ## discard, used in tscn fmt 3 as an load optimization
                del options["nodepaths"]

            if "parent" in options.keys():
                options["_parent"] = options.pop("parent")
            
            res = Node(**options)
            yield STEP("INITIAL", res)

            # if not (res.instance is None):
            #     res.instance = session.options["structure"].find_extres.get()(res.instance)
                ## find_editable is tempting, but better suited to the file level.
            
            properties : Properties = yield TRANSFORM(_properties)
            # raise Exception(res.name, properties)
            res.properties.update(properties)
            return res

    class PyToGd(PyToGd_Transformer):
        header_order = (
            "name",
            "type",
            "script",
            "parent",
            "unique_id",
            "instance",
        )

        def match(self, session, node):
            ''' Match only Non-Node SubResource '''
            if (not isinstance(node,Node)):
                return False
            return all([
                node.uid is None,
                node.file is None,
            ])
        
        def transform(self, session, node:Node)->Generator[Any,Any,str]:
            # Contextually a Promise #
            if not (session.options["structure"].properties.get() is None):
                # Escape to promise if within context of properties #
                p : Promise = session.options["structure"].declare_node.get()(node)
                r : str = yield TRANSFORM(p)
                return r

            t0 = session.options["structure"].subresource.set(node)
            # Ensure #
            self.ensure_fmt(node)

            # Header #
            _parent = session.options["structure"].declare_node.get()(node)
            header = {k:v for k,v in {
                "type" : node.gdtype if node.gdtype else "Node",
                "script" : node.gdscript,
                "instance" : node.instance,
                "name" : node.name,
                "parent" : _parent if (not (_parent is None)) else node._parent,
                "unique_id" : node.unique_id,
            }.items() if (not (v is None))}

            if header.get("parent", None) is None:
                ## Sanity check
                _c_res = session.options["structure"].resource.get()
                if not ((_c_res is node) or (_c_res is None)):
                    raise Exception(header)
                del _c_res

            t = session.options["structure"].properties.set(True)
            txt_header_options = yield from MACROS_PyToGd.dict_to_str(session, header , leading=" ", entry_join=" ", sort_func=lambda kv: self.header_order.index(kv[0]))

            session.options["structure"].properties.reset(t)
            
            # Properties #
            txt_properties = yield TRANSFORM(node.properties)

            # Context Declarations #
            if node.instance_editable:
                session.options["structure"].declare_editable.get()(node)
            for c in node.children.values():
                session.options["structure"].declare_node.get()(c)
            for c in node.signals:
                session.options["structure"].declare_signal.get()(c)

            # Compile #
            result = f"[node{txt_header_options}]"+"\n"+txt_properties
            
            # Reset Context #
            session.options["structure"].subresource.reset(t0)

            # Return #
            return result

        def ensure_fmt(self, node:Resource)->None:
            if node.name is None:
                node.name = "".join(sample(ascii_letters, 9))

class _Scene():
    class GdToPy(PyToGd_Transformer):
        keys = ["file_scene"]

    class PyToGd(_Node.PyToGd):
        scene_header_order = (
            "format",
            "uid",
        )
        def match(self, session, node):
            ''' Match only Non-Node SubResource '''
            if (not isinstance(node,Node)):
                return False
            return any([
                not (node.uid is None),
                not (node.file is None),
            ])

        def transform(self, session, node:Node):

            if not (session.options["structure"].resource.get() is None):
                # Escape to promise if within context of properties #
                p : Promise = session.options["structure"].declare_extres.get()(node)
                r : str = yield TRANSFORM(p)
                return r

            t0 = session.options["structure"].resource.set(node)
            t1 = session.options["structure"].subresource.set(node)
            
            _declared_subres : dict[str, Resource] = node.unclaimed_subres if node.unclaimed_subres else {} ## By Id 
            _promised_subres : dict[str, Promise] = dict({k:Promise(k, Promise.Type.SUB_RESOURCE) for k,_ in _declared_subres.items()})
            
            _declared_extres : dict[str, Promise|Resource] = node.unclaimed_extres if node.unclaimed_extres else {} ## By Uid
            _promised_extres : dict[str, Promise] = {}

            _declared_nodes : dict[str, Node] = node.unclaimed_nodes if node.unclaimed_nodes else {} 

            _declared_editable : list[str] = node.unclaimed_editable if node.unclaimed_editable else []
            _declared_signals : list[GdSignal] = node.unclaimed_signals if node.unclaimed_signals else []

            for v in _declared_extres.values():
                if isinstance(v, Promise):
                    _promised_extres[v.key["id"]] = Promise(v.key["id"], Promise.Type.EXT_RESOURCE_DIRECT)
                else:
                    _promised_extres[v.key["id"]] = Promise(v.uid, Promise.Type.EXT_RESOURCE_DIRECT)
            
            def declare_subres(obj:Resource|Promise)->Promise:
                if isinstance(obj,Promise):
                    _promised_subres[obj.key] = obj
                    return obj
                elif not isinstance(obj, Resource):
                    raise TypeError(obj)

                # Ensure Format #
                if obj.name is None:
                    obj.name = "".join(sample(ascii_letters,9))

                # Declare Subres # 
                _declared_subres[obj.name] = obj

                # Create and store promise #
                promise = Promise(obj.name, Promise.Type.SUB_RESOURCE)
                _promised_subres[obj.name] = promise

                return promise

            def declare_extres(obj:Resource|Promise)->Promise:
                ''' Declare Extres into local scope and return an escape (Promise.Type.EXT_RESOURCE_DIRECT)'''


                if obj is node:
                    raise Exception("Recursive!")
                
                if isinstance(obj, Resource):
                    ## Convert object reference to promise
                    if obj.uid is None:
                        obj.uid = "".join(sample(ascii_letters, 9))
                    
                    if (res:=_declared_extres.get(obj.uid, None)) is None:
                        ## DEFER TODO:  If a tree is fully  constructed or partly constructed and this is found first, IDs are regerenated. Cache them on obj?
                        i = "".join(sample(ascii_letters, 5))

                        promise : Promise
                        if isinstance(obj,Node):
                            assert not (obj.file is None)
                            promise = Promise({"uid":obj.uid, "path":obj.file, "id":i, "type":"PackedScene"}, Promise.Type.EXT_RESOURCE)
                        # elif isinstance(obj, GdScript): ## TODO
                        #     p.key["type"] = "Script"
                        else: # isinstance(obj,Resource):
                            assert not (obj.file is None)
                            promise = Promise({"uid":obj.uid, "path":obj.file, "id":i, "type":"Resource"}, Promise.Type.EXT_RESOURCE)

                        promise_direct = Promise(i, Promise.Type.EXT_RESOURCE_DIRECT)
                        
                        _declared_extres[obj.uid] = promise
                        _promised_extres[i] = promise_direct
                        return promise_direct
                    else:
                        return _promised_extres[res.key["id"]]

                if isinstance(obj,Promise) and (obj.p_type is Promise.Type.EXT_RESOURCE_DIRECT):
                    ## Store in sanity check for later, return
                    _promised_extres[obj.key] = obj
                    return obj

                if isinstance(obj,Promise) and (obj.p_type is Promise.Type.EXT_RESOURCE):
                    if (res:=_declared_extres.get(obj.key["uid"], None)) is None:
                        ## Assign and generate returned promise

                        ## Ensure it has an id
                        k = obj.key.get("id",None)
                        if (k is None) or (k in _promised_extres.keys()):
                            obj.key["id"] = "".join(sample(ascii_letters,9))

                        p = Promise(obj.key["id"], Promise.Type.EXT_RESOURCE_DIRECT)

                        _declared_extres[obj.key["uid"]] = obj
                        _promised_extres[obj.key["id"]] = p
                        return p
                        
                    else:
                        ## If it does exist, return the promise that references this promise
                        return _promised_extres[obj.key["id"]]

                raise TypeError(obj)

            def declare_node(obj:Node)->str:
                ''' contextual declaration, return parent node path '''

                if obj is node:
                    return None

                p = node.get_path(obj)
                assert not (".." in p)

                _declared_nodes[p] = obj

                l = p.split("/")
                if len(l) == 2:
                    # if child, ie "./node" return "."
                    return "."
                else:
                    # if obj.name == "E":
                    #     raise Exception(l)
                    # raise Exception(l[1:-1])
                    # if nested, return "./.../node" without leading "./" or trailing "node"
                    
                    return "/".join(l[1:-1])
                    # raise Exception(l)

            def declare_editable(obj:Node)->None:
                p = node.get_path(obj)
                l = p.split("/")

                if len(l) == 1:
                    _declared_editable.append(".")
                else:
                    _declared_editable.append("/".join(l[1:len(l)]))

            def declare_signal(obj:GdSignal)->None:
                _declared_signals.append(obj)
                
            from collections import OrderedDict
            def yield_mutating_dict(di:dict, keys:list, flag=TRANSFORM_CHILDREN, kwargs:dict=EMPTY_DICT):
                result = []
                to_yield = OrderedDict((k,v) for k,v in di.items() if not (k in keys))
                while len(to_yield) > 0:
                    res = yield flag(to_yield.values(), **kwargs)
                    result.extend(res)
                    keys.extend(to_yield.keys())
                    to_yield = OrderedDict((k,v) for k,v in di.items() if not (k in keys))
                return result

            header = {k:v for k,v in {
                    "format" : node.format if node.format else 4,
                    "uid" : "uid://"+node.uid,
                }.items() if (not (v is None))}
            
            _yielded_nodes = []
            _yielded_subres = []
            _yielded_extres = []

            t2 = session.options["structure"].declare_subres.set(declare_subres)
            t3 = session.options["structure"].declare_extres.set(declare_extres)
            t4 = session.options["structure"].declare_editable.set(declare_editable)
            t5 = session.options["structure"].declare_node.set(declare_node)
            t6 = session.options["structure"].declare_signal.set(declare_signal)

            t7 = session.options["structure"].properties.set(True)
            txt_header_options = yield from MACROS_PyToGd.dict_to_str(session, header , leading=" ", entry_join=" ", sort_func=lambda kv: self.scene_header_order.index(kv[0]))
            session.options["structure"].properties.reset(t7)


            txt_root : str  = yield from super().transform(session, node)
            txt_nodes : list = yield from yield_mutating_dict(_declared_nodes, _yielded_nodes)
            txt_subresource : list = yield from yield_mutating_dict(_declared_subres, _yielded_subres)
            txt_extresource : list = yield from yield_mutating_dict(_declared_extres, _yielded_extres)
            txt_editables : list = [f'[editable path="{x}"]' for x in _declared_editable]
            txt_signals : list = yield TRANSFORM_CHILDREN(_declared_signals)

            session.options["structure"].resource.reset(t0)
            session.options["structure"].subresource.reset(t1)
            session.options["structure"].declare_subres.reset(t2)
            session.options["structure"].declare_extres.reset(t3)
            session.options["structure"].declare_editable.reset(t4)
            session.options["structure"].declare_node.reset(t5)
            session.options["structure"].declare_signal.reset(t6)


            return "\n".join([
                f"[gd_scene{txt_header_options}]\n",
                *reversed(txt_extresource),
                *reversed(txt_subresource),
                txt_root,
                *txt_nodes,
                *txt_editables,
                *txt_signals,
            ])


gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    _GdSignal.GdToPy,
    _SubResource.GdToPy,
    _Properties.GdToPy,
    _ExtResource.GdToPy,
    _Promise.GdToPy,
    _Resource.GdToPy,
    _Node.GdToPy,
    _Scene.GdToPy,
], 
options = {"structure":OPTIONS_GdToPy}
)

py_to_gd = PyToGd_TransformerSet("STD::structure.py", [
    _GdSignal.PyToGd,
    _SubResource.PyToGd,
    _Properties.PyToGd,
    # _ExtResource.GdToPy,
    _Promise.PyToGd,
    _Resource.PyToGd,
    _Node.PyToGd,
    _Scene.PyToGd,
], 
options = {"structure":OPTIONS_PyToGd} 
)