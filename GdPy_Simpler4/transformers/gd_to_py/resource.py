from ._transformer import GdToPyModule, PyToGdModule, GdToPyRuleset, PyToGdRuleset

from ...core.structure import Resource, Node, ExtResources


class GdToPy_Resource(GdToPyModule):
    _keys = ("file_resource","resource")

class PyToGd_Resource(PyToGdModule):
    _keys = (Resource,)


class GdToPy_ExtResource(GdToPyModule):
    _keys = ("ext_resource",)

class PyToGd_ExtResource(PyToGdModule):
    _keys = (ExtResources,)


class GdToPy_Node(GdToPyModule):
    _keys = ("file_node", "node")

class PyToGd_Node(PyToGdModule):
    _keys = (Node,)


gd_to_py_ruleset = GdToPyRuleset("STD_Resources", [
    GdToPy_Resource,
    GdToPy_Node,
    GdToPy_ExtResource,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Resources", [
    PyToGd_Resource,
    PyToGd_Node,
    PyToGd_ExtResource,
])