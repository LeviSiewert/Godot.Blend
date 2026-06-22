from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

''' This module is for translating between GdProperty Collection and the BLProperty Collection structures
As the BLPropertyCollection is a unique datastructure for blender with nested arrays,dicts and variant types, it requires a subruleset to apply values correctly.
Value extraction is best done on the Node that holds the container, and allow that container to pass a slice of the Property Collection to store in blender. 
'''

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
) 

from ....GdPy.structure.core.property_collection import PropertyCollection
from ..core.properties import (
    BlPropertyCollection, 
    BlPrimitive, 
    BlFloatVector, 
    BlIntVector,
    BlArray, BlArrayWrapper,
    BlDictionary, BlDictionaryWrapper, 
    BlDictionaryItem, BlDictionaryItemWrapper,
)


class PROPCOL_PyToBl_BlDictionary(PyToBl):
    _keys = (GdValueDictionary,)

    def transform(self, node:GdValueDictionary, c, *args, **kwargs)->str:
        ''' BlDictionary, BlArray, BlPointer, ect all require contextual property_collection to add themselves to, and they return the pointer to themselves '''

        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not (propcol is None))

        ptr = propcol._generate_pointer()
        inst = propcol.bin_dictionaries.new()
        inst.name = ptr 

        for k,v in node.items():
            k_ptr, k_obj = propcol.new(k.__class__.__name__)
            t = c.existing_object.set(k_obj)
            yield(k,)
            c.existing_object.reset(t)
            
            v_ptr, v_obj = propcol.new(v.__class__.__name__)
            t = c.existing_object.set(v_obj)
            yield(v,)
            c.existing_object.reset(t)

            entry = inst.items.new()
            entry.key_ptr = k_ptr.ptr
            entry.val_ptr = v_ptr.ptr
            
        return ptr

class PROPCOL_BlToPy_BlDictionary(BlToPy):
    _keys = (BlDictionary, BlDictionaryWrapper,)

    def transform(self, node:BlDictionary, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not(propcol is None))
        
        res = PropertyCollection()

        for entry in node.items.values():
            k = propcol.fetch_pointer_data(entry.key_ptr, _wrap_complex=False)
            v = propcol.fetch_pointer_data(entry.val_ptr, _wrap_complex=False)
            yield (k,v)
            m = c.children_map.get()
            res[m[k]] = m[v]

        return res

class PROPCOL_PyToBl_BlArray(PyToBl):
    _keys = (GdValueArray,)
    
    def transform(self, node, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not(propcol is None))
        
        ptr = propcol._generate_pointer()
        inst = propcol.bin_dictionaries.new()
        inst.name = ptr
        
        yield node
        for _ptr in c.children.get():
            obj = inst.new()
            obj.val_ptr = _ptr

        return ptr

class PROPCOL_BlToPy_BlArray(BlToPy):
    _keys = (BlArray, BlArrayWrapper,)
    
    def transform(self, node, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not(propcol is None))

        res = GdValueArray()
        yield node.values()
        res.extend(c.children.get())

        return res

class PROPCOL_BlToPy_BlPrimitive(BlToPy):
    _keys = (BlPrimitive,)
    def transform(self, node, c, *args, **kwargs):
        raise Exception()
class PROPCOL_PyToBl_BlPrimitive(PyToBl):
    _keys = (GdValueStringName,int,float,bool,None,str)
    def transform(self, node, c, *args, **kwargs):
        raise Exception()

class PROPCOL_BlToPy_BlFloatVector(BlToPy):
    _keys = (BlFloatVector,)
    def transform(self, node, c, *args, **kwargs):
        raise Exception()
class PROPCOL_PyToBl_BlFloatVector(PyToBl):
    _keys = (GdValuePackedFloat32Array,GdValuePackedFloat64Array,GdValueVector2,GdValueVector3,GdValueVector4,GdValueRect2,GdValuePlane,GdValueColor,GdValueAABB,GdValueQuaternion,GdValueTransform2D,GdValueBasis,GdValueTransform3D,)
    def transform(self, node, c, *args, **kwargs):
        raise Exception()

class PROPCOL_BlToPy_BlIntVector(BlToPy):
    _keys = (BlIntVector,)
    def transform(self, node, c, *args, **kwargs):
        raise Exception()
class PROPCOL_PyToBl_BlIntVector(PyToBl):
    _keys = (GdValueVector2i,GdValueVector3i,GdValueVector4i,GdValueRect2i,GdValuePackedInt32Array,GdValuePackedInt64Array),
    def transform(self, node, c, *args, **kwargs):
        raise Exception()


PROPCOL_py_to_bl_ruleset = BlToPyRuleset((
    PROPCOL_PyToBl_BlDictionary(),
    PROPCOL_PyToBl_BlArray(),
    PROPCOL_PyToBl_BlPrimitive(),
    PROPCOL_PyToBl_BlFloatVector(),
    PROPCOL_PyToBl_BlIntVector(),
    )
)

PROPCOL_bl_to_py_ruleset = PyToBlRuleset((
    PROPCOL_BlToPy_BlDictionary(),
    PROPCOL_BlToPy_BlArray(),
    PROPCOL_BlToPy_BlPrimitive(),
    PROPCOL_BlToPy_BlFloatVector(),
    PROPCOL_BlToPy_BlIntVector(),
))

class PyToBl_PropertyCollection(PyToBl):
    _keys = (PropertyCollection,)

    def transform(self, node:PropertyCollection, c, *args, **kwargs):
        """ Property Collection aready exists """
        bl_props : BlPropertyCollection = c.existing_object.get()
        t = c.property_collection.set(bl_props)
        t1 = c.current_rulesets.set( (*c.current_rulesets.get(), PROPCOL_py_to_bl_ruleset) )

        assert(not(bl_props is None))

        for k,v in node.items.items():
            yield (v,)
            res_ptr = c.children.get()[0]
            entry = bl_props.properties.new()
            
            entry.name = k
            entry.value = res_ptr 
        
        c.property_collection.reset(t)
        c.current_rulesets.reset(t1)

        return bl_props


class BlToPy_PropertyCollection(BlToPy):
    _keys = (BlPropertyCollection,)

    def transform(self, node:BlPropertyCollection, c, *args, **kwargs):
        t = c.property_collection.set(node)
        t1 = c.current_rulesets.set( (*c.current_rulesets.get(), PROPCOL_bl_to_py_ruleset) )

        res = {}
        for k,v in node.properties.items():
            yield (v,)
            child = c.children.get()[0]
            res[k] = child

        c.current_rulesets.reset(t1)
        c.property_collection.reset(t)
        return PropertyCollection(res.items())
    

py_to_bl_ruleset = BlToPyRuleset((
    PyToBl_PropertyCollection(),
    ))

bl_to_py_ruleset = PyToBlRuleset((
    BlToPy_PropertyCollection(),
    ))