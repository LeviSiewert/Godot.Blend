from ._transformer import GdToPyModule, PyToGdModule, GdToPyRuleset, PyToGdRuleset

from ...core.structure import Resource, Node, ExtResource, Properties


class GdToPy_Properties(GdToPyModule):
    _keys = ("properties",)

    def transform(self, c, node):
        yield node.children
        return dict(c.children.get())

class PyToGd_Properties(GdToPyModule):
    _keys = (Properties,)

    def transform(self, c, node):
        yield dict(node)
        return "\n".join(f"{k}={v}" for k,v in c.children.get().items())


class GdToPy_Resource(GdToPyModule):
    #"[ ..." properties "]" ext_resources sub_resources [prim_resource]
    _keys = ("file_resource",)

    def transform(self, c, node): #->Resource:
        yield node.children
        header_properties, ext_resources, sub_resources, properties = c.children.get()

        # raise Exception(header_properties)

        return Resource(**header_properties, 
            ext_resources=ext_resources,
            sub_resources=sub_resources,
            properties=properties,
        )

class GdToPy_SubResource(GdToPyModule):
    _keys = ("sub_resource",)

    def transform(self, c, node): #->Resource:
        yield node.children
        children = c.children.get()
        header_properties = children[0]
        properties = children[1]
        return Resource(*header_properties, properties=properties)

class PyToGd_Resource(PyToGdModule):
    _keys = (Resource,)

    def transform(self, c, node:Resource):
        if node.is_subresource():
            res = yield from self.transform_subresource(c, node)
        else:
            res = yield from self.transform_resource(c, node)
        return res
    
    def transform_subresource(self, c, node:Resource):
        yield {
            "id" : node.id.key,
            "properties" : node.properties,
            "type" : node.gdtype if node.gdtype else "Resource"
        }
        d = c.children.get()

        header_props = f" type={d["type"]} id={d["id"]}"

        if isinstance(node.instance, Resource):
            header_props = header_props + f" instance={node.instance.uid.key}"
        elif isinstance(node.instance, str):
            header_props = header_props + f" instance={node.instance}"

        return (
            f"[sub_resource{header_props}]" 
            + d["properties"] 
            + "\n"
        )

    def transform_resource(self, c, node:Resource):
        yield {
            # "id" : node.id.key,
            "uid" : node.uid.key,
            "properties" : node.properties,
            "type" : node.gdtype if node.gdtype else "Resource",
            "ext_resources" : node.ext_resources.values(use_overlay=False),
            "sub_resources" : node.sub_resources.values(use_overlay=False),
        }

        header_props = f" type={d["type"]} uid={d["uid"]}"

        if isinstance(node.instance, Resource):
            header_props = header_props + f" instance={node.instance.uid.key}"
        elif isinstance(node.instance, str):
            header_props = header_props + f" instance={node.instance}"
        
        d = c.children.get()
        if len(d["properties"]) > 0:
            return (
                f"[gd_resource{header_props}]" 
                + d["ext_resource"] 
                + d["sub_resource"] 
                + f"[Resource]\n" 
                + d["properties"] 
                + "\n")
        return (
            f"[gd_resource{header_props}]" 
            + d["ext_resource"] 
            + d["sub_resource"] 
        )

class GdToPy_ExtResource(GdToPyModule):
    _keys = ("ext_resource",)

class PyToGd_ExtResource(PyToGdModule):
    _keys = (ExtResource,)


class GdToPy_Node(GdToPyModule):
    _keys = ("file_node", "node")

class PyToGd_Node(PyToGdModule):
    _keys = (Node,)


gd_to_py_ruleset = GdToPyRuleset("STD_Resources", *[
    GdToPy_Resource,
    GdToPy_SubResource,
    GdToPy_Node,
    GdToPy_ExtResource,
    GdToPy_Properties,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Resources", *[
    PyToGd_Resource,
    # PyToGd_SubResource,
    PyToGd_Node,
    PyToGd_ExtResource,
    PyToGd_Properties,
])