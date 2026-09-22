import bpy
from typing import Generator, Any

from ._transformer import (
    PyToBlContext, 
    PyToBlRuleset, 
    PyToBlModule, 
    BlToPyContext, 
    BlToPyRuleset,
    BlToPyModule,
)

from ...core.structure import (
    GdNode as BlGdNode, 
    ExtResource as BlExtResource
)

from ....GdPy.core.structure import (
    _Resource as Py_Resource
)

from ....GdPy.core.nodes import (
    Node as PyNode, 
    ResourceScene as PyResourceScene,
)

from ....GdPy.core.resources import (
    ResourceTres as PyResourceTres,
    SubResourceRef as PySubResourceRef,
    SubResource as PySubResource,
    ExtResourceRef as PyExtResourceRef,
    ExtResource as PyExtResource,
)

_bl_node_subtypes = (
    bpy.types.Object,
    # bpy.types.Material,
    # bpy.types.Mesh,
) 


class BlToPyRuleset_Objects(BlToPyRuleset):
    ''' Ruleset for extracting nodes from blender objects '''
    def _extract_keys(self, c, node):
        if not isinstance(node, _bl_node_subtypes):
            return None
        
        gd : BlGdNode = node.gd

        script_eid = gd.properties.get("script", default = None)
        ## Unloaded script ID, must fetch from contextual file.
        
        script_keys = [script_eid, ]
        
        if script_eid and (res := c.context.resource.get()):
            ext_res : BlExtResource |None= res.ext_resources.get(script_eid.val_str, None)
            if not (ext_res is None):
                script_keys.append(ext_res.uid)
                script_keys.append(ext_res.path)
                script_keys.append(ext_res.name)

        return filter(lambda x: not ((x is None) or (x == "")) , (
            gd.type,
            gd.script_name,
            *script_keys,
            *super()._extract_keys(node),
        ))
    
    def _match_module(self, keys, default=...):
        if keys is None: 
            return default
        return super()._match_module(keys, default)
    

class PyToBlRuleset_Objects(PyToBlRuleset):

    def _extract_keys(self, c, node):
        if not isinstance(node, PyNode):
            return None
        
        script_ref : PyExtResourceRef = node.properties.get("script", None)
        script_keys = []
        
        if script_ref:
            script_keys.append(script_ref.cached_addr)
            ext_res = script_ref.get()
            if not (ext_res is None):
                script_keys.append(ext_res.uid)
                script_keys.append(ext_res.path)
                script_keys.append(ext_res.name)

        return filter(lambda x: not ((x is None) or (x == "")) , (
            *script_keys,
            *super()._extract_keys(node),
        ))

        

    def _match_module(self, keys, default=...):
        if keys is None: 
            return default
        return super()._match_module(keys, default)
    
py_to_bl_ruleset = PyToBlRuleset_Objects("Nodes :: STD",(
    # PyToBl_ResourceScene,
    # PyToBl_Node,
))

bl_to_py_ruleset = BlToPyRuleset_Objects("Nodes :: STD",(
    # BlToPy_ResourceScene,
    # BlToPy_Node,
))