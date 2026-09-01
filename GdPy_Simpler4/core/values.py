from __future__ import annotations

from array import array
from typing import Any
from collections import OrderedDict, UserString, UserList

from .structure import NodePath
from .defininitions import GdDefValue, GdDefType, GdDefValueTyping
from .signals import Signal 

class StringName(UserString):
    def __repr__(self):
        return f'&{super().__repr__()}'

class Object():
    ''' Generic object, stored and accessed as a value. '''
    type : GdDefType
    kwargs : dict
    def __init__(self, type:GdDefType|None=None, **kwargs):
        self.type = type
        self.kwargs = kwargs
    
    def __eq__(self, value):
        if not isinstance(value, Object):
            return super().__eq__(value)
        return all([
            self.type == value.type,
            self.kwargs == value.kwargs,
        ])
    
    def items(self,):
        return self.kwargs.items()
    
    def __repr__(self,):
        return f"{self.__class__.__name__}({self.type,} ...{len(self.kwargs)})"

class Dictionary(OrderedDict):
    added : Signal[str,Any]
    removed : Signal[str,Any]
    updated : Signal[str,Any,Any]

    typing : GdDefValueTyping

    def __setup__(self):
        self.added = Signal(self)
        self.removed = Signal(self) 
        self.updated = Signal(self) 

    def __init__(self, map=tuple(), /, typing:GdDefValueTyping|Any=None):
        self.__setup__()

        if (typing is None):
            self.typing = None
        elif isinstance(typing, str):
            self.typing = GdDefValueTyping(typing)
        elif not isinstance(typing, GdDefValueTyping):
            self.typing = GdDefValueTyping(*typing)
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
    typing : GdDefValueTyping

    added : Signal[str,Any]
    removed : Signal[str,Any]
    updated : Signal[str,Any,Any]

    def __setup__(self):
        self.added = Signal(self)
        self.removed = Signal(self) 
        self.updated = Signal(self) 

    def __init__(self, *values, typing:tuple[GdDefValue|Any]=None):
        self.__setup__()

        if (typing is None):
            self.typing = None
        elif isinstance(typing, str):
            self.typing = GdDefValueTyping(typing)
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

class PackedVector2Array(_PackedListComplex):
    _type = Vector2
class PackedVector3Array(_PackedListComplex):
    _type = Vector3
class PackedVector4Array(_PackedListComplex):
    _type = Vector4
class PackedColorArray(_PackedListComplex):
    _type = Color



class PackedByteArray(bytearray, ): 
    def __init__(self, string, /, encoding="utf-8", errors = "strict"):
        super().__init__(string, encoding, errors)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("[]")})"