import bpy
from .primitives.pointer_collection import PointerCollection, BlPointerArray, BlPointerDictionary, _UNSET
from typing import Type

ITEMS =  (   
    ("UNSET", "Unset", "", 0),
    ("GDVALUESTRING", "String", "", 1),
    ("GDVALUEBOOL", "Bool", "", 2),
    ("GDVALUENONE", "None", "", 3),
    ("GDVALUEINT", "Int", "", 4),
    ("GDVALUEFLOAT", "Float", "", 5),
    ("GDVALUESTRINGNAME", "StringName", "", 6),
    ("GDVALUEARRAY", "Array", "", 7),
    ("GDVALUEVECTOR2", "Vector2", "", 8),
    ("GDVALUEVECTOR3", "Vector3", "", 9),
    ("GDVALUEVECTOR4", "Vector4", "", 10),
    ("GDVALUEVECTOR2I", "Vector2i", "", 11),
    ("GDVALUEVECTOR3I", "Vector3i", "", 12),
    ("GDVALUEVECTOR4I", "Vector4i", "", 13),
    ("GDVALUERECT2", "Rect2", "", 14),
    ("GDVALUERECT2I", "Rect2i", "", 15),
    ("GDVALUEPLANE", "Plane", "", 16),
    ("GDVALUECOLOR", "Color", "", 17),
    ("GDVALUEAABB", "AABB", "", 18),
    ("GDVALUEQUATERNION", "Quaternion", "", 19),
    ("GDVALUETRANSFORM2D", "Transform2D", "", 20),
    ("GDVALUEBASIS", "Basis", "", 21),
    ("GDVALUETRANSFORM3D", "Transform3D", "", 22),
    ("GDVALUEPACKEDBYTEARRAY", "PackedByteArray", "", 23),
    ("GDVALUEPACKEDINT32ARRAY", "PackedInt32Array", "", 24),
    ("GDVALUEPACKEDINT64ARRAY", "PackedInt64Array", "", 25),
    ("GDVALUEPACKEDFLOAT32ARRAY", "PackedFloat32Array", "", 26),
    ("GDVALUEPACKEDFLOAT64ARRAY", "PackedFloat64Array", "", 27),
    ("GDVALUEPACKEDSTRINGARRAY", "PackedStringArray", "", 28),
    ("GDVALUEPACKEDVECTOR2ARRAY", "PackedVector2Array", "", 29),
    ("GDVALUEPACKEDVECTOR3ARRAY", "PackedVector3Array", "", 30),
    ("GDVALUEPACKEDVECTOR4ARRAY", "PackedVector4Array", "", 31),
    ("GDVALUEPACKEDCOLORARRAY", "PackedColorArray", "", 32),
    ("GDVALUEDICTIONARY", "Dictionary", "", 33),
)

class BlPrimitives(bpy.types.PropertyGroup):
    _subtypes = ("String","Int","Float","Bool")
    name : bpy.props.StringProperty() #type:ignore

    subtype : bpy.props.EnumProperty(items=ITEMS, default="UNSET") #type:ignore

    @property
    def value(self,):
        return getattr(self, "val_"+self.subtype.lower(), _UNSET)
    @value.setter
    def value(self, value):
        getattr(self, "val_"+self.subtype.lower()) = value

    val_string : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_float : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore

class BlVectors():
    _subtypes = ("GdValueVector2","GdValueVector3","GdValueVector4","GdValueRect2","GdValuePlane","GdValueColor","GdValueAabb","GdValueQuaternion","GdValueBasis","GdValueTransform2d","GdValueTransform3d","GdValueVector2i","GdValueVector3i","GdValueVector4i","GdValueRect2i")
    name : bpy.props.StringProperty() #type:ignore
    subtype : bpy.props.EnumProperty(items=ITEMS, default="UNSET") #type:ignore

    @property
    def value(self,):
        return getattr(self, self.subtype.lower(), _UNSET)
    @value.setter
    def value(self, value):
        getattr(self, self.subtype) = value

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
    rect2i : bpy.prop.IntVectorProperty(size=4) #type:ignore

class BlDictionary(BlPointerDictionary):
    _subtypes = ("Dictionary")
    subtype : bpy.props.EnumProperty(items=ITEMS, default="Dictionary") #type:ignore
    
class BlArray(BlPointerArray):
    _subtypes = ("GdValueArray", "GdValuePackedByteArray","GdValuePackedInt32Array","GdValuePackedInt64Array","GdValuePackedFloat32Array","GdValuePackedFloat64Array","GdValuePackedStringArray","GdValuePackedVector2Array","GdValuePackedVector3Array","GdValuePackedVector4Array","GdValuePackedColorArray" )
    subtype : bpy.props.EnumProperty(items=ITEMS, default="Array") #type:ignore

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
        return self._bin_map[val.__class__.__name__]
        

_all = (
    BlPrimitives,
    BlVectors,
    BlDictionary,
    BlArray,
    BlPropertyCollection,
)