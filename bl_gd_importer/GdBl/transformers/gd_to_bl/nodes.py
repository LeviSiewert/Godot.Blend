from ._transformers import GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet, TransformerOptions

import bpy

from contextvars import ContextVar
from typing import Any, Callable, TypeAlias


from ....GdPy.core.structure import (
    Resource as GdResource, 
    Node as GdNode, 
    Properties as GdProperties, 
    Promise as GdPromise,
)
from ...structure import (
    Properties as BlProperties,
    Promise as BlPromise,
    Resource as BlResource,
    ResourceCollection as BlResourceCollection,
)

BlObject : TypeAlias = Any

class OPTIONS():
    class BlToGd(TransformerOptions):
        def __init__(self, session):
            self.resource = ContextVar(default=None)
            self.subresource = ContextVar(default=None)
            self.properties = ContextVar(default=None)
        resource : ContextVar[BlObject|None]
        subresource : ContextVar[BlObject|None]
        properties : ContextVar[BlProperties|None]
        def declare_node(self, obj:BlObject)->GdPromise:
            pass
        def declare_subresource(self, obj:BlObject|BlPromise)->GdPromise:
            pass
        def declare_extresource(self, obj:BlObject|BlPromise)->GdPromise:
            pass
        
    class GdToBL(TransformerOptions):
        def __init__(self, session):
            self.resource = ContextVar(default=None)
            self.subresource = ContextVar(default=None)
            self.properties = ContextVar(default=None)
        resource : ContextVar[GdResource|None]
        subresource : ContextVar[GdResource|None]
        properties : ContextVar[GdProperties|None]

        target_properties : ContextVar[BlProperties|None] #Target for alteration, required due to auto creation.
        
        def declare_node(self, obj:GdNode)->BlObject:
            pass
        def declare_subresource(self, obj:GdResource|GdPromise)->BlObject:
            pass
        def declare_extresource(self, obj:GdNode|GdResource|GdPromise)->BlObject:
            pass

class _Promise():
    class GdToBl(GdToBlTransformer):...
    class BlToGd(BlToGdTransformer):...

class _Resource():
    class GdToBl(GdToBlTransformer):...
    class BlToGd(BlToGdTransformer):...

class _SubResource():
    class GdToBl(GdToBlTransformer):...
    class BlToGd(BlToGdTransformer):...

class _Node():
    class GdToBl(GdToBlTransformer):...
    class BlToGd(BlToGdTransformer):...

class _Scene():
    class GdToBl(GdToBlTransformer):...
    class BlToGd(BlToGdTransformer):...


# class _Resource():
#     ''' Scene <-> Collection/OTHER. Primary resource stored as "root" node.
#     Only req is that (gd.type == "RESOURCE") and a path/uid can be provided.
#     This is to allow for arbitrary resources exporting.
#     All imported resources are marked as assets w/ a tag of "uid://" and "path://"
#     '''
#     class GdToBl(GdToBlTransformer):
#         def match(self, session, node):
#             return all ([
#                 isinstance(node, GdResource),
#                 (not (node.uid is None)) or (not (node.file is None))    
#             ])

#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             gd = getattr(node, "gd", None)
#             if (gd is None):
#                 return False
#             return gd.type == "RESOURCE"

# class _SubResource():
#     ''' Generic Subresource, derivitives by type/script are in .subtypes && via modules #TODO 
#     Defers to modules by being last in stack for import-export.
#     ## TODO: Place a key on imported objects to prioritize this class on export if the key is used. 
#     #   (python datastruct is more generic and stable, given priority over mutable blender modules for export then import) 
#     '''
#     class GdToBl(GdToBlTransformer):
#         def match(self, session, node):
#             return all ([
#                 isinstance(node, GdResource),
#                 (node.uid is None),
#                 (node.file is None),    
#             ])

#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             gd = getattr(node, "gd", None)
#             if (gd is None):
#                 return False
#             return gd.type == "SUBRESOURCE"


# class _Scene():
#     ''' Scene <-> Collection
#         - Collection marked as asset, tags include UID 
#         - Extres as Instance fr env
#             - Missing nodes have paths recorded, notation in name matching blender's missing paths?
#         - Signals attached to node.gd.signals
#             - References nodes OR relative paths if missing depending on construction.
#         - Edits require seperate caching file if collection not already present
#             - Collections matched via Assets Tags ( Uid -> Path factoring in some project remap notes?? )
#         - Subresources are sorted based on users?
#             - Single users are made children of referencer
#             - Multiple users are stored under root? or sub collection. TODO: Decide 
#             - Could also be flat, no parents & hidden
#     '''

#     class GdToBl(GdToBlTransformer):
#         def match(self, session, node):
#             return all ([
#                 isinstance(node, GdNode),
#                 (not (node.uid is None)) or (not (node.file is None))    
#             ])

#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             gd = getattr(node, "gd", None)
#             if (gd is None):
#                 return False
#             return gd.type == "SCENE"


# class _Node():
#     ''' Generic Subresource, derivitives by type/script are in .nodes && via modules #TODO '''
    
#     class GdToBl(GdToBlTransformer):
#         def match(self, session, node):
#             return all ([
#                 isinstance(node, GdNode),
#                 (node.uid is None),
#                 (node.file is None),    
#             ])
        
#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             gd = getattr(node, "gd", None)
#             if (gd is None):
#                 return False
#             return gd.type == "NODE" 
#             ## Default for <bpy.types.object>.gd
#             ## Changed based on script & class type. 


bl_to_gd = BlToGdTransformerSet("bl_to_gd::nodes.py",
    transformers=[
        _Promise.BlToGd,
        _Node.BlToGd,
        _Scene.BlToGd,
        _SubResource.BlToGd,
        _Resource.BlToGd,
    ],
    options={
        "node":OPTIONS.BlToGd
    }
)

gd_to_bl = GdToBlTransformerSet("gd_to_gl::nodes.py",
    transformers=[
        _Promise.GdToBl,
        _Node.GdToBl,
        _Scene.GdToBl,
        _SubResource.GdToBl,
        _Resource.GdToBl,
    ],
    options={
        "node":OPTIONS.GdToBl
    }
)