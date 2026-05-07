from __future__ import annotations
from .structure import GdTypeResourceFile, GdTypeResource
from .structure_values import *

### File Implimentation ###

class GdTypeResourceFileTres(GdTypeResourceFile):
    ''' Has properties, [resource] section header, and may have optional sub-resources '''
    _header_id       = "gd_resource"
    _header_contents = ["format", "uid"]
    type : str      ## base internal type.
    format : int    ## int denoting version
    uid : str       ## uid://

class GdTypeResourceFileTscn(GdTypeResourceFile):
    ''' May have properties and optional sub-resources '''
    _header_id       = "gd_scene"
    _header_contents = ["format", "uid"]

    format : int    ## int denoting version
    uid : str       ## uid://
    root : GdTypeSubResourceNode


### SubResources ###

class GdTypeSubResource(GdTypeResource):
    _header_id = "sub_resource"
    _header_contents = ["type", "id"]

class GdTypeSubResourceNode(GdTypeSubResource):
    _header_id = "node"
    _header_contents = ["name", "type", "parent", "id", "unique_id"]
    
    name : str
    type : str
    unique_id: int
    node_paths : list[str]
    parent : str
    
    _children : list[GdTypeSubResourceNode]

class GdTypeSubResourceExternal(GdTypeSubResource):
    _header_id = "ext_resource"
    _header_contents = []
    type : str
    uid : str
    path : str
    id : str

class GdTypeSubResourceEditable(GdTypeSubResource):
    _header_id = "editable"
    _header_contents = ["path"]
    path : str
