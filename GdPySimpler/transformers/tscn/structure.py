from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule

from ...core.structure import (
    Collection,
    ResourceSettings, 
    ResourceTres, 
    ResourceScene, 
    SubResource,
    SubResourceCollection, 
    Node,
    NodeCollection, 
    Category,
    CategoryCollection,
    ExtReference,
    ExtReferenceCollection,
    EditFlag,
    EditFlagCollection,
    GdType,
    GdTypeValueSet,
    Signal,
    SignalCollection
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



class GdToPy_ResourceTres(GdToPyModule):
    _keys = ("file_resource",)
    def transform(self, c, node):
        
        header_props, ext_references, sub_resources, prim_resource = node.children
        

        yield {
            "ext_references" : ext_references,
            "header_props" : header_props,
        }
        
        res = ResourceTres(
            **c.children.get()["header_props"],
        )
        apply(res,
            ext_references = c.children.get()["ext_references"],
        )

        t0 = c.resource.set(res)

        yield {
            "sub_resources" : sub_resources,
            "prim_resource" : prim_resource,
        }

        apply(res,
            sub_resources = c.children.get()["sub_resources"],
            prim_resource = c.children.get()["prim_resource"],
        )

        c.resource.reset(t0)
        return res


    
class PyToGd_ResourceTres(PyToGdModule):
    _keys = (ResourceTres,)



class GdToPy_ResourceScene(GdToPyModule):
    _keys = ("file_tscn",)
    def transform(self, c, node):
        header_props, ext_references, sub_resources, node_resources, edit_flags = node.children
        
        yield header_props

        res = ResourceScene(**c.children.get())
        t0 = c.resource.set(res)

        yield {
            # "properties":properties,
            "ext_references" : ext_references,
            "edit_flags" : edit_flags,
        }
        

        apply(res,
            edit_flags = c.children.get()["edit_flags"],
            ext_references = c.children.get()["ext_references"],
        )

        yield {
            "sub_resources":sub_resources,
            "node_resources":node_resources,
            "ResourceScene":ResourceScene,
        }

        apply(res,
            **c.children.get()
        )

        res.construct_node_tree()
        ## Nodes load deps as required, construction will load all instances

        c.resource.reset(t0)
    
        return res
    
class PyToGd_ResourceScene(PyToGdModule):
    _keys = (ResourceScene,)



## SUBRESOURCES:

class GdToPy_SubResource(GdToPyModule):
    _keys = ("sub_resource")
    def transform(self, c, node):
        _header_props, _properties = node.children
        
        yield _header_props
        header_props = c.children.get()

        _type = None
        if type_id := header_props.get("type",None):
            _type = c.project.get().typing.get(type_id, default=type_id)

        res = SubResource(
            owner=c.owner.get(),
            type = _type,
        )

        t0 = c.sub_resource.set(res)
        
        yield _properties
        
        apply(res,
            properties = PropertyCollection(c.children.get()),
        )

        c.sub_resource.reset(t0)
        return res       
    
class PyToGd_SubResource(PyToGdModule):
    _keys = (SubResource,)



class GdToPy_Node(GdToPyModule):
    _keys = ("node_resource")
    def transform(self, c, node):
        header_props, _properties = node.children

        yield header_props
        header : PropertyCollection = PropertyCollection(c.children.get())

        name = header["name"]
        path = header["parent"] + "/" + name

        instance = None
        instance_editable = False
        if inst_id := header.get("instance",None):
            instance = c.resource.get().ext_references.get(inst_id).file
            instance_editable = not (c.resource.get().edit_flags.get(path, None) is None)

        _type = None
        if type_id := header.get("type",None):
            _type = c.project.get().typing.get(type_id, default=type_id)

        res = Node(
            owner=c.resource.get(),
            name=name,
            type=_type,
            unique_id=header["unique_id"],
            instance=instance,
            instance_editable=instance_editable,
        )

        t0 = c.sub_resource.set(res)

        yield _properties
        
        apply(res,
            properties=PropertyCollection(c.children.get()),
        )

        c.sub_resource.reset(t0)
        
        return res

class PyToGd_Node(PyToGdModule):
    _keys = (Node,)


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

    

class GdToPy_ExtReference(GdToPyModule):
    _keys = ("ext_references",)
class PyToGd_ExtReference(PyToGdModule):
    _keys = (ExtReference,)


class GdToPy_EditFlag(GdToPyModule):
    _keys = ("edit_flag",)
class PyToGd_EditFlag(PyToGdModule):
    _keys = (EditFlag,)


class GdToPy_Signal(GdToPyModule):
    _keys = ("edit_flag",)
class PyToGd_Signal(PyToGdModule):
    _keys = (Signal,)



class PyToGd_Collections(GdToPyModule):
    _keys = ('sub_resources','node_resources','cat_resources','ext_references','edit_flags', 'signals')
    def transform(self, c, node):
        match c.key.get():
            case 'sub_resources':
                return SubResourceCollection(*c.children.get())
            case 'node_resources':
                return NodeCollection(*c.children.get())
            case 'cat_resources':
                return CategoryCollection(*c.children.get())
            case 'ext_references':
                return ExtReferenceCollection(*c.children.get())
            case 'edit_flags':
                return EditFlagCollection(*c.children.get())
            case 'signals':
                return SignalCollection(*c.children.get())

class GdToPy_Collections(PyToGdModule):
    _keys = (SubResourceCollection, NodeCollection, CategoryCollection, ExtReferenceCollection, EditFlagCollection, SignalCollection)
    def transform(self, c, node:Collection):
        yield (o for o,_ in node.data)
        return c.children.get()
        

class GdToPy_Properties(GdToPyModule):
    _keys = ('properties',)
    def transform(self, c, node):
        yield node.children
        res = PropertyCollection
        for k,v in c.children.get().items():
            PropertyCollection[k] = v
        return res 

class PyToGd_Properties(PyToGdModule):
    _keys = (PropertyCollection,)
    def transform(self, c, node:PropertyCollection):
        yield dict(node)
        res = []
        for k,v in c.children.get().items():
            res.append(f"{k} = {v}")
        return c.children.get()


class PyToGd_TypeAnno(PyToGdModule):
    _keys = ("type_anno",)
    def transform(self, c, node):
        yield node.children
        return GdTypeValueSet(*c.children.get())
class GdToPy_TypeAnno(GdToPyModule):
    _keys = (GdTypeValueSet,)

class PyToGd_TypeAnnoItem(PyToGdModule):
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

class GdToPy_TypeAnnoItem(GdToPyModule):
    _keys = (GdType,)
    


gd_to_py_ruleset = GdToPyRuleset(__file__, [

])

py_to_gd_ruleset = PyToGdRuleset(__file__, [

])