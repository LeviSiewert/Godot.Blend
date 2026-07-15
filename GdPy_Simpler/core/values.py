from array import array
from typing import Any
from collections import OrderedDict, UserString, UserList

from .property_collection import GdValue, _SetContextMixin
from .gdtype import GdType

from .structure import (Resource as _Resource, File as _File)


class NodePath(UserString, GdValue):
    _typing : GdType

    def __init__(self, value, /, typing:GdType=None):
        self._typing = typing
        super().__init__(value)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"
    
class StringName(UserString, GdValue):
    def __repr__(self):
        return f'&{super().__repr__()}'

class Object(GdValue):
    type : str
    kwargs : dict
    def __init__(self, type, **kwargs):
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

class Dictionary(OrderedDict, GdValue, _SetContextMixin):
    typing : GdType
    def __init__(self, map=tuple(), /, typing:tuple[GdType|Any]=None):
        self.typing = typing
        super().__init__(map)

    def __setitem__(self, key, value):
        if (not isinstance(value, GdValue)) and isinstance(value, (dict, list)):
            raise TypeError("This object cannot intake base dicts or lists due to context object support. Use values.Dictionary or values.Array instead")
        self._set_item_context(key, value)
        return super().__setitem__(key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("{}")})"
    
    def contains_subresource(self):
        for k,v in self.items():
            if isinstance(v, (Array,Dictionary)):
                if v.contains_subresource():
                    return True
            elif isinstance(v, _Resource):
                if not v.is_file:
                    return True
        return False

class Array(UserList, GdValue, _SetContextMixin):
    typing : GdType

    def __init__(self, *values, typing:tuple[GdType|Any]=None):
        self.typing = typing
        super().__init__(values)

    def append(self, value):        
        if (not isinstance(value, GdValue)) and isinstance(value, (dict, list)):
            raise TypeError("This object cannot intake base dicts or lists due to context object support. Use values.Dictionary or values.Array instead")
        self._set_item_context(len(self)+1, value)
        return super().append(object)
    
    def __setitem__(self, key, value):
        if (not isinstance(value, GdValue)) and isinstance(value, (dict, list)):
            raise TypeError("This object cannot intake base dicts or lists due to context object support. Use values.Dictionary or values.Array instead")
        self._set_item_context(key, value)
        return super().__setitem__(key, value)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("[]")})"

    def contains_subresource(self):
        for v in self.data:
            if isinstance(v, (Array,Dictionary)):
                if v.contains_subresource():
                    return True
            elif isinstance(v, _Resource):
                if not v.is_file:
                    return True
        return False


class _FixedLenArray(GdValue):
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
        return self.val == other
    def __iter__(self):
        yield from self.val

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


class _PackedListSimple(UserList, GdValue):
    def __init__(self, *args):
        l = []
        for v in args:
            l.append(self._types[0](v))
        self.data = l

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("[]")})"

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



class _PackedListComplex(UserList, GdValue):
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



class PackedByteArray(bytearray, GdValue): 
    def __init__(self, string, /, encoding="utf-8", errors = "strict"):
        super().__init__(string, encoding, errors)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__().strip("[]")})"