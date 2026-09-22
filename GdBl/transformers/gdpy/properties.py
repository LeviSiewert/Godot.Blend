from contextvars import ContextVar

from ._transformer import (
    GdToBl_Transformer, 
    GdToBl_TransformerSet, 
    GdToBl_TransformerOptions, 
    BlToGd_Transformer, 
    BlToGd_TransformerSet, 
    BlToGd_TransformerOptions, 
    TRANSFORM_CHILDREN,
    TRANSFORM,
)

from ....GdPy.core.structure import (
    Properties as PyProperties,
    Promise as PyPromise,
    Node as PyNode,
    Resource as PyResource,
)

from ....GdPy.core.values import (
    NodePath as PyNodePath,
    StringName as PyStringName,
    Object as PyObject,
    Dictionary as PyDictionary,
    Array as PyArray,
    Vector2i as PyVector2i,
    Vector3i as PyVector3i,
    Vector4i as PyVector4i,
    Rect2i as PyRect2i,
    Vector2 as PyVector2,
    Vector3 as PyVector3,
    Vector4 as PyVector4,
    Rect2 as PyRect2,
    Plane as PyPlane,
    Color as PyColor,
    AABB as PyAABB,
    Quaternion as PyQuaternion,
    Transform2D as PyTransform2D,
    Transform3D as PyTransform3D,
    Basis as PyBasis,
    PackedInt32Array as PyPackedInt32Array,
    PackedInt64Array as PyPackedInt64Array,
    PackedFloat32Array as PyPackedFloat32Array,
    PackedFloat64Array as PyPackedFloat64Array,
    PackedStringArray as PyPackedStringArray,
    PackedVector2Array as PyPackedVector2Array,
    PackedVector3Array as PyPackedVector3Array,
    PackedVector4Array as PyPackedVector4Array,
    PackedColorArray as PyPackedColorArray,
    PackedByteArray as PyPackedByteArray,
)

from ...core.property_collection import (
    GdDictionary as BlGdDictionary,
    GdArray as BlGdArray,
    GdPrimitive as BlGdPrimitive,
    GdVector as BlGdVector,
    GdReference as BlGdReference,
    GdPropertyCollection as BlGdPropertyCollection,
)

from ...core.primitives.pointer_collection import (
    BlPointerDictionaryWrapper as BlDictionaryWrapper,
    BlPointerArrayWrapper as BlArrayWrapper,
    BlPointerDictionaryItemWrapper as BlDictionaryItemWrapper,
    BlPointerArrayItemWrapper as BlArrayItemWrapper,
)


## OPTIONS ##

class GdToBl_Options(GdToBl_TransformerOptions):
    use_bl_property_structure : ContextVar[bool] = False
    bl_property_structure : ContextVar[BlGdPropertyCollection]
    def __init__(self, session):
        self.use_bl_property_structure = ContextVar("", default = False)
        self.bl_property_structure = ContextVar("")

class BlToGd_Options(BlToGd_TransformerOptions):
    use_bl_property_structure : ContextVar[bool] = False
    bl_property_structure : ContextVar[BlGdPropertyCollection] = False
    def __init__(self, session):
        self.use_bl_property_structure = ContextVar("", default = False)
        self.bl_property_structure = ContextVar("")


## TYPES ## 

### SIMPLE ### 
class GdToBl_Primitive(GdToBl_Transformer):
    _keys = (PyNodePath, PyStringName, str, int, float, bool, None)
    contextual = False
    memoized = False
    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()
        obj, ptr = propcol.store_value(val=node, bin_id="bin_primitive")
        return ptr
    
class BlToGd_Primitive(BlToGd_Transformer):
    _keys = (BlGdPrimitive,)
    _subtype_map = {"NodePath": PyNodePath, "StringName" : PyStringName}
    contextual = False
    memoized = False
    def transform(self, c, node:BlGdPrimitive):
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value)
        return node.value

