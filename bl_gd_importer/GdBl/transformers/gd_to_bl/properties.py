from ._transformers import GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet, TransformerOptions
from ....GdPy.core.transformer import TRANSFORM, TRANSFORM_CHILDREN, STEP

import bpy

from contextvars import ContextVar
from typing import Any, Callable, TypeAlias
from collections import OrderedDict

from ....GdPy.core.structure import (
    Resource as GdResource, 
    Node as GdNode, 
    Properties as GdProperties, 
    Promise as GdPromise,
)

from ...structure import (
    Promise as BlPromise,
    Resource as BlResource,
    ResourceCollection as BlResourceCollection,
)

BlObject : TypeAlias = Any

from ....GdPy.core.values import (
    Array as GdArray,
    Dictionary as GdDictionary,
    NodePath as GdNodePath,
    _FixedLenArray as GdFixedLenArray,
    _PackedListSimple as GdPackedListSimple,
    _PackedListComplex as GdPackedListComplex,
    StringName as GdStringName,
    Object as GdObject,
    Vector2i as GdVector2i,
    Vector3i as GdVector3i,
    Vector4i as GdVector4i,
    Rect2i as GdRect2i,
    Vector2 as GdVector2,
    Vector3 as GdVector3,
    Vector4 as GdVector4,
    Rect2 as GdRect2,
    Plane as GdPlane,
    Color as GdColor,
    AABB as GdAABB,
    Quaternion as GdQuaternion,
    Transform2D as GdTransform2D,
    Transform3D as GdTransform3D,
    Basis as GdBasis,
    PackedByteArray as GdPackedByteArray,
)

from ...properties import (
    Properties as BlProperties,
    PropertyBin as BlBin,
    Property as BlProperty,
    PropertyPromise as BlPromise,

    PropertyDictItem as BlDictItem,
    PropertyDictItemWrapper as BlDictItemWrapper,
    PropertyDict as BlDict,
    PropertyDictWrapper as BlDictWrapper,

    PropertyArrayItem as BlArrayItem,
    PropertyArrayItemWrapper as BlArrayItemWrapper,
    PropertyArray as BlArray,
    PropertyArrayWrapper as BlArrayWrapper,

    PropertyString as BlString,
    PropertyBinString as BlBinString,
    PropertyInt as BlInt,
    PropertyFloat as BlFloat,
    PropertyVector as BlVector,

    PropertyBinary as BlBinary,
)

class UTILS_BlToGd():
    @staticmethod
    def iter_dict(val):
        items = OrderedDict(val.items())
        
        keys = yield TRANSFORM_CHILDREN((k for k,v in items), as_generator=True)
        vals = yield TRANSFORM_CHILDREN((v for k,v in items), as_generator=True)

        res = {}
        for k,v in zip(keys, vals):
            res[k]= v
        return res

class _PropsGeneric():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node)->bool:
            return isinstance(node, (BlString, BlBinString, BlInt, BlFloat, BlVector, BlBinary))
        def transform(self, session, node)->Any:
            return node.value

class _PropsArray():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, BlArrayWrapper)
        def transform(self, session, node):
            res = yield TRANSFORM_CHILDREN(node)
            return GdArray(res, typing=node.typing)

class _PropsDictionary():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, BlDictWrapper)
        def transform(self, session, node):
            res = yield from UTILS_BlToGd.iter_dict(node)
            return GdDictionary(res, typing=node.typing)

_BlToGdPropertiesSubSet = BlToGdTransformerSet("standard::Properties.py::subset", [
    _PropsGeneric.BlToGd,
    _PropsArray.BlToGd,
    _PropsDictionary.BlToGd,
])

class _Properties():
    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return isinstance(node, GdProperties)
        def transform(self, session, node):
            t0 = session.options["structure"].properties.set(node)
            
            properties : BlProperties = session.options["structure"].existing_properties.get()
            properties.update(node)

            session.options["structure"].properties.reset(t0)
            return properties
        
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, BlProperties)
        
        def transform(self, session, node):
            t0 = session.options["structure"].properties.set(node)
            t1 = session.transformer_sets.set([_BlToGdPropertiesSubSet])

            base : dict = yield from UTILS_BlToGd.iter_dict(node)

            properties = GdProperties(base)

            session.transformer_sets.reset(t1)
            session.options["structure"].properties.reset(t0)

            return properties

bl_to_gd = BlToGdTransformerSet("bl_to_gd::nodes.py",
    transformers=[
        _Properties.BlToGd,
    ]
)

gd_to_bl = GdToBlTransformerSet("gd_to_gl::nodes.py",
    transformers=[
        _Properties.GdToBl,
   ]
)