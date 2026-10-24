from __future__ import annotations

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, EnumProperty, PointerProperty, FloatProperty, FloatVectorProperty, IntVectorProperty
from bpy.types import AddonPreferences, PropertyGroup, UILayout, Context, Operator

from typing import Any, Type, Iterable

from string import ascii_letters
from random import sample

from ..GdPy.core.structure import (
    Promise as GdPromise
)
from ..GdPy.core.values import (
    Array as GdArray,
    Dictionary as GdDictionary,
    NodePath as GdNodePath,
    _FixedLenArray as GdFixedLenArray,
    _PackedListSimple as GdPackedListSimple,
    _PackedListComplex as GdPackedListComplex,
    StringName as GdStringName,
    Object as GdObject,
    Vector2i as GdVector2i,
    Vector3i as GdVector3i,
    Vector4i as GdVector4i,
    Rect2i as GdRect2i,
    Vector2 as GdVector2,
    Vector3 as GdVector3,
    Vector4 as GdVector4,
    Rect2 as GdRect2,
    Plane as GdPlane,
    Color as GdColor,
    AABB as GdAABB,
    Quaternion as GdQuaternion,
    Transform2D as GdTransform2D,
    Transform3D as GdTransform3D,
    Basis as GdBasis,
    PackedByteArray as GdPackedByteArray,
    PackedInt32Array as GdPackedInt32Array,
    PackedInt64Array as GdPackedInt64Array,
    PackedFloat32Array as GdPackedFloat32Array,
    PackedFloat64Array as GdPackedFloat64Array,
    PackedStringArray as GdPackedStringArray,
    PackedVector2Array as GdPackedVector2Array,
    PackedVector3Array as GdPackedVector3Array,
    PackedVector4Array as GdPackedVector4Array,
    PackedColorArray as GdPackedColorArray, 
)



from collections import UserDict, UserList, UserString


class Promise(PropertyGroup):
    p_type : EnumProperty(items = [
        ("SUBRESOURCE","subresource",""),
        ("EXTRESOURCE","extresource",""),
        ("EXTRESOURCE_DIRECT","extresource_direct",""), #Refereing to promise in scope, W/out address, uid, ect
        ("RID","rid",""),
    ]) #type:ignore
    id : StringProperty() #type:ignore
    uid : StringProperty() #type:ignore
    filepath : StringProperty() #type:ignore

    ptr_col : PointerProperty(type=bpy.types.Collection) #type:ignore
    ptr_obj : PointerProperty(type=bpy.types.Object) #type:ignore
    ptr_tex : PointerProperty(type=bpy.types.Texture) #type:ignore
    ptr_img : PointerProperty(type=bpy.types.Image) #type:ignore
    ptr_mat : PointerProperty(type=bpy.types.Material) #type:ignore
    ptr_txt : PointerProperty(type=bpy.types.Text) #type:ignore
    ptr_scn : PointerProperty(type=bpy.types.Scene) #type:ignore
    ptr_snd : PointerProperty(type=bpy.types.Sound) #type:ignore
    ptr_lgt : PointerProperty(type=bpy.types.Light) #type:ignore
    ptr_cam : PointerProperty(type=bpy.types.Camera) #type:ignore
    ptr_mesh : PointerProperty(type=bpy.types.Mesh) #type:ignore
    ptr_clip : PointerProperty(type=bpy.types.Action) #type:ignore
    ptr_curv : PointerProperty(type=bpy.types.Curve) #type:ignore
    ptr_geon : PointerProperty(type=bpy.types.NodeTree) #type:ignore
    ptr_wrld : PointerProperty(type=bpy.types.World) #type:ignore
    # ptr_anim : PointerProperty(type=bpy.types.AnimData) #type:ignore
    
class UNSET:pass
class UNSETALT:pass


class PropertyWrapper[PROPERTY]():
    ''' Wrapped interface, returned by PropertyBin on get/set w/a '''
    _type : Type[PROPERTY]
    _property : PROPERTY
    _properties : Any

    def __init__(self, properties, property:PROPERTY):
        self._property = property
        self._properties = properties

    @property
    def name(self):
        return self._property.name
    @name.setter
    def name(self, val):
        self._property.name = val

    def __eq__(self, val):
        return self.property == val

