from __future__ import annotations
from .core import GdResource, GdType, GdValue, Signal, SignalContainer
from typing import Self, Type, Any, Iterable
from lark import Token #type: ignore 
from array import array
from collections import OrderedDict

class GdValueStringName(GdValue):
    value : str = ""
    def __init__(self, val=None):
        super().__init__()
        if not (val is None):
            self.set_value(val)

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("stringname",)

    @classmethod
    def parse_lark(cls, key, tc, gdc, address): #, address:Token)->Any:
        inst = cls()
        inst.value = str(address).strip('"&')
        return inst
        
    def set_value(self, value):
        self.value = str(value)

    def __eq__(self, value)->bool:
        if isinstance(value, self.__class__):
            return self.value == value
        return value == self.value

    def __hash__(self):
        return super().__hash__()
    
    def __str__(self):
        return self.value

class GdValueArray(GdValue):
    value : list
    _type : str = "Variant"

    item_appended : Signal
    item_removed : Signal
    
    def __init__(self, val:Any=None, type:str="Variant"):
        self.set_type(type)
        self.set_value(val)
        super().__init__()

    def set_type(self, _type:str):
        if _type is None: 
            self._type = "Variant"
            return
        self._type = _type

    def set_value(self, value):
        self.value = []
        if value is None:
            return
        for x in value:
            self.append(x)

    def is_def_value(self):
        return self.value == tuple()

    def append(self, item:Any):
        # if self._type:
        #     assert(isinstance(item,self._type))
        #   FUTURE
        self.value.append(item)
        # self.item_appended(item) #FUTURE 
        
    def remove(self, item:Any):
        self.value.remove(item)
        # self.item_removed(item) #FUTURE

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("array","array_explicit")
    
    @classmethod
    def parse_lark(cls, key, tc, gdc, *args, **kwargs)->Any:
        if key == "array":
            return cls._parse_implicit(tc, gdc, *args, **kwargs)
        elif key == "array_explicit":
            return cls._parse_explicit(tc, gdc, *args, **kwargs)
        else:
            raise Exception("Could not determine key", key)

    @classmethod
    def _parse_explicit(cls, tc, gdc, typing, interior_array:GdValueArray|None):
        if interior_array is None:
            res = cls(None, typing)
            return res
        interior_array.set_type(typing)
        return interior_array
    
    @classmethod
    def _parse_implicit(cls, tc, gdc, *children:list[Token|Any]):
        return cls(children)
    
    def __iter__(self,):
        return self.value.__iter__()

    def __eq__(self, other)->bool:
        if hasattr(other,"__iter__"):
            return self.value == other
        return False
    
    def __len__(self):
        return len(self.value)
    
    def _get_struct_children(self,)->Iterable:
        return self.value
    
    def __hash__(self):
        return super().__hash__()

class _GdValueArrayPackedType(GdValue):
    value : list

    def __init__(self, value:Iterable=None):
        if not (value is None):
            self.set_value(value)
        else:
            self.def_value()

    def set_value(self, value):
        self.value = list(value)

    def def_value(self):
        self.value = list()

    def is_def_value(self):
        return self.value == tuple()

    def __iter__(self,):
        return self.value.__iter__()
    
    def __eq__(self, other)->bool:
        if hasattr(other,"__iter__"):
            return self.value == other
        return False
    
    def __len__(self):
        return len(self.value)

    def __hash__(self):
        return super().__hash__()

class _GdValueArrayFixedLength(GdValue):
    value : array|tuple = tuple()
    _arr_item_def = 0
    _arr_type : str = "f"
    _arr_length : int = 0

    def __init__(self, val:Any=None):
        if (val is None) or (tuple(val) == ((None,)*self._arr_length)):
            self.def_value()
        else:
            self.set_value(val)

    def def_value(self,):
        self.value = self.get_def_value()
    def get_def_value(self,):
        return array(self._arr_type, (self.types[0](self._arr_item_def),)*self._arr_length)
    def is_def_value(self):
        return self.value == self.get_def_value()

    def set_value(self, value:Iterable):
        if len(value) != self._arr_length:
            raise Exception("len(vals) != cls._arr_length", self._arr_length, value )
        self.value = array(self._arr_type, value)
    
    def __iter__(self,):
        return self.value.__iter__()
    
    def __eq__(self, other)->bool:
        if hasattr(other,"__iter__"):
            return self.value == other
        return False
    
    def __hash__(self):
        return super().__hash__()

    def __len__(self):
        return len(self.value)

