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

from ...core.structure import PropertyCollection

def apply(inst, **kwargs):
    for k,v in kwargs.items():
        assert hasattr(inst, k)
        setattr(inst,k,v)
        if isinstance(v, PropertyCollection) and inst.overlay:
            v.overlay = v.overlay           
    return inst

## RESOURCES:

class GdToPy_ResourceSettings(GdToPyModule):
    _keys = ("file_settings",)
    def transform(self, c, node):
        properties, cat_resources = node.children.get()
    
        res = ResourceSettings()
        t0 = c.resource.set(res)
        yield {
            "properties" : properties,
            "cat_resources" : cat_resources,
        }

        apply(res,
            **c.children.get()
        )

        return res

class PyToGd_ResourceSettings(PyToGdModule):
    _keys = (ResourceSettings,)






class GdToPy_Category(GdToPyModule):
    _keys = ("cat_resource", "prim_resource")
    def transform(self, c, node):
        
        if c.key.get() == "prim_resource":
            _properties,_ = node.children
            name = "resource"
        else:
            name, _properties = node.children
        
        res = Category(name,)
        t0 = c.resource.set(res)

        yield _properties
        apply(res,
            name = name,
            properties = PropertyCollection(c.children.get()),
        )

        c.resource.reset(t0)
        return res

class PyToGd_Category(PyToGdModule):
    _keys = (Category,)




class GdToPy_ExtResource(GdToPyModule):
    _keys = ("ext_resource",)
    def transform(self, c, node):
        yield node.children
        properties = c.children.get()[0]
        return ExtResource(**properties)

class PyToGd_ExtResource(PyToGdModule):
    _keys = (ExtResource,)
    def transform(self, c, node:ExtResource):
        ## TODO: ID VERIFICATION / FETCH!

        yield {
                "type" : node.type.addr,
                "path" : node.path.addr,
                "uid" : node.uid.addr,
                "id" : node.id.addr,
            }
        d = c.children.get()
        assert not(d['type'] is None)
        assert not(d['path'] is None)
        assert not(d['uid'] is None)
        assert not(d['id'] is None)
        return f'[ext_resource type={d["type"]} uid={d["uid"]} path={d["path"]} id={d["id"]}]'



class GdToPy_ExtResourceRef(GdToPyModule):
    _keys = ("extresourceref",)
    def transform(self, c, node):
        yield node.children
        typing, idname = c.children.get()
        return ExtResourceRef(idname, typing = typing)

class PyToGd_ExtResourceRef(PyToGdModule):
    _keys = (ExtResourceRef,)
    def transform(self, c, node:ExtResourceRef):
        ## TODO: ID VERIFICATION / FETCH!
       
        yield (node.typing, node.id.addr)
        typing, path = c.children.get()
        assert not (path is None)
        if typing is None:
            return f'ExtResource({path})'
        return f'ExtResource({path})'



class GdToPy_RID(GdToPyModule):
    _keys = ("rid",)
    def transform(self, c, node):
        yield node.children
        typing, idname = c.children.get()
        return RID(idname, typing = typing)

class PyToGd_RID(PyToGdModule):
    _keys = (RID,)
    def transform(self, c, node:RID):
        ## TODO: ID VERIFICATION / FETCH!
        
        yield (node.typing, node.id.addr)
        typing, path = c.children.get()
        assert not (path is None)
        if typing is None:
            return f'RID({path})'
        return f'RID({path})'


class GdToPy_Collections(GdToPyModule):
    _keys = ('sub_resources','node_resources','cat_resources','ext_resources','edit_flags', 'signals')
    def transform(self, c, node):
        yield node.children
        match c.key.get():
            case 'sub_resources':
                return SubResourceCollection(*c.children.get())
            case 'node_resources':
                return NodeCollection(*c.children.get())
            case 'cat_resources':
                return CategoryCollection(*c.children.get())
            case 'ext_resources':
                return ExtResourceCollection(*c.children.get())
            case 'edit_flags':
                return EditFlagCollection(*c.children.get())
            case 'signals':
                return SignalNotationCollection(*c.children.get())
            case _:
                raise KeyError(c.key.get())

class PyToGd_Collections(PyToGdModule):
    _keys = (SubResourceCollection, NodeCollection, CategoryCollection, ExtResourceCollection, EditFlagCollection, SignalNotationCollection)
    def transform(self, c, node:Collection):
        yield (o for o,_ in node.data)
        return c.children.get()
        

class GdToPy_Properties(GdToPyModule):
    _keys = ('properties',)
    def transform(self, c, node):
        yield node.children
        res = PropertyCollection()
        if not (node.children == [None]):
            for k,v in c.children.get():
                res[k] = v
        return res 

class PyToGd_Properties(PyToGdModule):
    _keys = (PropertyCollection,)
    def transform(self, c, node:PropertyCollection):
        yield dict(node)
        res = []
        for k,v in c.children.get().items():
            res.append(f"{k} = {v}")
        return c.children.get()


class GdToPy_TypeAnno(GdToPyModule):
    _keys = ("type_anno",)
    def transform(self, c, node):
        yield node.children
        return GdTypeValueSet(*c.children.get())
class PyToGd_TypeAnno(PyToGdModule):
    _keys = (GdTypeValueSet,)

class GdToPy_TypeAnnoItem(GdToPyModule):
    _keys = ("type_anno_item",)
    def transform(self, c, node):
        yield node.children
        obj = c.children.get()[0]
        return obj

        ## TODO: Future w/ respect to references, files, and primitive types
        # if isinstance(obj, RID):
        #     pass
        # if isinstance(obj, String):
        #     pass
        # return c.project.get().typing.get(obj,default=obj)

class PyToGd_TypeAnnoItem(PyToGdModule):
    _keys = (GdType,)
    

# class _GdToPyRuleset(GdToPyRuleset):
#     def _match_module(self, keys, default):
#         raise Exception(keys, (*self.modules.keys(),))

gd_to_py_ruleset = GdToPyRuleset("STD_Structure", [
    GdToPy_ResourceSettings,
    GdToPy_RID,
    GdToPy_Category,
    GdToPy_ExtResource,
    GdToPy_ExtResourceRef,
    GdToPy_Collections,
    GdToPy_Properties,
    GdToPy_TypeAnno,
    GdToPy_TypeAnnoItem,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Structure", [
    PyToGd_ResourceSettings,
    PyToGd_RID,
    PyToGd_Category,
    PyToGd_ExtResource,
    PyToGd_ExtResourceRef,
    PyToGd_Collections,
    PyToGd_Properties,
    PyToGd_TypeAnno,
    PyToGd_TypeAnnoItem,
])