class Property[IN:Any](PropertyGroup):
    wrapper : Type = None
    name : StringProperty(name="pointer") #type:ignore

    def store(self, properties, val:IN)->None:
        ''' Store value and any dependencies stored in Properties '''
        raise NotImplementedError()
    
    def dump(self, properties): 
        ''' Dump any related values from src properties obj '''

    def __eq__(self, obj:Any):
        if isinstance(obj, PropertyWrapper):
            return self == obj._property
        else:
            return super().__eq__(obj)


class PropertyBin[IN:Any, OUT:Property|PropertyWrapper[Property]](PropertyGroup):
    ''' data container that acts as an interface for accessing and wrapping data stored in local .data'''
    in_types : tuple[Type] 
    wrapper : None|Type[PropertyWrapper] = None
    data : CollectionProperty #type:ignore

    def matches_type(self, data:Any|IN)->bool:
        return isinstance(data, self.in_types)

    def get(self, /, properties:PropertiesBase, ptr:str, default:Any=UNSET, wrap:bool=True)->OUT:
        entry = self.data.get(ptr, UNSET)
        if entry is UNSET:
            if default is UNSET:
                raise KeyError(self, ptr)
            return default
        if wrap and self.wrapper:
            return self.wrapper(properties, entry)
        return entry

    def add(self, /, properties:PropertiesBase, value:IN, wrap:bool=True)->OUT:
        return self.set(properties, properties.generate_pointer(), value, wrap)
    
    def set(self, /, properties:PropertiesBase, ptr:str, value:IN, wrap:bool=True)->OUT:
        entry = self.data.add()
        entry.name = ptr
        entry.store(properties, value)
        if wrap and self.wrapper:
            return self.wrapper(properties, entry)
        return entry

    def remove(self, /, properties:PropertiesBase, ptr:str, not_exist_ok:bool=False):
        entry = self.data.get(ptr, UNSET)
        if entry is UNSET:
            if not not_exist_ok:
                raise KeyError(self, ptr)
            return
        
        index = tuple(self.data.keys()).index(ptr)
        entry.dump(properties)
        self.data.remove(index)

    def __contains__(self, ptr:str)->bool:
        return (ptr in self.data.keys()) 

class PropertiesEntry(PropertyGroup):
    name : StringProperty() #type:ignore
    ptr : StringProperty() #type:ignore

class PropertiesBase[OUT:Property|PropertyWrapper[Property]](PropertyGroup):
    ''' Dict-like using "bins" to store values ''' 
    _bins : tuple[str] = tuple()

    data : CollectionProperty(type=PropertiesEntry) #type:ignore
    
    def generate_pointer(self)->str:
        keys = tuple(self.keys())
        ptr = "".join(sample(ascii_letters,5))
        while ptr in keys:
            ptr = "".join(sample(ascii_letters,5))
        return ptr

    ## DICT INTERFACE:

    def get(self, /, key:str, default:Any=UNSET, wrap:bool=True)->OUT:
        entry = self.data.get(key, None)
        if entry is None:
            if default is UNSET:
                raise KeyError(key)
            return default
        return self.bin_get(entry.ptr, default, wrap)

    def set(self, /, key:str, value:Any, wrap:bool=True)->OUT:
        val = self.bin_add(value, wrap)
        entry = self.data.get(key, None)
        if entry is None:
            entry = self.data.add()
            entry.name = key 
        else:
            self.bin_remove(entry.ptr, not_exist_ok = True)
        entry.ptr = val.name
        return val

    def remove(self, /, key:str, not_exist_ok:bool=False):
        entry = self.data.get(key, None)
        if entry is None:
            if not not_exist_ok:
                raise KeyError(key)
            return 
        self.bin_remove(entry.ptr, not_exist_ok=not_exist_ok)
        self.data.remove(tuple(self.data.keys()).index(key))

    def __contains__(self, key):
        return (key in self.data.keys()) or (key in self.data.values())

    def keys(self):
        yield from self.data.keys()
    
    def values(self, wrap:bool=True):
        for _,v in self.items(wrap):
            yield v
    
    def items(self, wrap:bool=True):
        for e in self.data.values():
            yield e.name, self.bin_get(e.ptr, None, wrap)

    def clear(self):
        for b in self.bins():
            b.data.clear()
        self.data.clear()

    ## PTR/DATA HANDLING:

    def bins(self):
        for k in self._bins:
            yield getattr(self, k)

    def bin_get(self, /, key:str, default:Any=UNSET, wrap:bool=True)->OUT:
        for b in self.bins():
            res = b.get(self, key, wrap=wrap, default=UNSETALT)
            if not (res is UNSETALT):
                return res
        if default is UNSET:
            raise KeyError(key)
        return default
            
    def bin_add(self, value:Any, wrap:bool=False):
        _bin = None
        for b in self.bins():
            if b.matches_type(value):
                _bin = b
                break
        if _bin is None:
            raise TypeError(self, value)
        value = _bin.add(self, value, wrap)
        return value

    def bin_remove(self, /, ptr:str, not_exist_ok:bool=False):
        for b in self.bins():
            if ptr in b:
                b.remove(self, ptr)
                return
        if not not_exist_ok:
            raise KeyError(ptr)
        return



