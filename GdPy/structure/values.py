from __future__ import annotations
from .core import GdResource, GdType, GdValue, Signal, SignalContainer
from typing import Self, Type, Any, Iterable
from lark import Token #type: ignore 
from array import array


class GdValueStringName(GdValue):
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("STRINGNAME",)

    @classmethod
    def parse_lark(cls, key:str, tfm, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"&')
        return inst
        
    def set_value(self, value):
        self.value = str(value)

class GdValueArray(GdValue):
    value : list
    types : tuple[Type[GdValue|Any]]

    item_appended : Signal
    item_removed : Signal
    
    def __init__(self, val:Any=None, types:tuple=None):
        if not (types is None):
            self.types = types
        if val != None:
            self.set_value(val)
        else:
            self.value = []
        super().__init__()

    def set_types(self, types:tuple[Type[GdValue|Any]]):
        self.types = types

    def set_value(self, value):
        self.value = []
        for x in value:
            self.append(x)

    def append(self, item:Any):
        if self.types:
            assert(isinstance(item,self.types))
        self.value.append(item)
        self.item_appended(item)
        
    def remove(self, item:Any):
        self.value.remove(item)
        self.item_removed(item)

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("array","array_explicit")
    
    @classmethod
    def parse_lark(cls, key:str, *args, **kwargs)->Any:
        if key == "array":
            return cls._parse_implicit(*args, **kwargs)
        elif key == "array_explicit":
            return cls._parse_explicit(*args, **kwargs)
        else:
            raise Exception("Could not determine key", key)

    @classmethod
    def _parse_explicit(cls, tfm, key, int_array:GdValueArray):
        if int_array is None:
            return cls()
        return int_array
    
    @classmethod
    def _parse_implicit(cls, tfm, *children:list[Token|Any]):
        inst = cls()
        inst.value = children
        return inst
    
    def __iter__(self,):
        return self.value.__iter__()

    def __eq__(self, other)->bool:
        if hasattr(other,"__iter__"):
            return self.value == other
        return False

class _GdValueArrayFixedType(GdValue):
    value : list

    def __init__(self, value:Iterable=None):
        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.value = list()
        else:
            self.value = list(*value)

    @classmethod
    def parse_lark(cls, key:str, tf, *args)->Any:
        if args == (None,):
            return cls()
        return cls(args)
    
    def __iter__(self,):
        return self.value.__iter__()
    
    def __eq__(self, other)->bool:
        if hasattr(other,"__iter__"):
            return self.value == other
        return False

class _GdValueArrayFixedLength(GdValue):
    value : array
    _arr_type : str = "f"
    _arr_length : int = 0

    def __init__(self, val:Any=None):
        if (val is None):
            self.def_value()
        else:
            self.set_value(val)

    def def_value(self,):
        self.value = array(self._arr_type, [0]*self._arr_length)

    def set_value(self, value:Iterable):
        assert(len(value)==self._arr_length)
        self.value = array(self._arr_type, value)

    @classmethod
    def parse_lark(cls, key:str, tf, *args)->Any:
        if (len(args)==0) or (args == (None,)) or (args == ((None,)*cls._arr_length)):
            return cls()
        assert(len(args) == cls._arr_length)
        return cls(args)
    
    def __iter__(self,):
        return self.value.__iter__()
    
    def __eq__(self, other)->bool:
        if hasattr(other,"__iter__"):
            return self.value == other
        return False
    
class GdValueVector2(_GdValueArrayFixedLength):
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 2
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector2",)
class GdValueVector3(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 3
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector3",)
class GdValueVector4(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector4",)
class GdValueVector2i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 2
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector2i",)
class GdValueVector3i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 3
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector3i",)
class GdValueVector4i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("vector4i",)
class GdValueRect2(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("rect2",)
class GdValueRect2i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("rect2i",)
class GdValuePlane(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "f"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("plane",)
class GdValueColor(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("color",)
class GdValueAABB(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 6
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("aabb",)
class GdValueQuaternion(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 4
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("quaternion",)
class GdValueTransform2D(_GdValueArrayFixedLength):
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 6
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("transform2d",)
class GdValueBasis(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 9
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("basis",)
class GdValueTransform3D(_GdValueArrayFixedLength): 
    types = (float,)
    _arr_type : str = "f"
    _arr_length : int = 12
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("transform3d",)



class GdValuePackedByteArray(_GdValueArrayFixedType): 
    types = (int,str)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedbytearray",)
class GdValuePackedInt32Array(_GdValueArrayFixedType): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedint32array",)
class GdValuePackedInt64Array(_GdValueArrayFixedType): 
    types = (int,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedint64array",)
class GdValuePackedFloat32Array(_GdValueArrayFixedType): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedfloat32array",)
class GdValuePackedFloat64Array(_GdValueArrayFixedType): 
    types = (int,float)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedfloat64array",)
class GdValuePackedStringArray(_GdValueArrayFixedType): 
    types = (str,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedstringarray",)
class GdValuePackedVector2Array(_GdValueArrayFixedType): 
    types = (GdValueVector2,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedvector2array",)
class GdValuePackedVector3Array(_GdValueArrayFixedType): 
    types = (GdValueVector3,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedvector3array",)
class GdValuePackedVector4Array(_GdValueArrayFixedType): 
    types = (GdValueVector4,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedvector4array",)
class GdValuePackedColorArray(_GdValueArrayFixedType): 
    types = (GdValueColor,)
    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("packedcolorarray",)


class GdValueDictionary(GdValue):
    value : dict
    types : tuple[Type]

    def __init__(self, value:list[tuple]|dict=None, types:tuple[Type]=None):
        if types:
            self.set_type(types)

        if (value is None):
            self.def_value()
        elif hasattr(value, "items"):
            self.set_value(value)
        elif hasattr(value, "__iter__"):
            self.def_value()
            for v in value:
                self.value[v[0]] = v[1]
        else:
            raise TypeError("Could not construct from type", value.__class__)

        if types:
            self.check_types()

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("dictionary","dictionary_explicit")
    
    def set_value(self, value):
        self.value = value
    def def_value(self):
        self.value = {}
    def set_type(self, types):
        self.types = types

    def check_types(self):
        pass

    def check_type(self):
        ##TODO
        pass

    @classmethod
    def parse_lark(cls, key:str, *args, **kwargs)->Any:
        if key == "dictionary":
            return cls._parse_implicit(*args, **kwargs)
        elif key == "dictionary_explicit":
            return cls._parse_explicit(*args, **kwargs)
        else:
            raise Exception("Cannot find key", key)

    @classmethod
    def _parse_implicit(cls, tfm, pairs:list[tuple])->Any:
        if pairs != None: 
            return cls(pairs)
        return cls()
    
    @classmethod
    def _parse_explicit(cls, tfm, type_anno, int_dict:Self)->Any:
        if int_dict is None:
            int_dict = cls()
        if type_anno:
            int_dict.set_type(type_anno)
        return int_dict

_all : tuple[Type] = (
    GdValueStringName,
    GdValueArray,
    GdValueVector2,
    GdValueVector3,
    GdValueVector4,
    GdValueVector2i,
    GdValueVector3i,
    GdValueVector4i,
    GdValueRect2,
    GdValueRect2i,
    GdValuePlane,
    GdValueColor,
    GdValueAABB,
    GdValueQuaternion,
    GdValueBasis,
    GdValueTransform2D,
    GdValueTransform3D,
    GdValuePackedByteArray,
    GdValuePackedInt32Array,
    GdValuePackedInt64Array,
    GdValuePackedFloat32Array,
    GdValuePackedFloat64Array,
    GdValuePackedStringArray,
    GdValuePackedVector2Array,
    GdValuePackedVector3Array,
    GdValuePackedVector4Array,
    GdValuePackedColorArray,
    GdValueDictionary,
)