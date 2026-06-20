import bpy
from bpy.types import PropertyGroup
# from bpy.types import IntProperty as IntPropertyType
# from bpy.types import StringProperty as FloatPropertyType
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatProperty, PointerProperty

class BlProperty(PropertyGroup):
    name : StringProperty() #type:ignore

    type : StringProperty() #type:ignore

    val_boolean : BoolProperty() #type:ignore
    val_float : FloatProperty() #type:ignore
    val_int : IntProperty() #type:ignore
    val_str : StringProperty() #type:ignore

    val_reflection : StringProperty() #type:ignore
    ## FUTURE: Allowence for refering back to another property as a nested property
    ## IE dict[str,list[dict]] ...


class ArrayIntItem(PropertyGroup):
    val : IntProperty() #type:ignore
class BlPropertyArrayInt(PropertyGroup):
    items : CollectionProperty(type = ArrayIntItem) #type:ignore
    # items : CollectionProperty(type = IntPropertyType) #type:ignore

class ArrayFloatItem(PropertyGroup):
    val : IntProperty() #type:ignore
class BlPropertyArrayFloat(PropertyGroup):
    items : CollectionProperty(type = ArrayFloatItem) #type:ignore
    # items : CollectionProperty(type = FloatPropertyType) #type:ignore

class BlPropertyDictItem(PropertyGroup):
    key : PointerProperty(type = BlProperty) #type:ignore
    item : PointerProperty(type = BlProperty) #type:ignore

class BlPropertyDict(PropertyGroup):
    items : CollectionProperty(type = BlProperty) #type:ignore


class BlPropertyArray(PropertyGroup):
    name : StringProperty() #type:ignore
    type_a : StringProperty() #type:ignore
    type_b : StringProperty() #type:ignore
    items : CollectionProperty(type = BlProperty) #type:ignore

class BlPropertyArrayVector(PropertyGroup):
    name : StringProperty() #type:ignore
    items : CollectionProperty(type = BlPropertyArrayFloat) #type:ignore

class BlPropertyCollection(PropertyGroup):
    items : CollectionProperty(type = BlProperty) #type:ignore
    dict_items : CollectionProperty(type = BlPropertyDict) #type:ignore
    array_items : CollectionProperty(type = BlPropertyArray) #type:ignore
    array_int_items : CollectionProperty(type = BlPropertyArrayInt) #type:ignore
    array_float_items : CollectionProperty(type = BlPropertyArrayFloat) #type:ignore
    array_vector_items : CollectionProperty(type = BlPropertyArrayVector) #type:ignore
    
    ## TODO: Add interface


_all = (
    BlProperty,
    ArrayIntItem,
    ArrayFloatItem,
    BlPropertyArrayInt,
    BlPropertyArrayFloat,
    BlPropertyArrayVector,
    BlPropertyArray,
    BlPropertyDictItem,
    BlPropertyDict,
    BlPropertyCollection,
)