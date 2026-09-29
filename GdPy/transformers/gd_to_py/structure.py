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
    properties : ContextVar[Properties|None] = None

class MACROS_GdToPy:
    def pairs_to_dict(session, obj:Iterable):
        r = {}
        for pair in obj: 
            k,v = yield TRANSFORM_CHILDREN(pair.children)
            r[k] = v
        return r


class OPTIONS_PyToGd(TransformerOptions):
    def __init__(self, session):
        self.properties = ContextVar("properties", default = None)
    properties : ContextVar[Properties|None] = None

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
                    raise NotImplementedError()
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
            options : dict = yield from MACROS_GdToPy.pairs_to_dict(_options.children)

            res = Resource(**options)
            yield STEP("INTIAL", res)

            if not (res.instance is None):
                res.instance = session.options["structure"].find_extres.get()(res.instance)
                ## find_editable is tempting, but better suited to the file level.
            
            properties : Properties = yield TRANSFORM(_properties)
            properties.context.set_extends(res.context)
            return res
    
    class PyToGd(PyToGd_Transformer):
        header_order = (
            "type",
            "script",
            "instance",
            "id",
        )
        def match(self, session, node):
            if (not isinstance(node,Resource)) or isinstance(node,Node):
                return False
            return not any([
                not (node.uid is None),
                not (node.file is None),
            ])
        def transform(self, session, node:Resource):
            if not (session.options["structure"].properties.get() is None):
                p : Promise = session.options["structure"].declare_subres(node)
                r : str = yield TRANSFORM(p)
                return r

            self.ensure_fmt(node)

            header = {
                "type" : node.gdtype if node.gdtype else "Resource",
                "script" : node.gdscript,
                "instance" : node.instance,
                "id" : node.name,
            }

            t = session.options["structure"].properties.set(True)
            txt_header = yield MACROS_PyToGd.dict_to_str(session,{k:v for k,v in header if (not(v is None))}, leading=" ")
            session.options["structure"].properties.reset(t)

            txt_properties = yield TRANSFORM(node.properties)

            if node.instance_editable:
                session.options["structure"].declare_editable.get()(node)

            return txt_header+"\n"+txt_properties

        def ensure_fmt(self,node:Resource):
            if node.id is None:
                node.id = "".join(ascii_letters, 9)

class _Properties():
    class PyToGd(PyToGd_Transformer):
        types = [Properties]
        def transform(self, session, node):
            t = session.option["structure"].properties.set(node)

            data = yield MACROS_GdToPy.pairs_to_dict(session, node.children)
            res = Properties(data)

            session.option["structure"].properties.reset(t) 
            return res

    class GdToPy(GdToPy_Transformer):
        keys = ["properties"]
        def transform(self, session, node:Properties):
            t = session.option["structure"].properties.set(node)

            res = yield MACROS_PyToGd.dict_to_str(session, node, entry_join="\n")

            session.option["structure"].properties.reset(t) 
            return res

gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    _GdSignal.GdToPy,
    _SubResource.GdToPy,
    _Properties.GdToPy,
    _ExtResource.GdToPy,
], 
options = {"structure":OPTIONS_GdToPy}
)

py_to_gd = PyToGd_TransformerSet("STD::structure.py", [
    _GdSignal.PyToGd,
    _SubResource.PyToGd,
    _Properties.PyToGd,
    # _ExtResource.GdToPy,
    _Promise.PyToGd,
], 
options = {"structure":OPTIONS_PyToGd} 
)