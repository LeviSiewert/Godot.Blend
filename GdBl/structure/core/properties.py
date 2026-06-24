import bpy
from .primitives.pointer_collection import PointerCollection, BlPointerArray, BlPointerDictionary, _UNSET
from typing import Type
from ....GdPy.structure.values import _primitive_types, _vector_types, _array_types, _dict_types, _type_map
from ....GdPy.structure.values import GdValueStringName


def _reverse_dict_tuple(di: dict[str,tuple[str]])->dict[str,str]:
    res = {}
    for v,t in di.items():
        for k in t:
            res[k] = v
    return res

class BlPrimitives(bpy.types.PropertyGroup):
    _subtypes = (*_primitive_types.keys(),)
    name : bpy.props.StringProperty() #type:ignore

    subtype : bpy.props.StringProperty(default="str") #type:ignore

    def set_value(self, val):
        self.value = val

    @property
    def value(self,):
        return getattr(self, self._attr_map[self.subtype])
    @value.setter
    def value(self, value):
        self.subtype = _type_map[value.__class__]
        setattr(self, self._attr_map[self.subtype] , self._cast(value))

    def _cast(self, val):
        if isinstance(val, GdValueStringName):
            return str(val)
        return val

    _attr_map = _reverse_dict_tuple({
        "val_str" : ("str","GdValueStringName"),
        "val_int" : ("int",),
        "val_float" : ("float",),
        "val_bool" : ("bool",),  
    })

    val_str : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_float : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore


class BlVectors(bpy.types.PropertyGroup):
    _subtypes = (*_vector_types.keys(),)
    name : bpy.props.StringProperty() #type:ignore
    subtype : bpy.props.StringProperty(default="UNSET") #type:ignore

    @property
    def value(self,):
        return getattr(self, self.subtype.lower().replace("gdvalue",""))
    @value.setter
    def value(self, value):
        self.subtype = _type_map[value.__class__]
        setattr(self, self.subtype.lower().replace("gdvalue",""), value)

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

    def set_value(self, val):
        self.value = val

class BlDictionary(BlPointerDictionary):
    _subtypes = (*_dict_types.keys(),)
    subtype : bpy.props.StringProperty(default="Dictionary") #type:ignore
    name : bpy.props.StringProperty() #type:ignore
    
class BlArray(BlPointerArray):
    _subtypes = (*_array_types.keys(),)
    subtype : bpy.props.StringProperty(default="Array") #type:ignore
    name : bpy.props.StringProperty() #type:ignore

    # items : bpy.props.CollectionProperty(type = BlPointerArrayItem) #type:ignore

def _map_keys(di:dict)->dict[str,Type]:
    res = {}
    for s,v in di.items():
        for t in s._subtypes:
            res[t]= v
    return res

class BlPropertyCollection(PointerCollection):
    ''' 
    Implementation for Gd of multi-object pointer collection, which was seperated for future use w/ generic File, Res, SubRes
    Considering using a TransformerV2 for store_value, as Dict, Array, are basically already doing so with a limited scope.
    ''' 
    #TODO: A-B testing of number of unique vs collection types 

    _bins = ("bin_array","bin_dict","bin_vector","bin_primitive")
    _bin_map = _map_keys({BlArray:"bin_array",BlDictionary:"bin_dict",BlPrimitives:"bin_primitive",BlVectors:"bin_vector"})

    bin_array : bpy.props.CollectionProperty(type = BlArray) #type:ignore
    bin_dict : bpy.props.CollectionProperty(type = BlDictionary) #type:ignore
    bin_vector : bpy.props.CollectionProperty(type = BlVectors) #type:ignore
    bin_primitive : bpy.props.CollectionProperty(type = BlPrimitives) #type:ignore

    def _bin_id_matcher(self, bin_id:str)->bpy.types.CollectionProperty:
        if not ((res := getattr(self, bin_id, None)) is None):
            return res
        raise KeyError("Could not determine bin for key", bin_id)

    def _bin_val_matcher(self, val):
        if val is None:
            return self.bin_primitive
        if isinstance(val,list):
            return self.bin_array
        if isinstance(val,dict):
            return self.bin_dict
        return getattr(self, self._bin_map[val.__class__.__name__])
        

_all = (
    BlPrimitives,
    BlVectors,
    BlDictionary,
    BlArray,
    BlPropertyCollection,
)