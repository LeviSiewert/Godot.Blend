from __future__ import annotations

from array import array
from typing import Any
from collections import OrderedDict, UserString, UserList

from .structure import NodePath, DefValue, DefType, DefValueTyping
from .signals import Signal 
from .enums import PrimitiveType

class StringName(UserString):
    def __repr__(self):
        return f'&{super().__repr__()}'

class Object():
    ''' Generic object, stored and accessed as a value. '''
    type : DefType|str
    kwargs : dict
    def __init__(self, type:DefType|str|None, **kwargs):
        self.type = type
        self.kwargs = kwargs
    
    def __eq__(self, value):
        if not isinstance(value, Object):
            return super().__eq__(value)
        return all([
            self.type == value.type,
            self.kwargs == value.kwargs,
        ])

    def _dif(self, value:Object)->dict:
        
        return {
            "type":(self.type==value.type, self.type, value.type),
            "kwargs":(self.kwargs==value.kwargs, self.kwargs, value.kwargs),
        }
        # return {
        #     "types" : (self.type, value.type) ,
        #     "foreign" : {k:(v) for k,v in value.kwargs.items() if not (k in self.kwargs.keys())},
        #     "local" : {k:(v) for k,v in self.kwargs.items() if not (k in value.kwargs.keys())},
        #     "different" : {k:(v) for k,v in self.kwargs.items() if ((k in value.kwargs.keys()) and  (value.kwargs[k] != v))},
        # }
        
    def items(self,):
        return self.kwargs.items()
    
    def __repr__(self,):
        return f"{self.__class__.__name__}({self.type,} ...{len(self.kwargs)})"

class Dictionary(OrderedDict):
    added : Signal[str,Any]
    removed : Signal[str,Any]
    updated : Signal[str,Any,Any]

    typing : DefValueTyping

    def __setup__(self):
        self.added = Signal(self)
        self.removed = Signal(self) 
        self.updated = Signal(self) 

    def __init__(self, map=tuple(), /, typing:DefValueTyping|Any=None):
        self.__setup__()

        if (typing is None):
            self.typing = None
        elif isinstance(typing, str):
            self.typing = DefValueTyping(typing)
        elif not isinstance(typing, DefValueTyping):
            self.typing = DefValueTyping(*typing)
        else:
            self.typing = typing

        super().__init__(map)

    def __setitem__(self, key, value):
        update = False
        if key in self.keys():
            o_value = self[key]
            update=True

        r = super().__setitem__(key, value)

        if update:
            self.updated(key, o_value, value)
        else:
            self.added(key, value)
        return r

    def __delitem__(self, key):
        value = self.get(key)
        r = super().__delattr__(key)
        self.removed(key, value)
        
class Array(UserList):
    typing : DefValueTyping

    added : Signal[str,Any]
    removed : Signal[str,Any]
    updated : Signal[str,Any,Any]

    def __setup__(self):
        self.added = Signal(self)
        self.removed = Signal(self) 
        self.updated = Signal(self) 

    def __init__(self, *values, typing:tuple[DefValue|Any]=None):
        self.__setup__()

        if (typing is None):
            self.typing = None
        elif isinstance(typing, str):
            self.typing = DefValueTyping(typing)
        else:
            self.typing = typing

        super().__init__(values)

    def __setitem__(self, key:int, value):
        update = False
        if key >= len(self):
            o_value = self[key]
            update=True

        r = super().__setitem__(key, value)

        if update:
            self.updated(key, o_value, value)
        else:
            self.added(key, value)
        return r

    def __delitem__(self, key):
        value = self.get(key)
        r = super().__delattr__(key)
        self.removed(key, value)

    def __hash__(self):
        return id(self.__class__) + sum(hash(x) for x in self.data)

class _FixedLenArray():
    val : array = None
    _type_str : str = "f"
    _types = (int, float,)
    _len: int = 0
    _def: Any = float(0.0)
    def __init__(self, *args):
        if args and (args != (None,)*self._len):
            assert(len(args) == self._len)
            self.val = array(self._type_str, args) #Let god (array) sort out the types
        else:
            self.val = array(self._type_str, (self._def,)*self._len)
    def __eq__(self, other):
        if not hasattr(other,"__len__"):
            return False
        if len(other) != len(self.val):
            return False
        return all(a==b for a,b in zip(other,self.val))
    def __iter__(self):
        yield from self.val
    def __len__(self):
        return len(self.val)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.val.__repr__()})"

    def __hash__(self):
        return id(self.__class__) + sum(hash(x) for x in self.val)

