from .core.transformer_v2 import TransformerModule, TransformerRuleset, TransformerContext, TERMINAL, IGNORE
from .core.lark_transformer import GdToPy, PyToGd, GdToPyRuleset, PyToGdRuleset
from .property_collection import PropertyCollection

from .sub_resources import (
    SubResourceExt,
    SubResourceEdit,
    SubResource,
    SubResourceNode,
    SubResourceCategory,
    ResourceContainer,
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
    _extra_space = False

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

        h_id = self.get_res_key(node)
        h_props = "" if not header_props else " "+" ".join(header_props)
        e_space = "" if not self._extra_space else "\n"
        body = "" if not props else "\n" + props

        return f"[{h_id}{h_props}]{e_space}{body}"

    
class GdToPy_SubResourceExt(_GdToPy):
    _keys = ("ext_resource",)
    _res_cls = SubResourceExt
class PyToGd_SubResourceExt(_PyToGd):
    _header_props = ('type', 'uid', 'path', 'id')
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
    _extra_space = True
    _keys = (SubResourceCategory,)
    _header_props = tuple()
    def get_res_key(self, node):
        return node.name 

class GdToPy_ResourceContainer(GdToPy):
    _keys = ("prim_resource",)
    _res_cls = ResourceContainer
    def _transform(self, _key, tc, gdc, body_properties:PropertyCollection):
        inst = ResourceContainer(_construct = True)
        inst.properties = body_properties
        return inst

class PyToGd_ResourceContainer(_PyToGd):
    _header_props = tuple()
    _keys = (ResourceContainer,)
    _res_key = "resource"


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