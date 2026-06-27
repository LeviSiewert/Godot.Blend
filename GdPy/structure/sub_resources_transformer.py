from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset
from .core.property_collection import PropertyCollection

from .sub_resources import (
    SubResourceExt,
    SubResourceEdit,
    SubResource,
    SubResourceNode,
    SubResourceCategory,
    ResourceContainer,
    GdObject,
)
from typing import Type

class _UNSET():pass

class _GdToPy(GdToPy):
    _res_cls : Type 
    def _transform(self, key, tc, gdc, header_properties:PropertyCollection, body_properties:PropertyCollection):
        inst = self._res_cls(_construct = True)
        for k,v in header_properties.items.items():
            assert(hasattr(inst, k))
            setattr(inst, k, v)
        inst.properties = body_properties
        return inst
class _PyToGd(PyToGd):
    _res_key : str

    def get_res_key(self, node)->str:
        return self._res_key
    def transform(self, node:SubResourceExt, tc, c, *args, **kwargs):
        ## Fetch, convert header properties
        _h_props = {}
        for k in self._header_props:
            v = getattr(node, k, None)
            if v is None:
                continue
            _h_props[k] = v 
        
        yield _h_props
        header_props = []
        for k,v in tc.children.get().items():
            header_props.append(f"{k}={v}") 

        ## Convert body properties
        yield {"props":node.properties}
        props = tc.children.get()["props"]

        return f"[{self.get_res_key()} {" ".join(header_props)}]" + "\n" + props
    
class GdToPy_SubResourceExt(_GdToPy):
    _keys = ("ext_resource",)
    _res_cls = SubResourceExt
class PyToGd_SubResourceExt(_PyToGd):
    _header_props = ('type', 'path', 'uid', 'id')
    _keys = (SubResourceExt,)
    _res_key = "ext_resource"

class GdToPy_SubResourceEdit(_GdToPy):
    _keys = ("edit_resource",)
    _res_cls = SubResourceEdit
class PyToGd_SubResourceEdit(_PyToGd):
    _header_props = ('type', 'path', 'uid', 'id')
    _keys = (SubResourceEdit,)
    _res_key = "editable"

class GdToPy_SubResource(_GdToPy):
    _keys = ("sub_resource",)
    _res_cls = SubResource
class PyToGd_SubResource(_PyToGd):
    _header_props = ('type', 'id')
    _keys = (SubResource,)
    _res_key = "sub_resource"

class GdToPy_SubResourceNode(_GdToPy):
    _keys = ("node_resource",)
    _res_cls = SubResourceNode
class PyToGd_SubResourceNode(_PyToGd):
    _header_props = ('name','type','node_paths','parent','unique_id','instance')
    _keys = (SubResourceNode,)
    _res_key = "node"

class GdToPy_SubResourceCategory(GdToPy):
    _keys = ("cat_resource",)
    def _transform(self, _key, tc, gdc, name:str, body_properties:PropertyCollection):
        inst = SubResourceCategory(_construct = True)
        inst.name = name
        inst.properties = body_properties
        return inst
class PyToGd_SubResourceCategory(_PyToGd):
    _keys = (SubResourceCategory,)
    _header_props = tuple()
    def get_res_key(self, node):
        return node.name 

class GdToPy_ResourceContainer(GdToPy):
    _keys = ("prim_resource",)
    _res_cls = ResourceContainer
    def _transform(self, _key, tc, gdc, body_properties:PropertyCollection):
        inst = SubResourceCategory(_construct = True)
        inst.properties = body_properties
        return inst
class PyToGd_ResourceContainer(_PyToGd):
    _header_props = tuple()
    _keys = (ResourceContainer,)
    _res_key = "resource"
    def transform(self, node:ResourceContainer, tc, c, *args, **kwargs):
        raise NotImplementedError("Not yet implimented!")


class GdToPy_GdObject(GdToPy):
    _keys = ("object",)
    def transform(self, node, tc, c, *args, **kwargs):
        raise NotImplementedError("Not yet implimented!")
class PyToGd_GdObject(PyToGd):
    _keys = (GdObject,)
    def transform(self, node:GdObject, tc, c, *args, **kwargs):
        yield node.properties.items
        props = []
        for k,v in tc.children.get():
            props.append(f"{k}:{v}")
        props = "{" + ",".join(props) + "}"
        return f"Object({node.gdtype} {props})"


gd_to_py_ruleset = GdToPyRuleset( __file__, (
    GdToPy_SubResourceExt,
    GdToPy_SubResourceEdit,
    GdToPy_SubResource,
    GdToPy_SubResourceNode,
    GdToPy_SubResourceCategory,
    GdToPy_ResourceContainer,
))
py_to_gd_ruleset = PyToGdRuleset( __file__, (
    PyToGd_SubResourceExt,
    PyToGd_SubResourceEdit,
    PyToGd_SubResource,
    PyToGd_SubResourceNode,
    PyToGd_SubResourceCategory,
    PyToGd_ResourceContainer,
))