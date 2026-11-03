import bpy

from ._transformers import GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet, TransformerOptions
from ....GdPy.core.transformer import TRANSFORM, TRANSFORM_CHILDREN, STEP

from contextvars import ContextVar
from typing import Any, Callable, TypeAlias
# from collections import OrderedDict

from ...structure import (
    Resource as BlResource,
    ResourceCollection as BlResource_Collection,
)
from ...properties import (
    Properties as BlProperties,
    Property_Base as _BlProperty,
    Property_Dict as BlDict,
    Property_Array as BlArray,
    Property_Promise as BlPromise,
)

from ....GdPy.core.values import (
    Dictionary as GdDict,
    Array as GdArray,
)
from ....GdPy.core.structure import (
    Properties as GdProperties,
    Promise as GdPromise,
    Resource as GdResource,
    Scene as GdScene,
)

BlObject : TypeAlias = Any

class OPTIONS_GdToBl(TransformerOptions):
    def __init__(self):
        self.bl_properties = ContextVar("", default=None)
    bl_properties : ContextVar[BlProperties|None]

class OPTIONS_BlToGd(TransformerOptions):
    def __init__(self):
        self.bl_properties = ContextVar("", default=None)
    bl_properties : ContextVar[BlProperties|None]


class Properties():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node)->bool:
            return isinstance(node, BlProperties)
        def transform(self, session, node)->GdProperties:
            return
        
    class GdToBl(GdToBlTransformer):
        def match(self, session, node)->bool:
            return isinstance(node, GdProperties)
        def transform(self, session, node)->BlProperties:
            target = session.options["properties"].target.get()
            assert target
            return


bl_to_gd = BlToGdTransformerSet("bl_to_gd::properties.py",
    transformers=[
        Properties.BlToGd,
    ],
    options={
        "properties":OPTIONS_BlToGd,
    }
)

gd_to_bl = GdToBlTransformerSet("gd_to_gl::properties.py",
    transformers=[
        Properties.GdToBl,
    ],
    options={
        "properties":OPTIONS_GdToBl,
    }
)

# class UTILS_BlToGd():
#     @staticmethod
#     def iter_dict(val):
#         items = OrderedDict(val.items())
        
#         keys = yield TRANSFORM_CHILDREN((k for k,v in items), as_generator=True)
#         vals = yield TRANSFORM_CHILDREN((v for k,v in items), as_generator=True)

#         res = {}
#         for k,v in zip(keys, vals):
#             res[k]= v
#         return res

# class _PropsGeneric():
#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node)->bool:
#             return isinstance(node, (BlString, BlBinString, BlInt, BlFloat, BlVector, BlBinary))
#         def transform(self, session, node)->Any:
#             return node.value

# class _PropsArray():
#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             return isinstance(node, BlArrayWrapper)
#         def transform(self, session, node):
#             res = yield TRANSFORM_CHILDREN(node)
#             return GdArray(res, typing=node.typing)

# class _PropsDictionary():
#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             return isinstance(node, BlDictWrapper)
#         def transform(self, session, node):
#             res = yield from UTILS_BlToGd.iter_dict(node)
#             return GdDictionary(res, typing=node.typing)

# _BlToGdPropertiesSubSet = BlToGdTransformerSet("standard::Properties.py::subset", [
#     _PropsGeneric.BlToGd,
#     _PropsArray.BlToGd,
#     _PropsDictionary.BlToGd,
# ])

# class _Properties():
#     class GdToBl(GdToBlTransformer):
#         def match(self, session, node):
#             return isinstance(node, GdProperties)
#         def transform(self, session, node):
#             t0 = session.options["structure"].properties.set(node)
            
#             properties : BlProperties = session.options["structure"].existing_properties.get()
#             properties.update(node)

#             session.options["structure"].properties.reset(t0)
#             return properties
        
#     class BlToGd(BlToGdTransformer):
#         def match(self, session, node):
#             return isinstance(node, BlProperties)
        
#         def transform(self, session, node):
#             t0 = session.options["structure"].properties.set(node)
#             t1 = session.transformer_sets.set([_BlToGdPropertiesSubSet])

#             base : dict = yield from UTILS_BlToGd.iter_dict(node)

#             properties = GdProperties(base)

#             session.transformer_sets.reset(t1)
#             session.options["structure"].properties.reset(t0)

#             return properties

