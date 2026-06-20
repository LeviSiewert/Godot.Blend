import bpy
from bpy.types import PropertyGroup
# from bpy.types import IntProperty as IntPropertyType
# from bpy.types import StringProperty as FloatPropertyType
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatProperty, PointerProperty
from .primitives.flatpack_collection import FlatPackCollection, FlatPackItemInterface

class BlProperty(bpy.types.PropertyGroup): #FlatPackItemInterface
    ''' Generic "multitype" '''
    name : StringProperty() #type:ignore

    type : StringProperty() #type:ignore

    val_boolean : BoolProperty() #type:ignore
    val_float : FloatProperty() #type:ignore
    val_int : IntProperty() #type:ignore
    val_str : StringProperty() #type:ignore

    val_pointer : StringProperty() #type:ignore

    def get_pointer_references(self,):
        if self.val_pointer:
            return (self.val_pointer,)
        return tuple()
    def pointer_reference_update(self, fr_pointer, old_val, to_pointer, new_val):
        if self.val_pointer == fr_pointer:
            self.val_pointer = to_pointer
    def pointer_reference_remove(self, fr_pointer, old_val):
        if self.val_pointer == fr_pointer:
            self.val_pointer = ""

class ArrayIntItem(bpy.types.PropertyGroup):
    ''' Req as I cant get collection to just create a list of bpy.types.IntProperty '''
    val : IntProperty() #type:ignore

class ArrayFloatItem(bpy.types.PropertyGroup):
    ''' Req as I cant get collection to just create a list of bpy.types.FloatProperty '''
    val : IntProperty() #type:ignore

class _ListLikeMixin(bpy.types.PropertyGroup):
    def values(self):
        return self.items.items()
    def new(self):
        res = self.items.new()
        return res


class BlPropertyArrayInt(_ListLikeMixin):
    type : StringProperty() #type:ignore
    items : CollectionProperty(type = ArrayIntItem) #type:ignore
    # items : CollectionProperty(type = IntPropertyType) #type:ignore

class BlPropertyArrayFloat(_ListLikeMixin):
    type : StringProperty() #type:ignore
    items : CollectionProperty(type = ArrayFloatItem) #type:ignore
    
class BlPropertyArrayVector(_ListLikeMixin):
    type : StringProperty() #type:ignore
    name : StringProperty() #type:ignore
    items : CollectionProperty(type = BlPropertyArrayFloat) #type:ignore
    _type_map = {
        "GdValuePackedVector2Array":"GdValueVector2",
        "GdValuePackedVector3Array":"GdValueVector3",
        "GdValuePackedVector4Array":"GdValueVector4",
        "GdValuePackedColorArray":"GdValedColor",
    }
    def new(self,):
        new = self.items.new()
        new.type = self._type_map[self.type]
        return new

class BlPropertyDictItem(bpy.types.PropertyGroup): #FlatPackItemInterface
    key : PointerProperty(type = BlProperty) #type:ignore
    item : PointerProperty(type = BlProperty) #type:ignore

    def get_flatpackitem_children(self):
        return (self.key, self.item)

class BlPropertyDict(bpy.types.PropertyGroup): #FlatPackItemInterface
    items : CollectionProperty(type = BlPropertyDictItem) #type:ignore
    type_a : StringProperty() #type:ignore
    type_b : StringProperty() #type:ignore

    def get_flatpackitem_children(self):
        return (self.items.values())
    
    def keys(self):
        return self.items.keys()
    def items(self):
        return self.items.items()
    def values(self):
        return self.items.items()
    def new(self)->BlPropertyDictItem:
        res = self.items.new()
        return res

class BlPropertyArray(bpy.types.PropertyGroup): #FlatPackItemInterface
    name : StringProperty() #type:ignore
    type_a : StringProperty() #type:ignore
    type_b : StringProperty() #type:ignore
    items : CollectionProperty(type = BlProperty) #type:ignore

    def keys(self):
        return self.items.keys()
    def items(self):
        return self.items.items()
    def values(self):
        return self.items.items()
    def new(self)->BlPropertyDictItem:
        res = self.items.new()
        return res

class BlPropertyCollection(FlatPackCollection):
    items : CollectionProperty(type = BlProperty) #type:ignore
    items_dict : CollectionProperty(type = BlPropertyDict) #type:ignore
    items_array : CollectionProperty(type = BlPropertyArray) #type:ignore
    items_array_int : CollectionProperty(type = BlPropertyArrayInt) #type:ignore
    items_array_float : CollectionProperty(type = BlPropertyArrayFloat) #type:ignore
    items_array_vector : CollectionProperty(type = BlPropertyArrayVector) #type:ignore
    
    def _map_data_collections(self):
        data = {
            self.items              : ("GdValueStringName","int","float","bool","None",), 
            self.items_dict         : ("GdValueDictionary",), 
            self.items_array        : ("GdValueArray", "GdValuePackedStringArray","GdValuePackedByteArray"), 
            self.items_array_int    : ("GdValueVector2i","GdValueVector3i","GdValueVector4i","GdValueRect2i","GdValuePackedInt32Array","GdValuePackedInt64Array"), 
            self.items_array_float  : ("GdValuePackedFloat32Array","GdValuePackedFloat64Array","GdValueVector2","GdValueVector3","GdValueVector4","GdValueRect2","GdValuePlane","GdValueColor","GdValueAABB","GdValueQuaternion","GdValueTransform2D","GdValueBasis","GdValueTransform3D",), 
            self.items_array_vector : ("GdValuePackedVector2Array","GdValuePackedVector3Array","GdValuePackedVector4Array","GdValuePackedColorArray"), 
        }
        res = {}
        for k,lv in data.items():
            for v in lv:
                res[v] = k
        return res

    def _map_pointer_collections(self):
        return self._map_data_collections()

    def _get_data_collections(self):
        return (
            self.items,
            self.items_dict,
            self.items_array,
            self.items_array_int,
            self.items_array_float,
            self.items_array_vector,
            )

    def _get_pointer_collections(self):
        return self._get_data_collections()
    
    def add_data(self, typeid, key, *args, **kwargs):
        res = super().add_data(typeid, key, *args, **kwargs)
        if hasattr(res,"type"):
            res.type = typeid
        return res
    
    def add_pointer_value(self, typeid, *args, **kwargs):
        ptr,res = super().add_pointer_value(typeid, *args, **kwargs)
        if hasattr(res,"type"):
            res.type = typeid
        return ptr,res

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