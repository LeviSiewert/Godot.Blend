from __future__ import annotations

from .sub_resources import SubResourceNode
from pygltflib import (
    Node as GltfNode,
)

class ZipNode[L:SubResourceNode, R:GltfNode]():
    ''' Utility class for IO of transformers ''' 
    ## FUTURE: allowences for dif/overlap of properties?? 
    # # # must conform to broad use cases.
    # # # Consider next as overlay series for each node being imported/exported
    
    tscn_node : L|None
    gltf_node : R|None
    children : list[ZipNode]

    def __init__(self, tscn_node:L=None, gltf_Node:R=None, children:list[ZipNode]=None):
        self.tscn_node=tscn_node
        self.gltf_Node=gltf_Node
        if children is None:
            self.children = []
        else: 
            self.children = children 

class GltfFileWrapper():
    ''' Wrapper to attach and track blender objects to GLTF binaries/external files '''

    def __init__(self, gltf):
        pass 