class Vector2i(_FixedLenArray):
    _type_str : str = "i"
    _types = (int,)
    _len = 2
    _def = 0
class Vector3i(_FixedLenArray):
    _type_str : str = "i"
    _types = (int,)
    _len = 3
    _def = 0
class Vector4i(_FixedLenArray):
    _type_str : str = "i"
    _types = (int,)
    _len = 4
    _def = 0
class Rect2i(_FixedLenArray):
    _type_str : str = "i"
    _types = (int,)
    _len = 4
    _def = 0

class Vector2(_FixedLenArray): 
    _len = 2
class Vector3(_FixedLenArray): 
    _len = 3
class Vector4(_FixedLenArray): 
    _len = 4
class Rect2(_FixedLenArray): 
    _len = 4
class Plane(_FixedLenArray): 
    _len = 4
class Color(_FixedLenArray): 
    _len = 4
class AABB(_FixedLenArray): 
    _len = 6
class Quaternion(_FixedLenArray): 
    _len = 4
class Transform2D(_FixedLenArray): 
    _len = 6
class Transform3D(_FixedLenArray): 
    _len = 12
class Basis(_FixedLenArray): 
    _len = 9
    def __init__(self, *args):
        if len(args) == 3:
            super().__init__(*args[0],*args[1],*args[2])
            return
        super().__init__(*args)


class _PackedListSimple(UserList, ):
    def __init__(self, *args):
        l = []
        for v in args:
            l.append(self._types[0](v))
        self.data = l

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("[]")})"

    def __eq__(self, other):
        if not hasattr(other,"__len__"):
            return False
        if len(other) != len(self.data):
            return False
        return all(a==b for a,b in zip(other,self.data))

    def __hash__(self):
        return id(self.__class__) + sum(hash(x) for x in self.data)


class PackedInt32Array(_PackedListSimple):
    _types = (int,)
class PackedInt64Array(_PackedListSimple):
    _types = (int,)

class PackedFloat32Array(_PackedListSimple):
    _types = (float,int)
class PackedFloat64Array(_PackedListSimple):
    _types = (float,int)

class PackedStringArray(_PackedListSimple): 
    _types = (str,)



class _PackedListComplex(UserList, ):
    _type : _FixedLenArray = Vector2
    def __init__(self, *args):
        super().__init__(self._unpack(args))

    @classmethod
    def _unpack(cls, _value):
        values = list(_value)
        ty : _FixedLenArray = cls._type
        while len(values):
            if isinstance(values[0], ty):
                yield values.pop(0)
            elif isinstance(values[0], ty._types):
                yield ty(*values[0:ty._len])
                values = values[ty._len:len(values)]
            elif hasattr(values[0], "__iter__"):
                yield ty(*values.pop(0))
            else:
                raise TypeError("Could not cast input to types", _value, ty)

    def __eq__(self, other):
        if not hasattr(other,"__len__"):
            return False
        if len(other) != len(self.data):
            return False
        return all(a==b for a,b in zip(other,self.data))
        
    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("[]")})"

    def __hash__(self):
        return id(self.__class__) + sum(hash(x) for x in self.data)
        # return id(self.__class__)+int("".join(str(abs(hash(x))) for x in self.data))
        

class PackedVector2Array(_PackedListComplex):
    _type = Vector2
class PackedVector3Array(_PackedListComplex):
    _type = Vector3
class PackedVector4Array(_PackedListComplex):
    _type = Vector4
class PackedColorArray(_PackedListComplex):
    _type = Color


class PackedByteArray(bytearray): 
    def __init__(self, string, /, encoding="utf-8", errors = "strict"):
        super().__init__(string, encoding, errors)

    def __hash__(self):
        return id(self)

class Projection():...


