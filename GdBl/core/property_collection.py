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
            return
        raise KeyError(subtype, val)

    ##TODO: Draw


class GdArray(_BlPointerArray):
    _subtypes = ("Array", "PackedInt32Array", "PackedInt64Array", "PackedFloat32Array", "PackedFloat64Array", "PackedStringArray", "PackedVector2Array", "PackedVector3Array", "PackedVector4Array", "PackedColorArray", "PackedByteArray",)
    subtype : bpy.props.StringProperty(default="Array") #type:ignore
    typing : bpy.props.StringProperty() #type:ignore

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype
            return
        raise KeyError(subtype, val)

    ##TODO: Draw


class _GenericBinItem(bpy.types.PropertyGroup):
    _subtypes : tuple[str] = tuple()
    _cast_types : dict[str,callable] = {}
    subtype : bpy.props.StringProperty() #type:ignore
    _val_prefix : str = ""

    def _cast(self,v):
        self._set_subtype_fr_val(v)
        if hasattr(v,"typing"):
            self.typing = str(v.typing)
        if cast:=self._cast_types.get(self.subtype,None):
            return cast(v) 
        return v 

    def _set_subtype_fr_val(self,val):
        subtype = val.__class__.__name__
        if subtype in self._subtypes:
            self.subtype = subtype
            return
        raise KeyError(subtype, val)

    def set_value(self, val):
        self.value = val

    @property
    def value(self,):
        if (self.subtype == "None"):
            return None
        return getattr(self, self._val_prefix+self.subtype.lower())
    
    @value.setter
    def value(self, v):
        if v is None:
            self.subtype = "None"
            return
        self[self._val_prefix+self.subtype.lower()] = self._cast(v)
        # setattr(self, self._val_prefix+self.subtype.lower(), self._cast(v))

    def draw(self, layout):
        if self.subtype:
            layout.prop(self, self.subtype)
        else:
            pass

class GdReference(_GenericBinItem):
    _subtypes = ("ExtResourceRef", "SubResourceRef", "RID", "ResourceRef")
    _caster = lambda x: x.cached_addr
    _cast_types = {"ExtResourceRef":_caster, "SubResourceRef":_caster, "RID":_caster, "ResourceRef":_caster}

    typing : bpy.props.StringProperty() #type:ignore

    val_str : bpy.props.StringProperty() #type:ignore

    @property
    def value(self,):
        if (self.subtype == "None"):
            return None
        return getattr(self, "val_str")
    
    @value.setter
    def value(self, v):
        if v is None:
            self.subtype = "None"
            return
        self["val_str"] = self._cast(v)


class GdPrimitive(_GenericBinItem):
    _subtypes = ("NodePath","StringName", "str", "int", "float", "bool", "None")
    _cast_types = {"NodePath":str, "StringName":str}
    _val_prefix = "val_"

    val_nodepath : bpy.props.StringProperty() #type:ignore
    val_stringname : bpy.props.StringProperty() #type:ignore
    val_str : bpy.props.StringProperty() #type:ignore
    val_int : bpy.props.IntProperty() #type:ignore
    val_float : bpy.props.FloatProperty() #type:ignore
    val_bool : bpy.props.BoolProperty() #type:ignore
    val_none = None


class GdVector(_GenericBinItem):
    _subtypes = ("Vector2", "Vector3", "Vector4", "Rect2", "Plane", "Color", "AABB", "Quaternion", "Basis", "Transform2D", "Transform3D", "Vector2i", "Vector3i", "Vector4i", "Rect2i")
    
    def _cast(self,v):
        self._set_subtype_fr_val(v)
        return tuple(v)
         

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

    