## IMPLEMENTATION ##

## BASIC:
class PropertyString(Property):
    _subtypes = {
        GdNodePath.__name__ : GdNodePath,
        GdStringName.__name__ : GdStringName,
    }
    subtype : StringProperty() #type:ignore
    value_store : StringProperty() #type:ignore
    typing : StringProperty() #type:ignore

    @property
    def value(self):
        if (self.subtype != ""):
            return self._subtypes[self.subtype](self.value_store)
        return self.value_store
    @value.setter
    def value(self, val):
        if val.__class__.__name__ in self._subtypes.keys():
            self.subtype = val.__class__.__name__
        self.value_store = str(val)
    
    def store(self, properties, val):
        self.value = val

class PropertyBinString(PropertyBin):
    in_types = (str, UserString, GdNodePath, GdStringName)
    data : CollectionProperty(type=PropertyString) #type:ignore


class PropertyInt(Property):
    subtype : StringProperty() #type:ignore
    value : IntProperty() #type:ignore
    def store(self, properties, val):
        self.value = val
class PropertyBinInt(PropertyBin):
    in_types = (int, )
    data : CollectionProperty(type=PropertyInt) #type:ignore


class PropertyFloat(Property):
    subtype : StringProperty() #type:ignore
    value : FloatProperty() #type:ignore
    def store(self, properties, val):
        self.value = val
class PropertyBinFloat(PropertyBin):
    in_types = (float, )
    data : CollectionProperty(type=PropertyFloat) #type:ignore


class PropertyVector(Property):
    _subtypes = {
        GdVector2i.__name__.lower() : GdVector2i,
        GdVector3i.__name__.lower() : GdVector3i,
        GdVector4i.__name__.lower() : GdVector4i,
        GdRect2i.__name__.lower() : GdRect2i,
        GdVector2.__name__.lower() : GdVector2,
        GdVector3.__name__.lower() : GdVector3,
        GdVector4.__name__.lower() : GdVector4,
        GdRect2.__name__.lower() : GdRect2,
        GdPlane.__name__.lower() : GdPlane,
        GdColor.__name__.lower() : GdColor,
        GdAABB.__name__.lower() : GdAABB,
        GdQuaternion.__name__.lower() : GdQuaternion,
        GdTransform2D.__name__.lower() : GdTransform2D,
        GdTransform3D.__name__.lower() : GdTransform3D,
        GdBasis.__name__.lower() : GdBasis,
    }

    subtype : EnumProperty(items=((k.lower(),k,"") for k,v in _subtypes.items()))#type:ignore
    vector2i : IntVectorProperty(size=2) #type:ignore
    vector3i : IntVectorProperty(size=3) #type:ignore
    vector4i : IntVectorProperty(size=4) #type:ignore
    rect2i : IntVectorProperty(size=4) #type:ignore
    vector2 : FloatVectorProperty(size=2) #type:ignore
    vector3 : FloatVectorProperty(size=3) #type:ignore
    vector4 : FloatVectorProperty(size=4) #type:ignore
    rect2 : FloatVectorProperty(size=4) #type:ignore
    plane : FloatVectorProperty(size=4) #type:ignore
    color : FloatVectorProperty(size=4, subtype="COLOR") #type:ignore
    aabb : FloatVectorProperty(size=6) #type:ignore
    quaternion : FloatVectorProperty(size=4, subtype="QUATERNION") #type:ignore
    transform2d : FloatVectorProperty(size=6) #type:ignore
    transform3d : FloatVectorProperty(size=12) #type:ignore
    basis : FloatVectorProperty(size=9) #type:ignore

    def store(self, properties, val):
        self.value = val

    @property
    def value(self):
        cls = self._subtypes[self.subtype]
        return cls(*getattr(self, str(self.subtype).lower()))
    @value.setter
    def value(self, val):
        self.property_unset(self.subtype)
        self.subtype = val.__class__.__name__.lower()
        assert self.subtype in self._subtypes.keys()
        try:
            setattr(self, self.subtype, tuple(val))
        except Exception as e:
            raise Exception(val, e)

