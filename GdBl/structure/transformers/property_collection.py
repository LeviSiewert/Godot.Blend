from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset

# from ....GdPy.structure.values
from ....GdPy.structure.core.property_collection import PropertyCollection
from ..core.properties import (
    BlPropertyCollection, 
    BlPrimitive, 
    BlFloatVector, 
    BlIntVector,
    BlArray, 
    BlDictionary, 
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
    _keys = (BlDictionary,)

    def transform(self, node:BlDictionary, c, *args, **kwargs):
        propcol = c.property_collection.get()
        assert(propcol != None)
        for k,v in node.



# class PyToBl_Properties(PyToBl):
#     _keys = (PropertyCollection,)
#     def transform(self, node:PropertyCollection, c, *args, **kwargs):
#         """ This transform should be a side effect on resulting container's parent, 
#         as target object's properylist already exists. 
#         This will have to be a existing_object "thrown" by the parent into the context... somehow
#         As with all other BlCollections, children are already attached
#         """
#         bl_props : BlPropertyCollection = c.existing_object.get()
#         assert(not(bl_props is None))

#         for k, v in node:
#             p = bl_props.add()
#             p.name = k
#             t = c.existing_object.set(p)
#             yield (v,) 
#             ## Throwing child value to fullfill
#             res = c.children.get(v)
#             assert (res is p)
#             c.existing_object.reset(t)

#         return bl_props

# class BlToPy_Properties(BlToPy):
#     _keys = (BlPropertyCollection,)
#     def transform(self, node:BlPropertyCollection, c, *args, **kwargs):

#         yield res.values()
#         ## Yield all children, let god sort them out

#         di = c.children_map.get()

#         res = PropertyCollection()
#         for k,v in node.items():
#             res[k] = di[v]

#         return res

        

py_to_bl_ruleset = BlToPyRuleset(
    BlToPy_Properties(),
    )
bl_to_py_ruleset = PyToBlRuleset(
    BlToPy_Properties(),
    )