type_map = {
    PrimitiveType.NIL : None, 
    PrimitiveType.BOOL : bool, 
    PrimitiveType.INT : int, 
    PrimitiveType.FLOAT : float, 
    PrimitiveType.STRING : str, 
    PrimitiveType.VECTOR2 : Vector2, 
    PrimitiveType.VECTOR2I : Vector2i, 
    PrimitiveType.RECT2 : Rect2, 
    PrimitiveType.RECT2I : Rect2i, 
    PrimitiveType.VECTOR3 : Vector3, 
    PrimitiveType.VECTOR3I : Vector3i, 
    PrimitiveType.TRANSFORM2D : Transform2D, 
    PrimitiveType.VECTOR4 : Vector4, 
    PrimitiveType.VECTOR4I : Vector4i, 
    PrimitiveType.PLANE : Plane, 
    PrimitiveType.QUATERNION : Quaternion, 
    PrimitiveType.AABB : AABB, 
    PrimitiveType.BASIS : Basis, 
    PrimitiveType.TRANSFORM3D : Transform3D, 
    PrimitiveType.PROJECTION : Projection, 
    PrimitiveType.COLOR : Color, 
    PrimitiveType.STRINGNAME : StringName, 
    PrimitiveType.NODEPATH : NodePath, 
    PrimitiveType.RID : str, 
    PrimitiveType.OBJECT : Object, 
    PrimitiveType.CALLABLE : callable, 
    PrimitiveType.SIGNAL : Signal,
    PrimitiveType.DICTIONARY : Dictionary, 
    PrimitiveType.ARRAY : Array, 
    PrimitiveType.PACKEDBYTEARRAY : PackedByteArray, 
    PrimitiveType.PACKEDINT32ARRAY : PackedInt32Array, 
    PrimitiveType.PACKEDINT64ARRAY : PackedInt64Array, 
    PrimitiveType.PACKEDFLOAT32ARRAY : PackedFloat32Array, 
    PrimitiveType.PACKEDFLOAT64ARRAY : PackedFloat64Array, 
    PrimitiveType.PACKEDSTRINGARRAY : PackedStringArray, 
    PrimitiveType.PACKEDVECTOR2ARRAY : PackedVector2Array, 
    PrimitiveType.PACKEDVECTOR3ARRAY : PackedVector3Array, 
    PrimitiveType.PACKEDCOLORARRAY : PackedColorArray, 
    PrimitiveType.PACKEDVECTOR4ARRAY : PackedVector4Array, 
}

str_map = {
    "NIL" : None, 
    "BOOL" : bool, 
    "INT" : int, 
    "FLOAT" : float, 
    "STRING" : str, 
    "VECTOR2" : Vector2, 
    "VECTOR2I" : Vector2i, 
    "RECT2" : Rect2, 
    "RECT2I" : Rect2i, 
    "VECTOR3" : Vector3, 
    "VECTOR3I" : Vector3i, 
    "TRANSFORM2D" : Transform2D, 
    "VECTOR4" : Vector4, 
    "VECTOR4I" : Vector4i, 
    "PLANE" : Plane, 
    "QUATERNION" : Quaternion, 
    "AABB" : AABB, 
    "BASIS" : Basis, 
    "TRANSFORM3D" : Transform3D, 
    "PROJECTION" : Projection, 
    "COLOR" : Color, 
    "STRINGNAME" : StringName, 
    "NODEPATH" : NodePath, 
    "RID" : str, 
    "OBJECT" : Object, 
    "CALLABLE" : callable, 
    "SIGNAL" : Signal,
    "DICTIONARY" : Dictionary, 
    "ARRAY" : Array, 
    "PACKEDBYTEARRAY" : PackedByteArray, 
    "PACKEDINT32ARRAY" : PackedInt32Array, 
    "PACKEDINT64ARRAY" : PackedInt64Array, 
    "PACKEDFLOAT32ARRAY" : PackedFloat32Array, 
    "PACKEDFLOAT64ARRAY" : PackedFloat64Array, 
    "PACKEDSTRINGARRAY" : PackedStringArray, 
    "PACKEDVECTOR2ARRAY" : PackedVector2Array, 
    "PACKEDVECTOR3ARRAY" : PackedVector3Array, 
    "PACKEDCOLORARRAY" : PackedColorArray, 
    "PACKEDVECTOR4ARRAY" : PackedVector4Array, 
}