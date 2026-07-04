from .collections import CollectionSubscriber
from array import array
from typing import Any
from collections import OrderedDict, UserString, UserList
from .structure import GdType, GdTypeValue, GdTypeValueSet, GdValue


class NodePath(UserString, GdValue):
    _typing : GdType|GdTypeValue
    def __init__(self, value, /, type:GdType|GdTypeValue=None):
        self._typing = type
        super().__init__(value)

class StringName(UserString, GdValue):
    ...

class Object(GdValue):
    type : str
    kwargs : dict
    def __init__(self, type, **kwargs):
        self.type = type
        self.kwargs = kwargs
    
    def __eq__(self, value):
        if isinstance(value, Object):
            return all([
                self.type == value.type,
                self.kwargs == value.kwargs,
            ])
        return super().__eq__(value)

class Dictionary(OrderedDict, GdValue):
    _typing : GdTypeValueSet 
    def __init__(self, map=tuple(), /, types:tuple[GdType|GdTypeValue|Any]=None):
        self._typing = types
        super().__init__(map)

class Array(list, GdValue):
    _typing : GdTypeValueSet 
    def __init__(self, *values, types:tuple[GdType|GdTypeValue|Any]=None):
        self._typing = types
        super().__init__(values)

class _FixedLenArray(GdValue):
    val : array
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
        return self.val == other
    def __iter__(self):
        yield from self.val

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


class _PackedListSimple(UserList, GdValue):
    def __init__(self, *args):
        l = []
        for v in args:
            l.append(self._types[0](v))
        self.data = l

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



class _PackedListComplex(list, GdValue):
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

class PackedVector2Array(_PackedListComplex):
    _type = Vector2
class PackedVector3Array(_PackedListComplex):
    _type = Vector3
class PackedVector4Array(_PackedListComplex):
    _type = Vector4
class PackedColorArray(_PackedListComplex):
    _type = Color



class PackedByteArray(bytearray, GdValue): 
    ...