class PropertyBinVector(PropertyBin):
    in_types = (GdFixedLenArray)
    data : CollectionProperty(type=PropertyVector) #type:ignore

class PropertyPromise(Property):
    typing : StringProperty() #type:ignore
    data : PointerProperty(type=Promise) #type:ignore
class PropertyBinPromise(PropertyBin):
    in_types = (GdPromise,Promise)
    data : CollectionProperty(type=PropertyPromise) #type:ignore


## DICT GROUP

class PropertyDictItem(Property):
    name : StringProperty() #type:ignore
    # key_ptr : StringProperty() #type:ignore
    val_ptr : StringProperty() #type:ignore

    def get_value(self, properties, wrap:bool=False):
        return properties.bin_get(self.val_ptr, wrap=wrap)
    def set_value(self, properties, value:Any, wrap:bool=False):
        properties.bin_remove(self.val_ptr, not_exist_ok=True)
        return properties.bin_add(value, wrap)

    def get_key(self, properties, wrap:bool=False):
        return properties.bin_get(self.name, wrap=wrap)
    def set_key(self, properties, value:Any, wrap:bool=False):
        properties.bin_remove(self.name, not_exist_ok=True)
        return properties.bin_add(value, wrap)

class PropertyDictItemWrapper(PropertyWrapper):
    @property
    def key(self): 
        return self._property.get_key(self._properties, wrap=True)
    @key.setter
    def key(self, key):
        self._property.set_key(self._properties, key)

    @property
    def value(self): 
        return self._property.get_value(self._properties, wrap=True)
    @value.setter
    def value(self, value):
        self._property.set_value(self._properties, value)
        
class PropertyDict(Property, PropertyBin):
    typing : StringProperty() #type:ignore
    data : CollectionProperty(type=PropertyDictItem) #type:ignore
    wrapper = PropertyDictItemWrapper


    def store(self, properties, val:Iterable):
        self.update(properties, val.items())

    def dump(self, properties):
        self.clear(properties)

    def get(self, properties:PropertiesBase, key:Any, default:Any=UNSET, wrap:bool=True):
        for k,v in self.items(properties, wrap=True):
            if k != key:
                continue
            if isinstance(v, PropertyWrapper) and not wrap:
                return v._property
            return v
        if default is UNSET:
            raise KeyError(key)
        return default

    def setitem(self, properties:PropertiesBase, key:Any, value:Any, wrap:bool=True):
        existing_val = self.get(properties, key,default=None,wrap=False)
        if not (existing_val is None):
            properties.bin_remove(self.data[existing_val.name].val_ptr, not_exist_ok = True)
        else:
            existing_val = self.data.add()
            _key = properties.bin_add(key, wrap=False)
            existing_val.name = _key.name
        val = properties.bin_add(value, wrap=True)
        existing_val.val_ptr = val.name
        if isinstance(val, PropertyWrapper) and not wrap:
            return val._property
        return val

    def delitem(self, properties:PropertiesBase, key:Any, not_exist_ok:bool=False):
        for k, v in self.items(wrap=True):
            if k != key:
                continue
            self._property.data.remove(k.name)
            return
        if not not_exist_ok:
            raise KeyError(key)
        return

    def update(self, properties:PropertiesBase, seq:Iterable):
        for k,v in seq:
            self.setitem(properties, k, v)
    
    def item_pointers(self):
        for e in self.data:
            yield e.name, e.val_ptr
    
    def items(self, properties:PropertiesBase, wrap:bool=True):
        for key_ptr, val_ptr in self.item_pointers():
            yield properties.bin_get(key_ptr, wrap=wrap), properties.bin_get(val_ptr, wrap=wrap)
    
    def keys(self, properties:PropertiesBase, wrap:bool=True):
        for e in self.data:
            yield properties.bin_get(e.key_ptr, wrap=wrap)
    
    def values(self, properties:PropertiesBase, wrap:bool=True):
        for e in self.data:
            yield properties.bin_get(e.val_ptr, wrap=wrap)

    def clear(self, properties):
        for e in self.data:
            properties.bin_remove(e.name, not_exist_ok=True)
            properties.bin_remove(e.val_ptr, not_exist_ok=True)

