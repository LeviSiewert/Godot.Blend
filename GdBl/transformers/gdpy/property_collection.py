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
    BlPointerDictionaryWrapper as BlDictionaryWrapper,
    BlPointerArrayWrapper as BlArrayWrapper,
    BlPointerDictionaryItemWrapper as BlDictionaryItemWrapper,
    BlPointerArrayItemWrapper as BlArrayItemWrapper,

)

from ._transformer import (
    PyToBlContext, 
    PyToBlRuleset, 
    PyToBlModule, 
    BlToPyContext, 
    BlToPyRuleset,
    BlToPyModule,
)


class PyToBl_Primitive(PyToBlModule):
    _keys = (PyNodePath, PyStringName, str, int, float, bool, None)
    def transform(self, c, node):
        propcol : BlGdPropertyCollection = c.property_collection.get()
        obj, ptr = propcol.store_value(val=node, bin_id="bin_primitive")
        return ptr

class BlToPy_Primitive(BlToPyModule):
    _keys = (BlGdPrimitive,)
    _subtype_map = {"NodePath": PyNodePath, "StringName" : PyStringName} 

    def transform(self, c, node:BlGdPrimitive):
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value)
        return node.value


class PyToBl_Vector(PyToBlModule):
    _keys = (PyVector2, PyVector3, PyVector4, PyRect2, PyPlane, PyColor, PyAABB, PyQuaternion, PyBasis, PyTransform2D, PyTransform3D, PyVector2i, PyVector3i,PyVector4i, PyRect2i)

    def transform(self, c, node):
        propcol : BlGdPropertyCollection = c.property_collection.get()
        obj, ptr = propcol.store_value(val=node, bin_id="bin_vector")
        return ptr

class BlToPy_Vector(BlToPyModule):
    _keys = (BlGdVector,)
    _subtype_map = {x.__class__.__name__:x for x in PyToBl_Vector._keys} 

    def transform(self, c, node:BlGdPrimitive):
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value)
        return node.value


class PyToBl_Reference(PyToBlModule):
    _keys = (PyExtResourceRef, PySubResourceRef, PyRID, PyResourceRef)
    
    def transform(self, c, node):
        propcol : BlGdPropertyCollection = c.property_collection.get()
        obj, ptr = propcol.store_value(val=node.addr, bin_id="bin_reference")
        return ptr
    
class BlToPy_Reference(BlToPyModule):
    _keys = (BlGdReference,)
    _subtype_map = {x.__class__.__name__:x for x in PyToBl_Reference._keys}
    
    def transform(self, c, node:BlGdPrimitive):
        yield (node.typing,)
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value, typing=c.children.get()[0])
        return node.value


class PyToBl_Dictionary(PyToBlModule):
    _keys = (PyDictionary, PyObject,)
    def transform(self, c, node:PyDictionary):
        propcol : BlGdPropertyCollection = c.property_collection.get()
        raise NotImplementedError(c.key.get())

    def transform(self, c, node):
        propcol : BlGdPropertyCollection = c.property_collection.get()
        obj, ptr = propcol.store_value(bin_id="bin_dictionary", wrap=False)
        obj : BlGdDictionary
        raise NotImplementedError()
        return ptr

class BlToPy_Dictionary(BlToPyModule):
    _keys = (BlDictionaryWrapper, )
    
    def transform(self, c, node:BlDictionaryWrapper):
        yield (node.data.typing,)
        typing = c.children.get()[0]
        
        di = {}
        
        for k,v in node.items():
            ## Left and right can be PyValues
            yield (k,v)
            k,v = c.children.get()
            di[k] = v

        match node.data.subtype:
            case "Object":
                return PyObject(node.data.objtype, **di)
            case "Dictionary":
                return PyDictionary(di.items(), typing=typing)
            case "":
                return PyDictionary(di.items(), typing=typing)
            case _:
                raise KeyError(node.data.subtype)


class PyToBl_Array(PyToBlModule):
    _keys = (PyArray, PyPackedInt32Array, PyPackedInt64Array, PyPackedFloat32Array, PyPackedFloat64Array, PyPackedStringArray, PyPackedVector2Array, PyPackedVector3Array, PyPackedVector4Array, PyPackedColorArray, PyPackedByteArray, )

    def transform(self, c, node):
        propcol : BlGdPropertyCollection = c.property_collection.get()
        obj, ptr = propcol.store_value(bin_id="bin_array", wrap=False)
        obj : BlGdArray
        raise NotImplementedError()
        return ptr

class BlToPy_Array(BlToPyModule):
    _keys = (BlArrayWrapper, )
    def transform(self, c, node:BlArrayWrapper):
        cls = self._subtype_map.get(node.subtype)

        if cls is PyArray:
            yield (node.data.typing,)
            typing = c.children.get()[0]
            yield node.values()
            return cls(*c.children.get(), typing=typing)
        yield node.values()
        return cls(c.children.get())


_COL_py_to_bl_ruleset = PyToBlRuleset("PropCol :: VALUES",(
    PyToBl_Primitive,
    PyToBl_Vector,
    PyToBl_Reference,
    PyToBl_Dictionary,
    PyToBl_Array,
))

_COL_bl_to_py_ruleset = BlToPyRuleset("PropCol :: VALUES",(
    BlToPy_Primitive,
    BlToPy_Vector,
    BlToPy_Reference,
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
        
        yield node.items()
        ## Generator, context must be maintained until consumed ?? TODO: ensure I'm copying context

        res = PyPropertyCollection(c.children.get().items()) 

        c.rulesets.reset(t1)
        c.property_collection.reset(t0)

        return res


py_to_bl_ruleset = PyToBlRuleset("PropCol :: STD",(
    PyToBl_PropertyCollection,
))

bl_to_py_ruleset = BlToPyRuleset("PropCol :: STD",(
    BlToPy_PropertyCollection,
))