import bpy

from ._transformers import GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet, TransformerOptions
from ....GdPy.core.transformer import TRANSFORM, TRANSFORM_CHILDREN, STEP

from contextvars import ContextVar
from typing import Any, Callable, TypeAlias, Generator
# from collections import OrderedDict

from ...structure import (
    Resource as BlResource,
    ResourceCollection as BlResource_Collection,
)
from ...properties import (
    Properties as BlProperties,
    Property_Base as _BlProperty,
    Property_Dict as BlDict,
    Property_Dict_Wrapped as BlDict_Wrapped,
    Property_Array as BlArray,
    Property_Array_Wrapped as BlArray_Wrapped,
    Property_Promise_Wrapped as BlPromise_Wrapped,
    Property_Promise as BlPromise,
    Property_Int as BlInt,
    Property_Float as BlFloat,
    Property_Vector as BlVector,
    Property_String as BlString,
    ReturnType
)

from ....GdPy.core.values import (
    Dictionary as GdDict,
    Array as GdArray,
)
from ....GdPy.core.structure import (
    Properties as GdProperties,
    Promise as GdPromise,
    Resource as GdResource,
    Node as GdNode,
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

from collections import OrderedDict

class UTILITIES():
    @staticmethod
    def iter_dict(val, *args, **kwargs):
        items = OrderedDict(val.items(*args, **kwargs))
        keys = yield TRANSFORM_CHILDREN((k for k,v in items), as_generator=True)
        vals = yield TRANSFORM_CHILDREN((v for k,v in items), as_generator=True)
        res = {}
        for k,v in zip(keys, vals):
            res[k]= v
        return res

class PropertyArray():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, BlArray)
        def transform(self, session, node:BlArray)->Generator[Any,Any,GdArray]:
            bl_properties = session.options["properties"].bl_properties.get()
            res = yield TRANSFORM_CHILDREN((bl_properties.bin_get(k.ptr) for k in node.data.values()), as_generator=True)
            typ = yield TRANSFORM(node.typing)
            return GdArray(*res, typing=typ)
                
    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return isinstance(node, GdArray)
        def transform(self, session, node)->Generator[Any,Any,str]:
            bl_properties : BlProperties = session.options["properties"].bl_properties.get()
            res = yield TRANSFORM_CHILDREN(node, as_generator=True)
            prop = bl_properties.bin_array.add()
            prop.name = bl_properties.bin_generate_pointer(bl_properties.bin_array)
            for k in res:
                e = prop.data.add()
                e.ptr = k
            prop.typing = yield TRANSFORM(node.typing)
            return prop.name

class PropertyDict():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, BlDict)
        def transform(self, session, node)->Generator[Any,Any,GdDict]:
            res = yield from UTILITIES.iter_dict(node, return_type=ReturnType.POINTER)
            typ = yield TRANSFORM(node.typing)
            return GdDict(res, typing=typ)

    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return isinstance(node, GdDict)
        def transform(self, session, node:GdDict)->Generator[Any,Any,str]:
            bl_properties : BlProperties = session.options["properties"].bl_properties.get()
            prop = bl_properties.bin_dict.data.add()
            prop.name = bl_properties.bin_generate_pointer(bl_properties.bin_dict)
            res = yield from UTILITIES.iter_dict(node, return_type=ReturnType.POINTER)
            prop.typing = yield TRANSFORM(node.typing)
            for k,v in res.items():
                e = prop.data.add()
                e.name = k
                e.ptr = v
            return prop.name


class PropertyPromise():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, (BlPromise, BlPromise_Wrapped))
        def transform(self, session, node):
            raise NotImplementedError()

    class GdToBl(GdToBlTransformer):
        def match(self, session, node):
            return isinstance(node, GdPromise)
        def transform(self, session, node):
            raise NotImplementedError()


class PropertyOther():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node):
            return isinstance(node, (BlInt, BlFloat, BlVector, BlString,))
        def transform(self, session, node:BlInt|BlFloat|BlVector|BlString):
            properties : BlProperties = session.options["properties"].properties.get()
            return node.export(properties=properties)
    class GdToBl(GdToBlTransformer):
        subtypes = tuple(int, float, *BlVector.subtypes.values(), str)
        def match(self, session, node):
            return isinstance(node, self.subtypes)
        def transform(self, session, node):
            properties : BlProperties = session.options["properties"].properties.get()
            return properties.bin_store(node, return_type=ReturnType.POINTER)

SUB_bl_to_gd = BlToGdTransformerSet("bl_to_gd::properties.py",
    transformers=[
        PropertyArray.BlToGd,
        PropertyDict.BlToGd,
        PropertyPromise.BlToGd,
        PropertyOther.BlToGd,
    ],
    options={
        "properties":OPTIONS_BlToGd,
    }
)


SUB_gd_to_bl = GdToBlTransformerSet("gd_to_gl::properties.py",
    transformers=[
        PropertyArray.GdToBl,
        PropertyDict.GdToBl,
        PropertyPromise.GdToBl,
        PropertyOther.GdToBl,
    ],
    options={
        "properties":OPTIONS_GdToBl,
    }
)


class Properties():
    class BlToGd(BlToGdTransformer):
        def match(self, session, node)->bool:
            return isinstance(node, BlProperties)
        def transform(self, session, node)->Generator[Any, Any, GdProperties]:#->GdProperties:
            t = session.transformer_sets.set(SUB_bl_to_gd)
            di = yield from UTILITIES.iter_dict(node, return_type=ReturnType.PROPERTY)
            session.transformer_sets.reset(t)
            return GdProperties(di)
        
    class GdToBl(GdToBlTransformer):
        def match(self, session, node)->bool:
            return isinstance(node, GdProperties)
        def transform(self, session, node)->Generator[Any,Any,BlProperties]:
            bl_properties : Properties = session.options["properties"].bl_properties.get()
            assert isinstance(bl_properties, BlProperties)

            t = session.transformer_sets.set(SUB_gd_to_bl)
            prop = bl_properties
            for k,v in node.items():
                e = prop.data.add()
                e.name = k
                e.ptr = yield TRANSFORM(v)

            session.transformer_sets.reset(t)
            return prop


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