class GdToBl_Vector(GdToBl_Transformer):
    _keys = (PyVector2, PyVector3, PyVector4, PyRect2, PyPlane, PyColor, PyAABB, PyQuaternion, PyBasis, PyTransform2D, PyTransform3D, PyVector2i, PyVector3i,PyVector4i, PyRect2i)
    contextual = False
    memoized = False
    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()
        obj, ptr = propcol.store_value(val=node, bin_id="bin_vector")
        return ptr

class BlToGd_Vector(BlToGd_Transformer):
    _keys = (BlGdVector,)
    _subtype_map = {x.__class__.__name__:x for x in GdToBl_Vector._keys}
    contextual = False
    memoized = False
    def transform(self, session, node):
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value)
        return node.value

## COMPLEX ## 

class Macros:
    @staticmethod
    def transform_kv_generator(gen:Generator)->dict:
        res = {}
        for k,v in gen:
            _k,_v = yield TRANSFORM_CHILDREN(gen) 
            res[_k] = v
        return res

class GdToBl_Dictionary(GdToBl_Transformer):
    _keys = (dict, PyDictionary, PyObject,)
    contextual = False
    memoized = False

    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()

        obj, ptr = propcol.store_value(bin_id="bin_dict", wrap=True)
        obj : BlDictionaryWrapper
        children = yield from Macros.transform_kv_generator(obj.items())
        ## All GdToBl_Properties::Transformers return pointers to the local value

        for k,v in children.items():
            e = obj.items.new()
            e.val_ptr = k
            e.key_ptr = v

        if isinstance(obj, PyObject):
            obj.objtype = node.type
        else:             
            obj.typing = yield TRANSFORM(node.typing)
            
        return ptr

class BlToGd_Dictionary(BlToGd_Transformer):
    _keys = (BlDictionaryWrapper)
    contextual = False
    memoized = False


    
class GdToBl_Array(GdToBl_Transformer):
    _keys = (PyArray, PyPackedInt32Array, PyPackedInt64Array, PyPackedFloat32Array, PyPackedFloat64Array, PyPackedStringArray, PyPackedVector2Array, PyPackedVector3Array, PyPackedVector4Array, PyPackedColorArray, PyPackedByteArray, )
    contextual = False
    memoized = False
class BlToGd_Array(BlToGd_Transformer):
    _keys = (BlArrayWrapper, )
    contextual = False
    memoized = False


## OBJECT REFS ##

class GdToBl_Reference(GdToBl_Transformer):
    _keys = (PyPromise,)
    contextual = False
    memoized = False
    def match(self, session, node):
        return any([
            isinstance(node, self._keys),
            isinstance(node, PyResource) and (not (node.uid is None)),
        ])
    def transform(self, session, node):
        return super().transform(session, node)

class BlToGd_Reference(BlToGd_Transformer):
    _keys = (BlGdReference,)
    _subtype_map = {x.__class__.__name__:x for x in GdToBl_Reference._keys}
    contextual = False
    memoized = False
    def transform(self, session, node):
        return super().transform(session, node)


## BODY ## 

class GdToBl_PropertyCollection(GdToBl_Transformer):
    _keys = (PyProperties,)
    contextual = False
    memoized = False
class BlToGd_PropertyCollection(BlToGd_Transformer):
    _keys = (BlGdPropertyCollection,)
    contextual = False
    memoized = False


## GROUPINGS ##

gd_to_bl = GdToBl_TransformerSet("Properties", [
    GdToBl_Primitive,
    GdToBl_Vector,
    GdToBl_Reference,
    GdToBl_Dictionary,
    GdToBl_Array,
    GdToBl_PropertyCollection,
], 
options={
    "properties":GdToBl_Options,
})

bl_to_gd = BlToGd_TransformerSet("Properties", [
    BlToGd_Primitive,
    BlToGd_Vector,
    BlToGd_Reference,
    BlToGd_Dictionary,
    BlToGd_Array,
    BlToGd_PropertyCollection,
],
options={
    "properties":BlToGd_Options,
})

