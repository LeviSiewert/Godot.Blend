from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule

from ...core.nodes import (
    ResourceScene, 
    Node,
    NodeCollection, 
    EditFlag,
    EditFlagCollection,
    SignalNotation,
    SignalNotationCollection,
)
from ...core.resources import (
    ResourceTres, 
    SubResource,
    SubResourceRef,  
    SubResourceCollection,
)

from ...core.structure import (
    Collection,
    ExtResource,
    ExtResourceRef,
    ExtResourceCollection,
    GdType,
    GdTypeValueSet,
    RID,
)

from ...core.settings import (
    ResourceSettings, 
    Category,
    CategoryCollection,
)


class GdToPy_ResourceTres(GdToPyModule):
    _keys = ("file_resource",)
        
    def transform(self, c, node):
        header_props, ext_resources, sub_resources, prim_resource = node.children
        
        yield (header_props,)

        res = ResourceTres.construct( **c.children.get()[0] )
        t0 = c.resource.set(res)
        
        yield {        
            "ext_resources" : ext_resources,
            "sub_resources" : sub_resources,
        }
        d = c.children.get()

        if prim_resource:
            yield dict(prim_resource)
            d["prim_resource"] = c.children.get()
        
        if r:=d.get("ext_resources", None):
            res.ext_resources.extend(r)
        if r:=d.get("sub_resources", None):
            res.sub_resources.extend(r)
        if r:=d.get("prim_resource", None):
            res.properties.update(r)
        

        c.resource.reset(t0)
        return res

    
class PyToGd_ResourceTres(PyToGdModule):
    _keys = (ResourceTres,)

    def transform(self, c, node):
        yield dict(node.properties)
        _properties : dict[str,str] = c.children.get()
        properties = "\n".join(f"{k} = {v}" for k,v in _properties.items())

        _header_props = {
            "type": node.type,
            "format": node.format,
            "uid": node.uid.addr,
        }
        # if node.instance:
        #     _header_props["instance"] = node.instance.addr

        _header_props : dict = c.children.get()
        header_props = " ".join(f"{k}={v}" for k,v in _properties.items()) 

        return f"[node {header_props}]" + properties


## SUBRESOURCES:

class GdToPy_SubResource(GdToPyModule):
    _keys = ("sub_resource",)
    def transform(self, c, node):
        header_props, _properties = node.children

        yield header_props.children
        header = dict(c.children.get())


        res = SubResource.construct(
            **header,
            # properties=dict(properties),
            _defered_apply_owner = True
        )
        
        t0 = c.sub_resource.set(res)
    
        yield (_properties,)
        properties = c.children.get()[0]
        res.properties.update(properties)
    
        c.sub_resource.reset(t0)

        return res       
    
class PyToGd_SubResource(PyToGdModule):
    _keys = (SubResource,)
    
    def transform(self, c, node:SubResource):
        yield dict(node.properties)
        _properties : dict[str,str] = c.children.get()
        properties = "\n".join(f"{k} = {v}" for k,v in _properties.items())
        
        _header_props = {
            "type": node.type,
            "id": node.id.addr,
        }
        yield _header_props
        _header_props : dict = c.children.get()
        header_props = " ".join(f"{k}={v}" for k,v in _header_props.items() if not (v is None)) 

        return f"[sub_resource {header_props}]\n" + properties
    
class GdToPy_SubResourceRef(GdToPyModule):
    _keys = ("subresourceref",)
    def transform(self, c, node):
        yield node.children
        typing, idname = c.children.get()
        return ExtResourceRef(idname, typing = typing)
    
class PyToGd_SubResourceRef(PyToGdModule):
    _keys = (SubResourceRef,)
    def transform(self, c, node:SubResourceRef):
        ## TODO: ID VERIFICATION / FETCH!
       
        yield (node.typing, node.cached_addr)
        typing, path = c.children.get()
        assert not (path is None)
        if typing is None:
            return f'SubResource({path})'
        return f'SubResource({path})'

    
gd_to_py_ruleset = GdToPyRuleset("STD_Nodes", [
    GdToPy_ResourceTres,
    GdToPy_SubResource,
    GdToPy_SubResourceRef,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Nodes", [
    PyToGd_ResourceTres,
    PyToGd_SubResource,
    PyToGd_SubResourceRef,
])