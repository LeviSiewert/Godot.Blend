import bpy 

from ._transformer import (
    PyToBlContext, 
    PyToBlRuleset, 
    PyToBlModule, 
    BlToPyContext, 
    BlToPyRuleset,
    BlToPyModule,
)

from ...core.structure import (
    GdScene as BlGdScene,
    GdNode as BlGdNode,
)

from ....GdPy.core.nodes import(
    ResourceScene as PyResourceScene,
    Node as PyNode,
)

class PyToBl_Node(PyToBlModule):
    _keys = (PyNode,)
 
    def transform(self, c, node:PyNode):
        bl_node : bpy.types.Object = bpy.data.objects.new("Node", None)

        def apply_settings():
            gd : BlGdNode = bl_node.gd
            
            bl_node.name = node.name

            gd.name = node.name
            gd.unique_id = node.unique_id
            gd.type = node.type
            gd.script_type = node.script_type

            t = c.existing_object.set(gd.properties)
            yield (PyNode.properties,)
            c.existing_object.reset(t)

            return bl_node

        yield from apply_settings(bl_node)

        yield node.get_children()
        for _bl_child in c.children.get():
            _bl_child : bpy.types.Object
            _bl_child.parent = bl_node

        return bl_node

class BlToPy_Node(BlToPyModule):
    _keys = (bpy.types.Object,)

    def transform(self, c, node:bpy.types.Object):

        yield (node.gd.properties,)
        properties = c.children.get()[0]
        
        yield node.children
        children = c.children.get()

        return PyNode.construct(node.gd.name,
            unique_id = node.gd.unique_id,
            type = node.gd.type,
            script_type = node.gd.script_type,
            children=children,
            properties=properties,
        )


class PyToBl_ResourceScene(PyToBlModule):
    _keys = (PyResourceScene,)

class BlToPy_ResourceScene(BlToPyModule):
    _keys = (bpy.types.Collection,)


py_to_bl_ruleset = PyToBlRuleset("STD :: Nodes",(
    PyToBl_ResourceScene,
    PyToBl_Node,
))

bl_to_py_ruleset = BlToPyRuleset("STD :: Nodes",(
    BlToPy_ResourceScene,
    BlToPy_Node,
))