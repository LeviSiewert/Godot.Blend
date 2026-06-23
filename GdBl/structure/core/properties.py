import bpy
from .primitives.pointer_collection import PointerCollection, BlPointerArray, BlPointerDictionary, _UNSET
from typing import Type
from ....GdPy.structure.values import _primitive_types, _vector_types, _array_types, _dict_types, _type_map


class BlPrimitives(bpy.types.PropertyGroup):
    _subtypes = (*_primitive_types.keys(), "string", "int", "float", "bool", "None")
    name : bpy.props.StringProperty() #type:ignore

    subtype : bpy.props.StringProperty(default="str") #type:ignore

    @property
    def value(self,):
        return getattr(self, "val_"+self.subtype.lower().replace("gdtype",""), _UNSET)
    @value.setter
    def value(self, value):
        setattr(self, "val_"+self.subtype.lower().replace("gdtype",""), value)

    val_string : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_float : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore

class BlVectors(bpy.types.PropertyGroup):
    _subtypes = (*_vector_types.keys(),)
    name : bpy.props.StringProperty() #type:ignore
    subtype : bpy.props.StringProperty(default="UNSET") #type:ignore

    @property
    def value(self,):
        return getattr(self, self.subtype.lower().replace("gdtype",""), _UNSET)
    @value.setter
    def value(self, value):
        setattr(self, "val_"+self.subtype.lower().replace("gdtype",""), value)

    vector2 : bpy.props.FloatVectorProperty(size = 2) #type:ignore
    vector3 : bpy.props.FloatVectorProperty(size = 3) #type:ignore
    vector4 : bpy.props.FloatVectorProperty(size = 4) #type:ignore
    rect2 : bpy.props.FloatVectorProperty(size = 4) #type:ignore
    plane : bpy.props.FloatVectorProperty(size = 6) #type:ignore
    color : bpy.props.FloatVectorProperty(size = 4, subtype="COLOR") #type:ignore
    aabb : bpy.props.FloatVectorProperty(size = 6) #type:ignore
    quaternion : bpy.props.FloatVectorProperty(size = 4, subtype="QUATERNION") #type:ignore
    basis : bpy.props.FloatVectorProperty(size = 9, subtype="MATRIX") #type:ignore
    
    transform2d : bpy.props.FloatVectorProperty(size = 6) #type:ignore
    transform3d : bpy.props.FloatVectorProperty(size = 12) #type:ignore
    
    vector2i : bpy.props.IntVectorProperty(size=2) #type:ignore
    vector3i : bpy.props.IntVectorProperty(size=3) #type:ignore
    vector4i : bpy.props.IntVectorProperty(size=4) #type:ignore
    rect2i : bpy.props.IntVectorProperty(size=4) #type:ignore

class BlDictionary(BlPointerDictionary):
    _subtypes = (*_dict_types.keys(),)
    subtype : bpy.props.StringProperty(default="Dictionary") #type:ignore
    
class BlArray(BlPointerArray):
    _subtypes = (*_array_types.keys(),)
    subtype : bpy.props.StringProperty(default="Array") #type:ignore

def _map_keys(*items)->dict[str,Type]:
    res = {}
    for c in items:
        for t in c._subtypes:
            res[t]= c
    return res

class BlPropertyCollection(PointerCollection):
    ''' 
    Implementation for Gd of multi-object pointer collection, which was seperated for future use w/ generic File, Res, SubRes
    Considering using a TransformerV2 for store_value, as Dict, Array, are basically already doing so with a limited scope.
    ''' 
    #TODO: A-B testing of number of unique vs collection types 

    _bins = ("bin_array","bin_dict","bin_vector","bin_primitive")
    _bin_map = _map_keys(BlArray,BlDictionary,BlPrimitives,BlVectors)

    bin_array : bpy.props.CollectionProperty(type = BlArray) #type:ignore
    bin_dict : bpy.props.CollectionProperty(type = BlDictionary) #type:ignore
    bin_vector : bpy.props.CollectionProperty(type = BlPrimitives) #type:ignore
    bin_primitive : bpy.props.CollectionProperty(type = BlVectors) #type:ignore

    def _bin_val_matcher(self, val):
        if val is None:
            return self.bin_primitive
        if isinstance(val,list):
            return "bin_array"
        if isinstance(val,dict):
            return "bin_dict"
        return self._bin_map[val.__class__.__name__]
        

_all = (
    BlPrimitives,
    BlVectors,
    BlDictionary,
    BlArray,
    BlPropertyCollection,
)