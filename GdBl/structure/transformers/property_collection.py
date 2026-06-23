from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

from ....GdPy.structure.core.transformer_v2 import TERMINAL

from ....GdPy.structure.core.property_collection import PropertyCollection as GdPropertyCollection
from ....GdPy.structure.values import (
    GdValueArray,
    GdValueDictionary,
    GdValueVector2i,
    GdValueVector3i,
    GdValueVector4i,
    GdValueRect2i,
    GdValuePackedInt32Array,
    GdValuePackedInt64Array,
    GdValuePackedFloat32Array,
    GdValuePackedFloat64Array,
    GdValueVector2,
    GdValueVector3,
    GdValueVector4,
    GdValueRect2,
    GdValuePlane,
    GdValueColor,
    GdValueAABB,
    GdValueQuaternion,
    GdValueTransform2D,
    GdValueBasis,
    GdValueTransform3D,
    GdValueStringName,
    GdValuePackedByteArray,  
    GdValuePackedStringArray, 
    GdValuePackedVector2Array, 
    GdValuePackedVector3Array, 
    GdValuePackedVector4Array, 
    GdValuePackedColorArray,
    _type_map
) 

from ..core.properties import (
    BlPropertyCollection, 
    BlVectors, 
    BlPrimitives, 
    BlDictionary, 
    BlArray
) 
from ..core.primitives.pointer_collection import (
    BlPointerDictionaryWrapper,
    BlPointerArrayWrapper,
)

class BlToPy_Primitives(BlToPy):
    _keys = (BlPrimitives,)
    def transform(self, node:BlVectors, c, *args, **kwargs):
        yield TERMINAL
        return _type_map[node.subtype](node.value)  
class PyToBl_Primitives(PyToBl):
    _keys = (str, int, bool, None)
    def transform(self, node, c, *args, **kwargs): #->str (ptr)
        yield TERMINAL
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))
        raise NotImplementedError(self.__class__.__name__)

class BlToPy_Vectors(BlToPy):
    _keys = (BlVectors,)
    def transform(self, node:BlVectors, c, *args, **kwargs):
        yield TERMINAL
        if node.value is None:
            return None
        return _type_map[node.subtype](node.value)  
class PyToBl_Vectors(PyToBl):
    _keys = (GdValueVector2,GdValueVector3,GdValueVector4,GdValueRect2,GdValuePlane,GdValueColor,GdValueAABB,GdValueQuaternion,GdValueBasis,GdValueTransform2D,GdValueTransform3D,GdValueVector2i,GdValueVector3i,GdValueVector4i,GdValueRect2i)
    def transform(self, node, c, *args, **kwargs): #->str (ptr)
        yield TERMINAL
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))
        if node is None:
            obj,ptr = propcol.store_value(None)
            return ptr 
        obj,ptr = propcol.store_value(node, subtype=_type_map[node.__class__])
        return ptr


class BlToPy_Dictionary(BlToPy):
    _keys = (BlDictionary, BlPointerDictionaryWrapper)
    def transform(self, node:BlDictionary|BlPointerDictionaryWrapper, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))
        
        if not isinstance(node, BlPointerDictionaryWrapper):
            node = BlPointerDictionaryWrapper(propcol, node)
        yield dict(node.items(wrap=True))
        return GdValueDictionary(c.children.get())

class PyToBl_Dictionary(PyToBl):
    _keys = (GdValueDictionary,)
    def transform(self, node:GdValueDictionary, c, *args, **kwargs): #->str (ptr)
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))

        obj,ptr = propcol.store_value(bin_id = "GdValueDictionary")

        for k,v in node.items.items():
            item = obj.items.add()
            yield (k,v)
            _m = c.children_map.get()
            item.key_ptr = _m[k]
            item.val_ptr = _m[v]

        return ptr


class BlToPy_Array(BlToPy):
    _keys = (BlArray,BlPointerArrayWrapper)
    def transform(self, node:BlArray|BlPointerArrayWrapper, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))
        if not isinstance(node, BlPointerArrayWrapper):
            node = BlPointerArrayWrapper(propcol, node)
        yield node.values()
        return GdValueArray(c.children.get())

class PyToBl_Array(PyToBl):
    _keys = (GdValueArray, GdValuePackedByteArray, GdValuePackedInt32Array, GdValuePackedInt64Array, GdValuePackedFloat32Array,GdValuePackedFloat64Array, GdValuePackedStringArray, GdValuePackedVector2Array, GdValuePackedVector3Array, GdValuePackedVector4Array, GdValuePackedColorArray )
    def transform(self, node, c, *args, **kwargs): #->str (ptr)
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))

        obj,ptr = propcol.store_value(bin_id = _type_map[node])
        obj.subtype = _type_map[node]

        yield node.__iter__()

        for c_ptr in c.children.get():
            e = obj.items.new()
            e.ptr = c_ptr

        return ptr


_PROPCOL_bl_to_py_ruleset = BlToPyRuleset(__file__+" :: PROPCOL", (
    BlToPy_Vectors,
    BlToPy_Primitives,
    BlToPy_Dictionary,
    BlToPy_Array,
))
_PROPCOL_py_to_bl_ruleset = PyToBlRuleset(__file__+" :: PROPCOL", (
    PyToBl_Vectors,
    PyToBl_Primitives,
    PyToBl_Dictionary,
    PyToBl_Array,
))


class BlToPy_PropertyCollection(BlToPy):
    _keys = (BlPropertyCollection,)
    def transform(self, node:BlPropertyCollection, c, *args, **kwargs): #->GdPropertyCollection
        t0 = c.property_collection.set(node)
        t1=c.current_rulesets.set(_PROPCOL_bl_to_py_ruleset)

        yield dict(node.items())
        res = GdPropertyCollection(c.children.get().items())

        c.current_rulesets.reset(t1)
        c.property_collection.set(t0)
        return res

class PyToBl_PropertyCollection(PyToBl):
    _keys = (GdPropertyCollection,)
    def transform(self, node:GdPropertyCollection, c, *args, **kwargs): #->BlPropertyCollection
        t0 = c.property_collection.set(node)
        t1=c.current_rulesets.set(_PROPCOL_py_to_bl_ruleset)
        propcol : BlPropertyCollection = c.existing_object.get()
        assert(propcol)

        yield dict(node.items.items())
        for k, ptr in c.children.get().items():
            propcol.set_property(ptr=ptr)

        c.property_collection.reset(t0)
        c.current_rulesets.reset(t1)
        return propcol 


_bl_to_py_ruleset = BlToPyRuleset(__file__, (
    BlToPy_PropertyCollection,
    ))

_py_to_bl_ruleset = PyToBlRuleset(__file__, (
    PyToBl_PropertyCollection,
    ))