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

from ....GdPy.core.nodes import (
    Node as PyNode, 
    ResourceScene as PyResourceScene,
)

from ....GdPy.core.resources import (
    ExtResourceRef as PyExtResourceRef,
    ExtResource as PyExtResource,
)

_bl_node_subtypes = (
    bpy.types.Object,
    # bpy.types.Armature,
    # bpy.types.Curve,
    # bpy.types.Light,
    # bpy.types.LightProbe,
    # bpy.types.Camera,
) 

from typing import Generator, Any

def store_dependency(c:BlToPyContext, node:Any, defer_transform:bool=True, try_embed:bool=None, force_embed:bool=None, try_file:bool=None, force_file=None, override_uid:str=None, override_filepath:str=None)->tuple[PySubResourceRef|PyExtResourceRef, PySubResource|PyResource]:
    ''' Determine if subres OR extres is already created and resolved as required. 
    defer transform should resolve subres or extres 
    '''
    c.defered_dependencies.append()

def as_dependencies(c:BlToPyContext, *nodes, **kwargs)->Generator:
    file = c.resource.get()
    assert file
    for x in nodes:
        yield store_dependency(x, **kwargs)

def fetch_dependency():
    pass

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