class PropertyDictWrapper(PropertyWrapper):
    def get(self, key:Any, default:Any=UNSET, wrap:bool=True):
        return self._property.get(self._properties, key, default, wrap)
    def store(self, val):
        return self._property.store(self._properties, val)
    def update(self, val):
        return self._property.update(self._properties, val)
    def remove(self, key:Any):
        return self._property.remove(self._properties, key)
    def setitem(self, key:int, val):
        return self._property.setitem(self._properties, key, val)
    def delitem(self, key):
        return self._property.delitem(self._properties)
    def values(self, wrap:bool=True):
        yield from self._property.values(self._properties, wrap=wrap)
    def keys(self, wrap:bool=True):
        yield from self._property.keys(self._properties, wrap=wrap)
    def items(self, wrap:bool=True):
        yield from self._property.items(self._properties, wrap=wrap)
    
class PropertyBinDict(PropertyBin):
    in_types = (dict, GdDictionary, UserDict, GdObject)
    data : CollectionProperty(type=PropertyDict) #type:ignore
    wrapper = PropertyDictWrapper


## ARRAY GROUP

class PropertyArrayItem(Property):
    ptr : StringProperty() #type:ignore
    def get_data(self, properties, wrap:bool=False):
        return properties.bin_get(self.ptr , wrap=wrap)
    def set_data(self, properties, value:Any, wrap:bool=False):
        properties.bin_remove(self.ptr , not_exist_ok=True)
        return properties.bin_add(value, wrap)
    
class PropertyArrayItemWrapper(PropertyWrapper):
    @property
    def data(self): 
        return self._property.get_data(self._properties, wrap=True)
    @data.setter
    def data(self, data):
        self._property.set_data(self._properties, data)

class PropertyArray(Property):
    typing : StringProperty() #type:ignore
    data : CollectionProperty(type=PropertyArrayItem) #type:ignore
    wrapper = PropertyArrayItemWrapper

    subtype : StringProperty() #type:ignore
    _subtypes = {
        GdPackedInt32Array.__name__.lower(): GdPackedInt32Array,
        GdPackedInt64Array.__name__.lower(): GdPackedInt64Array,
        GdPackedFloat32Array.__name__.lower(): GdPackedFloat32Array,
        GdPackedFloat64Array.__name__.lower(): GdPackedFloat64Array,
        GdPackedStringArray.__name__.lower(): GdPackedStringArray,
        GdPackedVector2Array.__name__.lower(): GdPackedVector2Array,
        GdPackedVector3Array.__name__.lower(): GdPackedVector3Array,
        GdPackedVector4Array.__name__.lower(): GdPackedVector4Array,
        GdPackedColorArray.__name__.lower(): GdPackedColorArray,
    }

    def value(self, properties:PropertiesBase)->Any:
        if self.subtype != "":
            return self._subtypes[self.subtype](*self.values(properties))
        return GdArray(*self.values(properties), type=self.typing)
        
        
    def store(self, properties:PropertiesBase, val):
        if (clsname:=val.__class__.__name__.lower()) in self._subtypes.keys():
            self.subtype = clsname
        else:
            self.subtype = ""
        self.clear(properties)
        self.extend(properties, val)

    def dump(self, properties:PropertiesBase):
        self.clear(properties)

    def append(self, properties:PropertiesBase, val:Any):
        v = properties.bin_add(val)
        e = self.data.add()
        e.name = v.name

    def extend(self, properties, val):
        for v in val:
            self.append(properties, v)
    
    def remove(self, properties:PropertiesBase, val:Any):
        for e in tuple(self.data):
            if properties.bin_get(e.name) == val:
                self.data.remove(e)
                properties.bin_remove(e.name)
                return

    def setitem(self, properties:PropertiesBase, index:int, val):
        if len(self.data) < index:
            raise KeyError(self.data, index)
        v = properties.bin_add(val)
        tuple(self.data.keys())[index].ptr = v.name

    def delitem(self, properties:PropertiesBase, index):
        if len(self.data) < index:
            raise KeyError(self.data, index)
        e = tuple(self.data.keys())[index]
        properties.bin_remove(e.name)
        self.data.remove(e)
        
    def clear(self, properties):
        for e in self.data:
            properties.bin_remove(e.name, not_exist_ok=True)

    def values(self, properties:PropertiesBase, wrap:bool=True):
        for e in tuple(self.data):
            yield properties.bin_get(e.name, wrap=True)

