from ....GdPy.core.property_collection import (
    PropertyCollection as PyPropertyCollection,
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

from ....GdPy.core.structure import(
    ResourceRef as PyResourceRef,
    RID as PyRID,
)

from ....GdPy.core.resources import(
    ExtResourceRef as PyExtResourceRef,
    SubResourceRef as PySubResourceRef,
)

from ...core.property_collection import (
    GdDictionary as BlGdDictionary,
    GdArray as BlGdArray,
    GdPrimitive as BlGdPrimitive,
    GdVector as BlGdVector,
    GdReference as BlGdReference,
    GdPropertyCollection as BlGdPropertyCollection
)
from ...core.primitives.pointer_collection import (
    BlPointerDictionaryItemWrapper as BlDictionaryWrapper,
    BlPointerArrayItemWrapper as BlArrayWrapper,
    # BlPropertyItem,
)

from ._transformer import (
    PyToBlContext, 
    PyToBlRuleset, 
    PyToBlModule, 
    BlToPyContext, 
    BlToPyRuleset,
    BlToPyModule,
)



class BlToPy_Primitive(BlToPyModule):
    _keys = (BlGdPrimitive,)
    def transform(self, c, node):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())

class PyToBl_Primitive(PyToBlModule):
    _keys = (PyStringName, str, int, float, bool, None)
    def transform(self, c, node):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())


class BlToPy_Vector(BlToPyModule):
    _keys = (BlGdVector,)
    def transform(self, c, node):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())

class PyToBl_Vector(PyToBlModule):
    _subtypes = (PyVector2, PyVector3, PyVector4, PyRect2, PyPlane, PyColor, PyAABB, PyQuaternion, PyBasis, PyTransform2D, PyTransform3D, PyVector2i, PyVector3i,PyVector4i, PyRect2i)

    def transform(self, c, node):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())


class BlToPy_Reference(BlToPyModule):
    _keys = (BlGdReference,)
    def transform(self, c, node):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())

class PyToBl_Reference(PyToBlModule):
    _keys = (PyExtResourceRef, PySubResourceRef, PyRID, PyResourceRef)
    def transform(self, c, node):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())


class PyToBl_Dictionary(PyToBlModule):
    _keys = (PyDictionary, )
    def transform(self, c, node:PyDictionary):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())

class BlToPy_Dictionary(BlToPyModule):
    _keys = (BlDictionaryWrapper, )
    def transform(self, c, node:BlDictionaryWrapper):
        raise NotImplementedError(c.key.get())


class PyToBl_Array(PyToBlModule):
    _keys = (PyArray, )
    def transform(self, c, node:PyArray):
        propcol = c.property_collection.get()
        raise NotImplementedError(c.key.get())

class BlToPy_Array(BlToPyModule):
    _keys = (BlArrayWrapper, )
    def transform(self, c, node:BlArrayWrapper):
        raise NotImplementedError(c.key.get())


_COL_py_to_bl_ruleset = PyToBlRuleset("Values :: COLLECTION",(
    PyToBl_Values,
    PyToBl_Dictionary,
    PyToBl_Array,
))

_COL_bl_to_py_ruleset = BlToPyRuleset("Values :: COLLECTION",(
    BlToPy_Values,
    BlToPy_Dictionary,
    BlToPy_Array,
))


class PyToBl_PropertyCollection(PyToBlModule):
    _keys = (PyPropertyCollection,)
    def transform(self, c, node:PyPropertyCollection):
        target : BlGdPropertyCollection = c.existing_object.get()
        t0 = c.property_collection.set(target)
        t1 = c.rulesets.set((_COL_py_to_bl_ruleset,))
        
        yield dict(node.items())
        res : dict[str,str] = c.children.get()
        ## Every item in _COL_py_to_bl_ruleset must attach itself to the c.property_collection and return a ptr!
        
        for key, ptr in res.items():
            target.set_property(key, ptr=ptr)

        c.rulesets.reset(t1)
        c.property_collection.reset(t0)
        
        # return target
        ## As this is mutated in place, no need to return a value (which isnt assignable elsewhere in bl anyway!)

class BlToPy_PropertyCollection(BlToPyModule):
    _keys = (BlGdPropertyCollection,)
    def transform(self, c, node:BlGdPropertyCollection):
        t0 = c.property_collection.set(node)
        t1 = c.rulesets.set((_COL_bl_to_py_ruleset,))
        
        yield dict(node.items())
        res : dict[str,str] = c.children.get()
        ## Every item in _COL_py_to_bl_ruleset must attach itself to the c.property_collection and return a ptr!
        
        yield dict(node.items(wrap=True))
        ## Yielding just node.items() would return a generator that must be consumed for the side effects to occur

        c.rulesets.reset(t1)
        c.property_collection.reset(t0)


py_to_bl_ruleset = PyToBlRuleset("PropCol :: STD",(
    PyToBl_PropertyCollection,
))

bl_to_py_ruleset = BlToPyRuleset("PropCol :: STD",(
    BlToPy_PropertyCollection,
))