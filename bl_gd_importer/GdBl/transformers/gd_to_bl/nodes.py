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
)
BlScene : TypeAlias = bpy.types.Collection|Any
BlResource : TypeAlias = bpy.types.Collection|Any
BlNode : TypeAlias = bpy.types.Object|Any
BlSubResource : TypeAlias = bpy.types.Object|Any

class OPTIONS():
    class GdToBl(TransformerOptions):
        def __init__(self, session):
            self.resource = ContextVar(default=None)
            self.subresource = ContextVar(default=None)
            self.properties = ContextVar(default=None)
            self.declare_extres = ContextVar(default=self._declare_extres)
            self.declare_subres = ContextVar(default=self._declare_subres)

        resource : ContextVar[GdResource|GdNode|None]
        subresource : ContextVar[GdResource|GdNode|None]
        properties : ContextVar[GdProperties]

        declare_extres : ContextVar[Callable]
        declare_node : ContextVar[Callable]
        declare_subres : ContextVar[Callable]

        def _declare_rid(self, n:GdPromise|GdResource)->GdPromise|BlResource:
            return n
        def _declare_extres(self, n:GdPromise|GdResource)->GdPromise|BlResource:
            return n
        def _declare_subres(self, n:GdPromise|GdResource)->GdPromise|BlResource:
            return n

    class BlToGd(TransformerOptions):
        def __init__(self, session):
            self.resource = ContextVar(default=None)
            self.subresource = ContextVar(default=None)
            self.properties = ContextVar(default=None)
            self.declare_extres = ContextVar(default=self._declare_extres)
            self.declare_node = ContextVar(default=self._declare_node)
            self.declare_subres = ContextVar(default=self._declare_subres)

        resource : ContextVar[BlResource|BlNode|None]
        subresource : ContextVar[BlResource|BlNode|None]
        properties : ContextVar[BlProperties]

        declare_extres : ContextVar[Callable]
        declare_node : ContextVar[Callable]
        declare_subres : ContextVar[Callable]

        def _declare_rid(self, n:BlPromise|BlResource)->GdPromise|GdResource:
            return n
        def _declare_extres(self, n:BlPromise|BlResource)->GdPromise|GdResource:
            return n
        def _declare_subres(self, n:BlPromise|BlResource)->GdPromise|GdResource:
            return n
        
class _Properties():
    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return isinstance(node, GdProperties)

    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, BlProperties)

class _Resource():
    ''' Scene <-> Collection/OTHER. Primary resource stored as "root" node.
    Only req is that (gd.type == "RESOURCE") and a path/uid can be provided.
    This is to allow for arbitrary resources exporting.
    All imported resources are marked as assets w/ a tag of "uid://" and "path://"
    '''
    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return all ([
                isinstance(node, GdResource),
                (not (node.uid is None)) or (not (node.file is None))    
            ])

    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            gd = getattr(node, "gd", None)
            if (gd is None):
                return False
            return gd.type == "RESOURCE"

class _SubResource():
    ''' Generic Subresource, derivitives by type/script are in .subtypes && via modules #TODO 
    Defers to modules by being last in stack for import-export.
    ## TODO: Place a key on imported objects to prioritize this class on export if the key is used. 
    #   (python datastruct is more generic and stable, given priority over mutable blender modules for export then import) 
    '''
    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return all ([
                isinstance(node, GdResource),
                (node.uid is None),
                (node.file is None),    
            ])

    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            gd = getattr(node, "gd", None)
            if (gd is None):
                return False
            return gd.type == "SUBRESOURCE"


class _Scene():
    ''' Scene <-> Collection
        - Collection marked as asset, tags include UID 
        - Extres as Instance fr env
            - Missing nodes have paths recorded, notation in name matching blender's missing paths?
        - Signals attached to node.gd.signals
            - References nodes OR relative paths if missing depending on construction.
        - Edits require seperate caching file if collection not already present
            - Collections matched via Assets Tags ( Uid -> Path factoring in some project remap notes?? )
        - Subresources are sorted based on users?
            - Single users are made children of referencer
            - Multiple users are stored under root? or sub collection. TODO: Decide 
            - Could also be flat, no parents & hidden
    '''

    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return all ([
                isinstance(node, GdNode),
                (not (node.uid is None)) or (not (node.file is None))    
            ])

    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            gd = getattr(node, "gd", None)
            if (gd is None):
                return False
            return gd.type == "SCENE"


class _Node():
    ''' Generic Subresource, derivitives by type/script are in .nodes && via modules #TODO '''
    
    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return all ([
                isinstance(node, GdNode),
                (node.uid is None),
                (node.file is None),    
            ])
        
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            gd = getattr(node, "gd", None)
            if (gd is None):
                return False
            return gd.type == "NODE" 
            ## Default for <bpy.types.object>.gd
            ## Changed based on script & class type. 


bl_to_gd = BlToGdTransformerSet("bl_to_gd::nodes.py",
    transformers=[
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
        _Node.GdToBl,
        _Scene.GdToBl,
        _SubResource.GdToBl,
        _Resource.GdToBl,
    ],
    options={
        "node":OPTIONS.GdToBl
    }
)