class PropertyArrayWrapper(PropertyWrapper):
    @property

    def value(self):
        return GdArray(*self.values(),typing = self._property.typing)
    @value.setter
    def value(self, val:Iterable):
        self._property.clear(self._properties)
        self._property.store(self._properties, val)

    def store(self, val):
        return self._property.store(self._properties, val)
    def append(self, val:Any):
        return self._property.append(self._properties, val)
    def extend(self, val):
        return self._property.extend(self._properties, val)
    def remove(self, val:Any):
        return self._property.remove(self._properties, val)
    def setitem(self, index:int, val):
        return self._property.setitem(self._properties, index, val)
    def delitem(self, index):
        return self._property.delitem(self._properties, index)
    def values(self, wrap:bool=True):
        yield from self._property.values(self._properties, wrap=wrap)
    def clear(self):
        return self._property.clear(self._properties)

class PropertyBinArray(PropertyBin):
    in_types = (GdArray, list, UserList, GdPackedListSimple, GdPackedListComplex)
    data : CollectionProperty(type=PropertyArray) #type:ignore
    wrapper = PropertyArrayWrapper


class PropertyBinary(Property):
    ''' Store bytes objects in utf8 in text objects, no other way to keep in file currently known. 
    *Generally* should not be used, most objects should have binary data incorperated into blender equiv.
    '''
    data_store : PointerProperty(type=bpy.types.Text) #type:ignore    
    @property
    def data(self)->bytes:
        if self.data_store:
            return self.data_store.text.encode("utf-8")
    @data.setter
    def data(self, val:bytes|None):
        if not (val is None):
            if self.data_store is None:
                self.data_store = bpy.data.texts.new()
                self.data_store.name = self.name+".utf8.bin"
            self.data_store.text = val.encode("utf-8")
        if (val is None) and (not (self.data_store is None)):
            bpy.data.texts.remove(self.data_store.name)

    def store(self, val):
        self.data = val

    def dump(self):
        self.data = None

class PropertyBinBinary(PropertyBin):
    in_types = (GdPackedByteArray, bytes, bytearray)
    data : CollectionProperty(type=PropertyBinary) #type:ignore

class Properties(PropertiesBase):
    ''' dict-like object using local bins for "variant" allowences 
    Currently all objects are unique and not user-count tracked

    Future plans will store large strings in text data blocks, 
    bytes objects *are* suppported but generally binary data should have an incorperated type
    '''

    _bins = ["bin_int", "bin_float", "bin_string", "bin_binary", "bin_dict", "bin_vector", "bin_array", "bin_promises"]
    ## _bins also doubles as priority of match. 
    bin_string : PointerProperty(type=PropertyBinString) #type:ignore
    bin_float : PointerProperty(type=PropertyBinFloat) #type:ignore
    bin_int : PointerProperty(type=PropertyBinInt) #type:ignore
    bin_promises : PointerProperty(type=PropertyBinPromise) #type:ignore
    bin_dict : PointerProperty(type=PropertyBinDict) #type:ignore
    bin_array : PointerProperty(type=PropertyBinArray) #type:ignore
    bin_vector : PointerProperty(type=PropertyBinVector) #type:ignore
    bin_binary : PointerProperty(type=PropertyBinBinary) #type:ignore

classes = [
    Promise,
    PropertyString,
    PropertyInt,
    PropertyFloat,
    PropertyVector,
    PropertyPromise,
    PropertyDictItem,
    PropertyDict,
    PropertyBinary,
    PropertyArrayItem,
    PropertyArray,
    PropertyBinString,
    PropertyBinInt,
    PropertyBinFloat,
    PropertyBinPromise,
    PropertyBinDict,
    PropertyBinArray,
    PropertyBinVector,
    PropertyBinBinary,
    PropertiesEntry,
    Properties,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        for l,n in getattr(c, "attach", tuple()):
            setattr(l, n, PointerProperty(type=c))
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        for l,n in reversed(getattr(c, "attach", tuple())):
            delattr(l, n)