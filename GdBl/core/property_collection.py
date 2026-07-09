from __future__ import annotations
import bpy

from .primitives.pointer_collection import (
    PointerCollection as _PointerCollection, 
    BlPointerDictionary as _BlPointerDictionary, 
    BlPointerArray as _BlPointerArray,
)

class GdPropertyCollection(_PointerCollection):    
    _bins = ("bin_array", "bin_dict", "bin_vector", "bin_primitive", "bin_reference")

    bin_dict : bpy.props.CollectionProperty(type=GdDictionary) #type:ignore
    bin_array : bpy.props.CollectionProperty(type=GdArray) #type:ignore

    bin_primitive : bpy.props.CollectionProperty(type = GdPrimitive) #type:ignore
    bin_vector : bpy.props.CollectionProperty(type = GdVector) #type:ignore
    bin_reference : bpy.props.CollectionProperty(type= GdReference) #type:ignore

    def _bin_val_matcher(self, val):
        ty = val.__class__
        tyname = ty.__name__
        for b, name in ((getattr(self,x),x) for x in self._bins):
            if (tyname in b._subtypes) or (ty in b._subtypes):
                return name 
        return super()._bin_val_matcher(val)
    
    ##TODO: Draw


class GdDictionary(_BlPointerDictionary):
    _subtypes = ("Dictionary", "Object")
    subtype : bpy.props.StringProperty(default="Dictionary") #type:ignore
    typing : bpy.props.StringProperty() #type:ignore
    objtype : bpy.props.StringProperty() #type:ignore

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype

    ##TODO: Draw


class GdArray(_BlPointerArray):
    _subtypes = ("Array", "PackedInt32Array", "PackedInt64Array", "PackedFloat32Array", "PackedFloat64Array", "PackedStringArray", "PackedVector2Array", "PackedVector3Array", "PackedVector4Array", "PackedColorArray", "PackedByteArray",)
    subtype : bpy.props.StringProperty(default="Array") #type:ignore
    typing : bpy.props.StringProperty() #type:ignore

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype

    ##TODO: Draw

class GdReference(bpy.types.PropertyGroup):
    _subtypes = ("ExtResourceRef", "SubResourceRef", "RID", "ResourceRef")
    typing : bpy.props.StringProperty() #type:ignore
    subtype : bpy.props.StringProperty() #type:ignore

    val_str : bpy.props.StringProperty() #type:ignore

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype

    @property
    def value(self, v):
        self._set_subtype_fr_val(v)
        self.val_str = v
    @value.getter
    def value(self,):
        return self.val_str

    def draw(self, layout):
        if self.subtype:
            layout.prop(self, self.subtype)
        else:
            pass


class GdPrimitive(bpy.types.PropertyGroup):
    _subtypes = ("NodePath","StringName", "str", "int", "float", "bool", "None")
    subtype : bpy.props.StringProperty() #type:ignore

    val_nodepath : bpy.props.StringProperty() #type:ignore
    val_stringname : bpy.props.StringProperty() #type:ignore
    val_str : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_float : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore
    val_none = None

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype

    @property
    def value(self, v):
        self._set_subtype_fr_val(v)
        if v is None: return
        setattr(self, "val_"+self.subtype.lower(), v)
    @value.getter
    def value(self,):
        return getattr(self, "val_"+self.subtype.lower())

    def draw(self, layout):
        if self.subtype:
            layout.prop(self, self.subtype)
        else:
            pass

class GdVector(bpy.types.PropertyGroup):
    _subtypes = ("Vector2", "Vector3", "Vector4", "Rect2", "Plane", "Color", "AABB", "Quaternion", "Basis", "Transform2D", "Transform3D", "Vector2i", "Vector3i", "Vector4i", "Rect2i")
    subtype : bpy.props.StringProperty() #type:ignore
    
    vector2 : bpy.props.FloatVectorProperty(size = 2) #type:ignore
    vector3 : bpy.props.FloatVectorProperty(size = 3) #type:ignore
    vector4 : bpy.props.FloatVectorProperty(size = 4) #type:ignore
    rect2 : bpy.props.FloatVectorProperty(size = 4) #type:ignore
    plane : bpy.props.FloatVectorProperty(size = 4) #type:ignore
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

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype

    @property
    def value(self, v):
        self._set_subtype_fr_val(v)
        setattr(self, self.subtype.lower(), v)
    @value.getter
    def value(self,):
        return getattr(self, self.subtype.lower())

    def draw(self, layout):
        if self.subtype:
            layout.prop(self, self.subtype)
        else:
            pass


from .primitives.pointer_collection import (
    BlPointerDictionaryItem as _BlPointerDictionaryItem, 
    BlPointerArrayItem as _BlPointerArrayItem,
    BlPropertyItem as _BlPropertyItem,
)

_all = (
    _BlPropertyItem,
    _BlPointerDictionaryItem,
    _BlPointerArrayItem,
    GdPrimitive,
    GdVector,
    GdReference,
    GdDictionary,
    GdArray,
    GdPropertyCollection,
)

def register():
    for c in _all:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_all):
        bpy.utils.unregister_class(c)

    