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
    GdNode as BlGdNode, 
    ExtResource as BlExtResource
)

_bl_node_subtypes = (
    bpy.types.Object,
    # bpy.types.Armature,
    # bpy.types.Curve,
    # bpy.types.Light,
    # bpy.types.LightProbe,
    # bpy.types.Camera,
) 

class BlToPyRuleset_Objects(BlToPyRuleset):
    ''' Ruleset for extracting nodes from blender objects '''
    def _extract_keys(self, node):
        if not isinstance(node, _bl_node_subtypes):
            return None
        
        gd : BlGdNode = node.gd

        script_eid = gd.properties.get("script", default = None)
        
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

    def _extract_keys(self, node):

        return super()._extract_keys(node)
