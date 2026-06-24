import bpy
from typing import Generator

from .utils import BlenderPytestAttr
from ..structure.core.properties import BlPropertyCollection, BlArray, BlDictionary, BlPrimitives, BlVectors
from ..structure.core.primitives.pointer_collection import BlPointerArrayItemWrapper, BlPointerArrayWrapper, BlPointerDictionaryItemWrapper, BlPointerDictionaryWrapper, _Wrapper
from ...GdPy.structure.core.property_collection import PropertyCollection as GdPropertyCollection
from ...GdPy.structure import values as GdPy



from typing import Any

from ..structure.transformers.property_collection import py_to_bl_ruleset, bl_to_py_ruleset
from ...GdPy.structure.core.transformer_v2 import Transformer

from ..structure.transformers.core import BlPyTransformerContext

from contextlib import contextmanager

_bl_to_py_transformer = Transformer((bl_to_py_ruleset,))
_bl_to_py_context = BlPyTransformerContext(_bl_to_py_transformer)

@contextmanager
def _bl_to_py(bl_pc)->Generator[GdPropertyCollection]:
    ''' Yield a new GdPropertyCollection from the BlPropertyCollection object'''
    t = _bl_to_py_context.property_collection.set(bl_pc)
    t1 = _bl_to_py_context.existing_object.set(bl_pc)
    yield _bl_to_py_transformer.transform_tree(_bl_to_py_context,bl_pc)
    _bl_to_py_context.property_collection.set(t)
    _bl_to_py_context.existing_object.reset(t1)
    bl_pc.clear()

_py_to_bl_transformer = Transformer((py_to_bl_ruleset,))
_py_to_bl_context = BlPyTransformerContext(_py_to_bl_transformer)
@contextmanager
def _py_to_bl(bl_pc, gd_pc)->Generator[BlPropertyCollection]:
    ''' Yield a transformed bl_pc (same as input object)'''
    t = _py_to_bl_context.property_collection.set(bl_pc)
    t1 = _py_to_bl_context.existing_object.set(bl_pc)
    yield _py_to_bl_transformer.transform_tree(_py_to_bl_context,gd_pc)
    _py_to_bl_context.property_collection.set(t)
    _py_to_bl_context.existing_object.reset(t1)
    bl_pc.clear()