class GdValueVector2(_GdValueArrayFixedLength):
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 2
class GdValueVector3(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 3
class GdValueVector4(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 4
class GdValueVector2i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 2
class GdValueVector3i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 3
class GdValueVector4i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 4
class GdValueRect2(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 4
class GdValueRect2i(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "i"
    _arr_length : int = 4
class GdValuePlane(_GdValueArrayFixedLength): 
    types = (int,)
    _arr_type : str = "f"
    _arr_length : int = 4
class GdValueColor(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 4
class GdValueAABB(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 6
class GdValueQuaternion(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 4
class GdValueTransform2D(_GdValueArrayFixedLength):
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 6
class GdValueBasis(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 9
    
    def set_value(self, value:Iterable):
        if len(value) == 3:
            value = tuple(self._unpack(value))
        super().set_value(value)

    def _unpack(self, val:Iterable):
        for e in val:
            yield from e


class GdValueTransform3D(_GdValueArrayFixedLength): 
    types = (float,int)
    _arr_type : str = "f"
    _arr_length : int = 12


class GdValuePackedByteArray(_GdValueArrayPackedType): 
    types = (str,)
class GdValuePackedInt32Array(_GdValueArrayPackedType): 
    types = (int,)
class GdValuePackedInt64Array(_GdValueArrayPackedType): 
    types = (int,)
class GdValuePackedFloat32Array(_GdValueArrayPackedType): 
    types = (int,float)
class GdValuePackedFloat64Array(_GdValueArrayPackedType): 
    types = (int,float)
class GdValuePackedStringArray(_GdValueArrayPackedType): 
    types = (str,)

class _GdValueArrayPackedTypeComplex(_GdValueArrayPackedType):
    value : list
    types : tuple[Type]

    def __init__(self, value:Iterable[Iterable|Any]=None):
        if value is None:
            self.def_value()
            return

        assert hasattr(value, "__iter__")
        if len(value) == 0:
            self.def_value()
            return

        self.set_value(self._unpack(value))

    @classmethod
    def _unpack(cls, _value:Iterable):
        values = list(_value)
        ty = cls.types[0]
        while len(values):
            if isinstance(values[0], cls.types):
                yield values.pop(0)
            elif isinstance(values[0], ty.types):
                yield ty(values[0:ty._arr_length])
                values = values[ty._arr_length:len(values)]
            elif hasattr(values[0], "__iter__"):
                yield ty(values.pop(0))
            else:
                raise TypeError("Could not cast input to types", _value, ty)

class GdValuePackedVector2Array(_GdValueArrayPackedTypeComplex): 
    types = (GdValueVector2,)
class GdValuePackedVector3Array(_GdValueArrayPackedTypeComplex): 
    types = (GdValueVector3,)
class GdValuePackedVector4Array(_GdValueArrayPackedTypeComplex): 
    types = (GdValueVector4,)
class GdValuePackedColorArray(_GdValueArrayPackedTypeComplex): 
    types = (GdValueColor,)


class GdValueDictionary(GdValue):
    value : OrderedDict
    types : tuple[Type] = ("Variant","Variant")

    def __init__(self, value:Iterable[tuple]|dict=None, types:tuple[Type]=None):
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

        if self.types:
            self.check_types()

    @classmethod
    def lark_keys(cls)->tuple[str]: 
        return ("dictionary","dictionary_explicit")
    
    def set_value(self, value):
        self.value = OrderedDict(value)
    def def_value(self):
        self.value = OrderedDict()
    def set_type(self, types:tuple[str,str]):
        if types is None: return
        self.types = types

    def check_types(self):
        ##TODO
        pass

    def __eq__(self, value):
        return self.value == value

    @classmethod
    def parse_lark(cls, key, tc, gdc, *args, **kwargs)->Any:
        if key == "dictionary":
            return cls._parse_implicit(*args, **kwargs)
        elif key == "dictionary_explicit":
            return cls._parse_explicit(*args, **kwargs)
        else:
            raise Exception("Cannot find key", key)

    @classmethod
    def _parse_implicit(cls, pairs:list[tuple]=tuple())->Any: 
        return cls(pairs)
    
    @classmethod
    def _parse_explicit(cls, type_anno, int_dict:Self)->Any:
        if int_dict is None:
            int_dict = cls()
        if type_anno:
            int_dict.set_type(type_anno)
        return int_dict
    
    def items(self):
        yield from self.value.items()

    def __hash__(self):
        return super().__hash__()

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

_type_map = {t.__name__:t for t in (*_all, str, int, float, bool)} | {t:t.__name__ for t in (*_all, str, int, float, bool)} | { "None" : None, None: "None" }

_primitive_types = {t.__name__:t for t in (GdValueStringName, str, int, float, bool) } | { "None" : None }
_vector_types = {t.__name__:t for t in (GdValueVector2,GdValueVector3,GdValueVector4,GdValueVector2i,GdValueVector3i,GdValueVector4i,GdValueRect2,GdValueRect2i,GdValuePlane,GdValueColor,GdValueAABB,GdValueQuaternion,GdValueBasis,GdValueTransform2D,GdValueTransform3D) }
_array_types = {t.__name__:t for t in (GdValueArray,GdValuePackedByteArray,GdValuePackedInt32Array,GdValuePackedInt64Array,GdValuePackedFloat32Array,GdValuePackedFloat64Array,GdValuePackedStringArray,GdValuePackedVector2Array,GdValuePackedVector3Array,GdValuePackedVector4Array,GdValuePackedColorArray) }
_dict_types = {t.__name__:t for t in (GdValueDictionary,) }
