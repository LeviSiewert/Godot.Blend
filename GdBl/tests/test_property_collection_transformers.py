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
    attr_value = bpy.props.CollectionProperty(type = BlPropertyCollection)
    
    @contextmanager
    def _adding_removal(self, expected_bin_id:str, value:str, /, prop_name:str="A", expect_wrapped=False, subtype:str=None, yield_wrapped=False):
        bl_pc : BlPropertyCollection = self.get_attr()
        obj,ptr = bl_pc.new_property(prop_name, value, wrap=False)

        if subtype:
            assert (obj.subtype == subtype)

        assert (bl_pc._bin_val_matcher(value) == bl_pc._bin_val_matcher(expected_bin_id))
        assert (len(bl_pc._bin_val_matcher(value))==1)
        assert (len(bl_pc.properties)==1)

        assert (bl_pc[ptr] == obj)
        assert (bl_pc[prop_name] == obj)

        if expect_wrapped:        
            assert (isinstance(bl_pc.get(prop_name, return_prop=False, wrap=True), _Wrapper))
            assert (bl_pc.get(prop_name, return_prop=False, wrap=True).data == obj)
        assert (bl_pc.get(prop_name, return_prop=False, wrap=False) == obj)

        assert (bl_pc.get(prop_name, return_prop=True, wrap=False) == ptr)
        assert (isinstance(bl_pc.get(prop_name, return_prop=True, wrap=True), _Wrapper))

        assert (dict(bl_pc.items())[prop_name] == obj )

        assert (bl_pc.get(prop_name, return_prop=False, wrap=True).value == value)

        if yield_wrapped:
            yield bl_pc._wrap(obj), bl_pc._wrap(ptr)
        else:
            yield obj,ptr

        bl_pc.clear()
        
        assert (len(bl_pc.bin_primitive)==0)
        assert (len(bl_pc.properties)==0)

    def adding_removal(self, *args, **kwargs):
        with self._adding_remove(*args, **kwargs):
            pass

    def test_adding_removal(self,):
        
        self.adding_removal("bin_primitives", "a")
        self.adding_removal("bin_primitives", 1)
        self.adding_removal("bin_primitives", 2.0)
        self.adding_removal("bin_primitives", 0.01)

        self.adding_removal("bin_dict", {}, expect_wrapped=True)
        self.adding_removal("bin_array", [], expect_wrapped=True)
        
        self.adding_removal("bin_primitives", GdPy.GdValueStringName(), subtype = "GdValueStringName")
        self.adding_removal("bin_primitives", GdPy.GdValueStringName("Value"), subtype = "GdValueStringName")
        
        self.adding_removal("bin_vectors", GdPy.GdValueVector2((1,2)), subtype = "GdValueVector2" )

        #TODO: Expand out to all types and fullfill

    @contextmanager
    def _array_adding_removal(self, value_bin_id:str, value):
        propcol : BlPropertyCollection = self.get_attr()
        with self._adding_removal("bin_array", [],  expect_wrapped=True, yield_wrapped=True) as (arr,ptr):
            ##TODO: More  assertions for behavioral constraining

            _start_count = len(propcol._bin_id_matcher(value_bin_id))
            assert (isinstance(arr, BlPointerArrayWrapper))
            assert (len(arr) == 0)
            ptr,obj = arr.new(value)
            assert (len(arr) == 1)            
            assert (arr.data[0] == ptr.data)
            assert (arr[0] == obj)
            yield arr,ptr
            arr.clear()
            assert (len(arr) == 0)
            assert (len(propcol._bin_id_matcher(value_bin_id)) == _start_count-1)

    def array_adding_removal(self,*args,**kwargs):
        with self._array_adding_removal(*args,**kwargs):
            pass

    def test_array_behavior(self,):
        self.array_adding_removal("bin_primitives","a", )

        self.array_adding_removal("bin_primitives", "a")
        self.array_adding_removal("bin_primitives", 1)
        self.array_adding_removal("bin_primitives", 2.0)
        self.array_adding_removal("bin_primitives", 0.01)

        self.array_adding_removal("bin_dict", {})
        self.array_adding_removal("bin_array", [])
        
        self.array_adding_removal("bin_primitives", GdPy.GdValueStringName())
        self.array_adding_removal("bin_primitives", GdPy.GdValueStringName("Value"))
        
        self.array_adding_removal("bin_vectors", GdPy.GdValueVector2((1,2)))

    @contextmanager
    def _dictionary_adding_removal(self, k, v, yield_wrapped=True): #->tuple[Any, Obj, Obj]:
        propcol : BlPropertyCollection = self.get_attr
        with self._adding_removal("bin_dictionary", {},  expect_wrapped=True, yield_wrapped=True) as (di,ptr):
            ##TODO: More  assertions for behavioral constraining

            k_bin,k_val = k
            v_bin,v_val = v

            index, entry = di.new(key_val = k_val,val_val= v_val, key_bin=k_bin, val_bin=v_bin, wrap=True)

            k_obj = entry.key_unwrapped
            v_obj = entry.value_unwrapped

            assert (k_val == k_obj.value)
            assert (v_val == v_obj.value)
            assert (k_obj in propcol._bin_id_matcher(k_bin).values())
            assert (v_obj in propcol._bin_id_matcher(k_bin).values())

            if yield_wrapped:
                yield entry, entry.key, entry.value
            else:
                yield entry.value, entry.key, entry.value 

            di.remove(index)

            assert (len(di.items())==0)
            assert (not (k_obj in propcol._bin_id_matcher(k_bin).values()))
            assert (not (v_obj in propcol._bin_id_matcher(k_bin).values()))

    
    def dictionary_adding_removal(self, *args, **kwargs):
        with self._dictionary_adding_removal(*args, **kwargs):
            pass

    def test_dictionary_behavior(self,):
        self.dictionary_adding_removal(("bin_primitives","a",) , ("bin_primitives","a",) )

        self.dictionary_adding_removal(("bin_primitives", "a"), ("bin_primitives", "a"))
        self.dictionary_adding_removal(("bin_primitives", 1), ("bin_primitives", 1))
        self.dictionary_adding_removal(("bin_primitives", 2.0), ("bin_primitives", 2.0))
        self.dictionary_adding_removal(("bin_primitives", 0.01), ("bin_primitives", 0.01))

        self.dictionary_adding_removal(("bin_dict", {}) , ("bin_dict", {}))
        self.dictionary_adding_removal(("bin_array", []) , ("bin_array", []))
        
        self.dictionary_adding_removal(("bin_primitives", GdPy.GdValueStringName()) , ("bin_primitives", GdPy.GdValueStringName()))
        self.dictionary_adding_removal(("bin_primitives", GdPy.GdValueStringName("Value")) , ("bin_primitives", GdPy.GdValueStringName("Value")))
        
        self.dictionary_adding_removal(("bin_vectors", GdPy.GdValueVector2((1,2))) , ("bin_vectors", GdPy.GdValueVector2((1,2))))


# class TestPrimitives():
#     pass