class TestBehavior(BlenderPytestAttr):
    attr_value = bpy.props.PointerProperty(type = BlPropertyCollection)
    
    @contextmanager
    def _adding_removal(self, expected_bin_id:str, value:str, /, prop_name:str="A", expect_wrapped=False, subtype:str=None, yield_wrapped=False):
        bl_pc : BlPropertyCollection = self.get_attr()
        stats = {b:len(b) for b in bl_pc._iter_bins()} | {bl_pc.properties:len(bl_pc.properties)}

        obj,ptr = bl_pc.new_property(prop_name, value, wrap=False)

        if subtype:
            assert (obj.subtype == subtype)

        assert (bl_pc._bin_val_matcher(value) == bl_pc._bin_id_matcher(expected_bin_id))

        if expect_wrapped:        
            assert (bl_pc[ptr.ptr].data == obj)
            assert (bl_pc[prop_name].data == obj)
            # assert (isinstance(bl_pc.get(prop_name, return_prop=False, wrap=True), _Wrapper))
            assert (bl_pc.get(prop_name, return_prop=False, wrap=True).data == obj)
        else:
            assert (bl_pc[ptr.ptr] == obj)
            assert (bl_pc[prop_name] == obj)
        assert (bl_pc.get(prop_name, return_prop=False, wrap=False) == obj)

        assert (bl_pc.get(prop_name, return_prop=True, wrap=False) == ptr)

        assert (dict(bl_pc.items(wrap=False))[prop_name] == obj )

        if yield_wrapped:
            yield bl_pc._wrap(obj), bl_pc._wrap(ptr)
        else:
            yield obj,ptr

        bl_pc.delete_property(prop_name)

        for k,v in stats.items():
            assert(len(k) == v)

    def adding_removal(self, *args, **kwargs):
        with self._adding_removal(*args, **kwargs):
            pass

    def test_adding_removal(self,):
        
        self.adding_removal("bin_primitive", "a")
        self.adding_removal("bin_primitive", 1)
        self.adding_removal("bin_primitive", 2.0)
        self.adding_removal("bin_primitive", 0.01)

        self.adding_removal("bin_dict", {}, expect_wrapped=True)
        self.adding_removal("bin_array", [], expect_wrapped=True)
        
        self.adding_removal("bin_primitive", GdPy.GdValueStringName(), subtype = "GdValueStringName")
        self.adding_removal("bin_primitive", GdPy.GdValueStringName("Value"), subtype = "GdValueStringName")
        
        self.adding_removal("bin_vector", GdPy.GdValueVector2((1,2)), subtype = "GdValueVector2" )

        #TODO: Expand out to all types and fullfill

    @contextmanager
    def _array_adding_removal(self, value_bin_id:str, value):
        propcol : BlPropertyCollection = self.get_attr()
        with self._adding_removal("bin_array", [],  prop_name="ARRAY" ,expect_wrapped=True, yield_wrapped=True) as (arr,ptr):
            ##TODO: More  assertions for behavioral constraining

            _start_count = len(propcol._bin_id_matcher(value_bin_id))
            assert (isinstance(arr, BlPointerArrayWrapper))
            assert (len(arr) == 0)
            obj,ptr = arr.new(value, wrap=False)
            assert (len(arr) == 1)
            # assert (arr.data[0] == ptr.data)
            assert (arr.get(0,wrap=False) == obj)
            yield arr,ptr
            arr.clear()
            assert (len(arr) == 0)
            assert (len(propcol._bin_id_matcher(value_bin_id)) == _start_count)

    def array_adding_removal(self,*args,**kwargs):
        with self._array_adding_removal(*args,**kwargs):
            pass

    def test_array_behavior(self,):
        self.array_adding_removal("bin_primitive","a", )

        self.array_adding_removal("bin_primitive", "a")
        self.array_adding_removal("bin_primitive", 1)
        self.array_adding_removal("bin_primitive", 2.0)
        self.array_adding_removal("bin_primitive", 0.01)

        self.array_adding_removal("bin_dict", {})
        self.array_adding_removal("bin_array", [])
        
        self.array_adding_removal("bin_primitive", GdPy.GdValueStringName())
        self.array_adding_removal("bin_primitive", GdPy.GdValueStringName("Value"))
        
        self.array_adding_removal("bin_vector", GdPy.GdValueVector2((1,2)))

    @contextmanager
    def _dictionary_adding_removal(self, k, v, yield_wrapped=True): #->tuple[Any, Obj, Obj]:
        propcol : BlPropertyCollection = self.get_attr()
        with self._adding_removal("bin_dict", {}, prop_name="DICT", expect_wrapped=True, yield_wrapped=True) as (di,ptr):
            di : BlPointerDictionaryWrapper
            ##TODO: More  assertions for behavioral constraining

            k_bin,k_val = k
            v_bin,v_val = v

            entry = di.new(k_val,v_val, key_bin=k_bin, val_bin=v_bin, wrap=True)

            k_obj = entry.key_unwrapped
            v_obj = entry.value_unwrapped

            if isinstance(k_val, float):
                assert (abs(k_val - k_obj.value)<0.0001)
            elif isinstance(k_val, (list,dict,*GdPy._array_types.values(),*GdPy._dict_types.values())):
                pass ##TODO: Evaluation of complex types?
            elif isinstance(k_val, (*GdPy._vector_types.values(),)):
                pass ##TODO: Evaluation of complex types?
            else:
                assert (k_val == k_obj.value)

            if isinstance(v_val, float):
                assert (abs(v_val - v_obj.value)<0.0001)
            elif isinstance(v_val, (list,dict,*GdPy._array_types.values(),*GdPy._dict_types.values())):
                pass ##TODO: Evaluation of complex types?
            elif isinstance(v_val, (*GdPy._vector_types.values(),)):
                pass ##TODO: Evaluation of complex types?
            else:
                assert (v_val == v_obj.value)


            assert (k_obj in propcol._bin_id_matcher(k_bin).values())
            assert (v_obj in propcol._bin_id_matcher(v_bin).values())

            if yield_wrapped:
                yield entry, entry.key, entry.value
            else:
                yield entry.value, entry.key, entry.value 

            di.remove(0)

            assert (len(tuple(di.items()))==0)
            assert (not (k_obj in propcol._bin_id_matcher(k_bin).values()))
            assert (not (v_obj in propcol._bin_id_matcher(v_bin).values()))

    
    def dictionary_adding_removal(self, *args, **kwargs):
        with self._dictionary_adding_removal(*args, **kwargs):
            pass

    def test_dictionary_behavior(self,):
        self.dictionary_adding_removal(("bin_primitive","a",) , ("bin_primitive","a",) )

        self.dictionary_adding_removal(("bin_primitive", "a"), ("bin_primitive", "a"))
        self.dictionary_adding_removal(("bin_primitive", 1), ("bin_primitive", 1))
        self.dictionary_adding_removal(("bin_primitive", 2.0), ("bin_primitive", 2.0))
        self.dictionary_adding_removal(("bin_primitive", 0.01), ("bin_primitive", 0.01))

        self.dictionary_adding_removal(("bin_dict", {}) , ("bin_dict", {}))
        self.dictionary_adding_removal(("bin_array", []) , ("bin_array", []))
        
        self.dictionary_adding_removal(("bin_primitive", GdPy.GdValueStringName()) , ("bin_primitive", GdPy.GdValueStringName()))
        self.dictionary_adding_removal(("bin_primitive", GdPy.GdValueStringName("Value")) , ("bin_primitive", GdPy.GdValueStringName("Value")))
        
        self.dictionary_adding_removal(("bin_vector", GdPy.GdValueVector2((1,2))) , ("bin_vector", GdPy.GdValueVector2((1,2))))


# class TestPrimitives():
#     pass