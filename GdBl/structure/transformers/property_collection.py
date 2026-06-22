from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

from ....GdPy.structure.values import (
    GdValueArray,
    GdValueDictionary,
) 
from ....GdPy.structure.core.property_collection import PropertyCollection
from ..core.properties import (
    BlPropertyCollection, 
    BlPrimitive, 
    BlFloatVector, 
    BlIntVector,
    BlArray, BlArrayWrapper,
    BlDictionary, BlDictionaryWrapper, 
    BlDictionaryItem, 
)

class PyToBl_PropertyCollection(PyToBl):
    _keys = (BlPropertyCollection,)

    def transform(self, node:PropertyCollection, c, *args, **kwargs):
        """ Property Collection aready exists """
        bl_props : BlPropertyCollection = c.existing_object.get()
        t = c.propertycollection.set(bl_props)

        assert(not(bl_props is None))

        for k,v in node.items.items():
            yield (v,)
            res_ptr = c.children.get()[0]
            entry = bl_props.properties.new()
            
            entry.name = k
            entry.value = res_ptr 

        c.propertycollection.reset(t)

        return bl_props

class BlToPy_PropertyCollection(BlToPy):
    _keys = (PropertyCollection,)

    def transform(self, node:BlPropertyCollection, c, *args, **kwargs):
        t = c.propertycollection.set(node)
        
        res = {}
        for k,v in node.properties.items():
            yield (v,)
            child = c.children.get()[0]
            res[k] = child

        c.propertycollection.reset(t)
        return PropertyCollection(res.items())

class PyToBl_GdValueDictionary(PyToBl):
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
            entry.key_ptr = k_ptr.value
            entry.val_ptr = v_ptr.value
            
        return ptr

class BlToPy_GdValueDictionary(BlToPy):
    _keys = (BlDictionary, BlDictionaryWrapper,)

    def transform(self, node:BlDictionary, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not(propcol is None))
        
        res = PropertyCollection()

        for entry in node.items.values():
            k = propcol.get(entry.key_ptr, _wrap_complex=False)
            v = propcol.get(entry.val_ptr, _wrap_complex=False)
            yield (k,v)
            m = c.children_map.get()
            res[m[k]] = m[v]

        return res

class PyToBl_GdValueArray(PyToBl):
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

class BlToPy_GdValueArray(BlToPy):
    _keys = (BlArray, BlArrayWrapper,)
    
    def transform(self, node, c, *args, **kwargs):
        propcol : BlPropertyCollection = c.property_collection.get()
        assert(not(propcol is None))

        res = GdValueArray()
        yield node.values()
        res.extend(c.children.get())

        return res

        

py_to_bl_ruleset = BlToPyRuleset(
    # BlToPy_Properties(),
    )
bl_to_py_ruleset = PyToBlRuleset(
    # BlToPy_Properties(),
    )