from ._transformer import GdToPyModule, PyToGdModule, GdToPyRuleset, PyToGdRuleset

from ...core.structure import Resource, Node, ExtResource, Properties


class GdToPy_Properties(GdToPyModule):
    _keys = ("properties",)

class PyToGd_Properties(GdToPyModule):
    _keys = (Properties,)

class GdToPy_Resource(GdToPyModule):
    #"[ ..." properties "]" ext_resources sub_resources [prim_resource]
    _keys = ("file_resource",)

    def transform(self, c, node): #->Resource:
        yield node.children
        children = c.children.get()

        header_properties = children[0]
        ext_resources = children[1]
        sub_resources = children[2]
        properties = children[3][0]

        return Resource(*header_properties, 
            ext_resources=ext_resources,
            sub_resources=sub_resources,
            properties=properties,
        )

class GdToPy_SubResource(GdToPyModule):
    _keys = ("resource",)

    def transform(self, c, node): #->Resource:
        yield node.children
        children = c.children.get()
        header_properties = children[0]
        properties = children[1]
        return Resource(*header_properties, properties=properties)

class PyToGd_Resource(PyToGdModule):
    _keys = (Resource,)

    def transform(self, c, node)->Resource:
        return super().transform(c, node)

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