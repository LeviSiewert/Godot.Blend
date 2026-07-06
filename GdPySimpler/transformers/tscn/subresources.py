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
from ...core.subresources import (
    ResourceTres, 
    SubResource,
    SubResourceRef,  
    SubResourceCollection,
)

from ...core.structure import (
    ResourceSettings, 
    Collection,
    Category,
    CategoryCollection,
    ExtResource,
    ExtResourceRef,
    ExtResourceCollection,
    GdType,
    GdTypeValueSet,
    RID,
    )


class GdToPy_ResourceTres(GdToPyModule):
    _keys = ("file_resource",)
    # def transform(self, c, node):
        
    #     header_props, ext_resources, sub_resources, prim_resource = node.children
        

    #     yield {
    #         "ext_resources" : ext_resources,
    #         "header_props" : header_props,
    #     }
        
    #     res = ResourceTres(
    #         **c.children.get()["header_props"],
    #     )
    #     apply(res,
    #         ext_resources = c.children.get()["ext_resources"],
    #     )

    #     t0 = c.resource.set(res)

    #     yield {
    #         "sub_resources" : sub_resources,
    #         "prim_resource" : prim_resource,
    #     }

    #     apply(res,
    #         sub_resources = c.children.get()["sub_resources"],
    #         prim_resource = c.children.get()["prim_resource"],
    #     )

    #     c.resource.reset(t0)
    #     return res


    
class PyToGd_ResourceTres(PyToGdModule):
    _keys = (ResourceTres,)




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
            "id": node.id,
            "type": node.type,
        }
        _header_props : dict = c.children.get()
        header_props = " ".join(f"{k}={v}" for k,v in _properties.items()) 

        return f"[node {header_props}]" + properties
    
class GdToPy_SubResourceRef(GdToPyModule):
    _keys = ("subresourceref",)
    def transform(self, c, node):
        yield node.children
        idname = c.children.get()[0]
        return SubResourceRef(**idname)

class PyToGd_SubResourceRef(PyToGdModule):
    _keys = (SubResourceRef,)
    def transform(self, c, node:SubResourceRef):
        ## TODO: ID VERIFICATION / FETCH!
        
        yield (node.cached_addr,)
        path = c.children.get()[0]
        assert not (path is None)
        return f'ExtResource({path})'

    
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