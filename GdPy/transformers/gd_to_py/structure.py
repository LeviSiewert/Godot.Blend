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



class OPTIONS_GdToPy(TransformerOptions):
    def __init__(self, session):
        self.properties = ContextVar("properties", default = None)
        self.subresource = ContextVar("subresource", default = None)
        
        self.find_extres = ContextVar("find_extres", default = self._find_extres)
    properties : ContextVar[Properties|bool|None] = None
    subresource : ContextVar[Resource|None] = None

    find_extres : ContextVar[Callable] = None
    def _find_extres(self, promise:Promise|str):
        return promise
    
class MACROS_GdToPy:
    def pairs_to_dict(session, obj:Iterable):
        r = {}
        for pair in obj: 
            k,v = yield TRANSFORM_CHILDREN(pair.children)
            r[k] = v
        return r

class MACROS:
    def Default(value, default:Any=None, flag:Any=TRANSFORM_CHILDREN, conditional:Callable=lambda x: not (x is None), kwargs:dict=tuple()):
        if not conditional(value):
            return value
        res = yield flag(value, **kwargs)
        return res

class OPTIONS_PyToGd(TransformerOptions):
    def __init__(self, session):
        self.properties = ContextVar("properties", default = None)
        self.subresource = ContextVar("subresource", default = None)
        
        self.declare_extres = ContextVar("declare_extres", default = self._declare_extres)
    properties : ContextVar[Properties|bool|None] = None
    subresource : ContextVar[Resource|None] = None

    declare_extres : ContextVar[Callable] = None
    def _declare_extres(self, promise:Promise|str):
        return promise
    
    def get_id_contributer(self, session, obj):
        ''' Cache id space "shifting", called per get_id '''
        if not isinstance(obj, Resource):
            return 0
        return hash ([
            not (self.resource.get() is None),
            not (self.subresource.get() is None),
            not (self.properties.get() is None),
        ])
    
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
                    raise NotImplementedError()
                case "ref_extresource":
                    typing = yield from MACROS.Default(node.children[0])
                    key = yield TRANSFORM(node.children[1])
                    return session.options["structure"].find_extres.get()(Promise(key, Promise.Type.EXT_RESOURCE_DIRECT, typing=typing))
                case "ref_resource":
                    raise NotImplementedError()
    class PyToGd(PyToGd_Transformer):
        types = [Promise]
        extres_options_order = ("type","uid","path","id")
        def transform(self, session, node:Promise):
            match node.p_type:
                case Promise.Type.EXT_RESOURCE_DIRECT:
                    return f'ExtResource("{node.key}")'
                case Promise.Type.EXT_RESOURCE:
                    if not (session.options["structure"].properties.get() is None):
                        return f'ExtResource("{node.key["id"]}")'
                    options = yield from MACROS_PyToGd.dict_to_str(session, node.key, pair_join="=", entry_join=" ", sort_func=lambda kv:self.extres_options_order.index(kv[0])) 
                    return f'[ext_resource {options}]'
                case Promise.Type.SUB_RESOURCE:
                    raise NotImplementedError()
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
            yield STEP("INTIAL", res)

            if not (res.instance is None):
                res.instance = session.options["structure"].find_extres.get()(res.instance)
                ## find_editable is tempting, but better suited to the file level.
            
            properties : Properties = yield TRANSFORM(_properties)
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
                not (node.uid is None),
                not (node.file is None),
            ])
        def transform(self, session, node:Resource)->Generator[Any,Any,str]:

            # Contextually a Promise #
            if not (session.options["structure"].properties.get() is None):
                # Escape to promise if within context of properties #
                p : Promise = session.options["structure"].declare_subres(node)
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
            if node.instance_editable:
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

    class PyToGd(PyToGd_Transformer):
        header_order = (
            "format",
            "type",
            "script",
            "instance",
            "uid",
        )
        def match(self, session, node):
            ''' Match only Non-Node SubResource '''
            if (not isinstance(node,Resource)) or isinstance(node,Node):
                return False
            return any([
                (node.uid is None),
                (node.file is None),
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
            _promised_subres : dict[str, Promise] = dict({p.key["id"]:Promise(p.key["id"] for p in _declared_subres.items())}) ## By Id, sanity check obj for errors/warnings 

            _declared_extres : dict[str, Promise] = node.unclaimed_extres if node.unclaimed_extres else {} ## By Uid
            _promised_extres : dict[str, Promise] = dict({p.key["id"]:Promise(p.key["id"] for p in _declared_extres.items())}) ## By Id, sanity check obj for errors/warnings 
            
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
                if isinstance(obj, Resource):
                    if obj.uid is None:
                        obj.uid = "".join(sample(ascii_letters, 9))
                    
                    if (res:=_declared_extres.get(obj.uid, None)) is None:
                        ## DEFER TODO:  If a tree is fully  constructed or partly constructed and this is found first, IDs are regerenated. Cache them on obj?
                        i = "".join(sample(ascii_letters, 5))

                        p = Promise({"uid":obj.uid, "path":obj.path, "id":i}, Promise.Type.EXT_RESOURCE)
                        pd = Promise(i, Promise.Type.EXT_RESOURCE_DIRECT)

                        if isinstance(obj,Node):
                            p.key["type"] = "scene"
                        # DEFER TODO : GdScript
                        # elif isinstance(obj, GdScript):
                        #     p.key["type"] = "Script"
                        elif isinstance(obj,Resource):
                            p.key["type"] = "Resource"

                        _declared_extres[i] = p
                        _promised_extres[i] = pd
                        return pd

                if isinstance(obj,Promise):
                    if obj.p_type is Promise.Type.EXT_RESOURCE_DIRECT:
                        _promised_extres[obj.key] = obj
                        return obj

                    if obj.p_type is Promise.Type.EXT_RESOURCE:

                        if (res:=_declared_extres.get(obj.key["uid"], None)) is None:
                            ## Generate key, id if doesnt exist or isnt unique.
                            _declared_extres[obj.key["uid"]] = obj

                            k = obj.key.get("id",None)
                            if (k is None) or (k in _promised_extres.keys()):
                                obj.key["id"] = "".join(sample(ascii_letters,9))
                            
                            p = Promise(obj.key["id"], Promise.Type.EXT_RESOURCE_DIRECT)
                            _promised_extres[obj.key["id"]] = p
                            return p
                            
                        else:
                            return Promise(res.key["id"], Promise.Type.EXT_RESOURCE_DIRECT)

                raise TypeError(obj)

            from collections import OrderedDict
            def yield_mutating_dict(di:dict, keys:list, flag=TRANSFORM_CHILDREN, kwargs:dict=tuple()):
                result = []
                to_yield = OrderedDict((k,v) for k,v in di.items() if not (k in keys))
                while len(to_yield) > 0:
                    res = yield flag(to_yield.values(), **kwargs)
                    result.extend(res)
                    keys.extend(to_yield.keys())
                    to_yield = OrderedDict((k,v) for k,v in di.items() if not (k in keys))

            # Header #
            header = {k:v for k,v in {
                "format" : node.format if node.format else 4,
                "type" : node.gdtype if node.gdtype else "Resource",
                "script" : node.gdscript,
                "instance" : node.instance,
                "uid" : node.gdtype if node.gdtype else "Resource",
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
            txt_extresource : list = yield from yield_mutating_dict(_declared_subres, _yielded_extres)

            session.options["structure"].resource.reset(t0)
            session.options["structure"].subresource.reset(t1)
            session.options["structure"].declare_subres.reset(t2)
            session.options["structure"].declare_extres.reset(t3)

            return "\n".join([
                f"[gd_resource{txt_header_options}]\n",
                *txt_extresource,
                *txt_subresource,
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

gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    _GdSignal.GdToPy,
    _SubResource.GdToPy,
    _Properties.GdToPy,
    _ExtResource.GdToPy,
    _Promise.GdToPy,
    _Resource.GdToPy,
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
], 
options = {"structure":OPTIONS_PyToGd} 
)