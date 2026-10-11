# from __future__ import annotations

# from typing import Type, Any
from enum import Enum

# from .context import Context
# from .collection import CollectionKeyProperty, Collection

class PropertyHint(Enum):
    PROPERTY_HINT_NONE = 0
    PROPERTY_HINT_RANGE = 1
    PROPERTY_HINT_ENUM = 2
    PROPERTY_HINT_ENUM_SUGGESTION = 3
    PROPERTY_HINT_EXP_EASING = 4
    PROPERTY_HINT_LINK = 5
    PROPERTY_HINT_FLAGS = 6
    PROPERTY_HINT_LAYERS_2D_RENDER = 7
    PROPERTY_HINT_LAYERS_2D_PHYSICS = 8
    PROPERTY_HINT_LAYERS_2D_NAVIGATION = 9
    PROPERTY_HINT_LAYERS_3D_RENDER = 10
    PROPERTY_HINT_LAYERS_3D_PHYSICS = 11
    PROPERTY_HINT_LAYERS_3D_NAVIGATION = 12
    PROPERTY_HINT_FILE = 13
    PROPERTY_HINT_DIR = 14
    PROPERTY_HINT_GLOBAL_FILE = 15
    PROPERTY_HINT_GLOBAL_DIR = 16
    PROPERTY_HINT_RESOURCE_TYPE = 17
    PROPERTY_HINT_MULTILINE_TEXT = 18
    PROPERTY_HINT_EXPRESSION = 19
    PROPERTY_HINT_PLACEHOLDER_TEXT = 20
    PROPERTY_HINT_COLOR_NO_ALPHA = 21
    PROPERTY_HINT_OBJECT_ID = 22
    PROPERTY_HINT_TYPE_STRING = 23
    PROPERTY_HINT_NODE_PATH_TO_EDITED_NODE = 24
    PROPERTY_HINT_OBJECT_TOO_BIG = 25
    PROPERTY_HINT_NODE_PATH_VALID_TYPES = 26
    PROPERTY_HINT_SAVE_FILE = 27
    PROPERTY_HINT_GLOBAL_SAVE_FILE = 28
    PROPERTY_HINT_INT_IS_OBJECTID = 29
    PROPERTY_HINT_INT_IS_POINTER = 30
    PROPERTY_HINT_ARRAY_TYPE = 31
    PROPERTY_HINT_LOCALE_ID = 32
    PROPERTY_HINT_LOCALIZABLE_STRING = 33
    PROPERTY_HINT_NODE_TYPE = 34
    PROPERTY_HINT_HIDE_QUATERNION_EDIT = 35
    PROPERTY_HINT_PASSWORD = 36
    PROPERTY_HINT_LAYERS_AVOIDANCE = 37
    PROPERTY_HINT_DICTIONARY_TYPE = 38
    PROPERTY_HINT_TOOL_BUTTON = 39
    PROPERTY_HINT_ONESHOT = 40
    PROPERTY_HINT_GROUP_ENABLE = 42
    PROPERTY_HINT_INPUT_NAME = 43
    PROPERTY_HINT_FILE_PATH = 44
    PROPERTY_HINT_MAX = 45

class PrimitiveType(Enum):
    NIL = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    VECTOR2 = 5
    VECTOR2I = 6
    RECT2 = 7
    RECT2I = 8
    VECTOR3 = 9
    VECTOR3I = 10
    TRANSFORM2D = 11
    VECTOR4 = 12
    VECTOR4I = 13
    PLANE = 14
    QUATERNION = 15
    AABB = 16
    BASIS = 17
    TRANSFORM3D = 18
    PROJECTION = 19
    COLOR = 20
    STRINGNAME = 21
    NODEPATH = 22
    RID = 23
    OBJECT = 24
    CALLABLE = 25
    SIGNAL = 26
    DICTIONARY = 27
    ARRAY = 28
    PACKEDBYTEARRAY = 29
    PACKEDINT32ARRAY = 30
    PACKEDINT64ARRAY = 31
    PACKEDFLOAT32ARRAY = 32
    PACKEDFLOAT64ARRAY = 33
    PACKEDSTRINGARRAY = 34
    PACKEDVECTOR2ARRAY = 35
    PACKEDVECTOR3ARRAY = 36
    PACKEDCOLORARRAY = 37
    PACKEDVECTOR4ARRAY = 38

class PropertyUsage(Enum):
    PROPERTY_USAGE_NONE = 0 
    PROPERTY_USAGE_STORAGE = 2 
    PROPERTY_USAGE_EDITOR = 4 
    PROPERTY_USAGE_DEFAULT = 6 
    PROPERTY_USAGE_INTERNAL = 8 
    PROPERTY_USAGE_CHECKABLE = 16 
    PROPERTY_USAGE_CHECKED = 32 
    PROPERTY_USAGE_GROUP = 64 
    PROPERTY_USAGE_CATEGORY = 128 
    PROPERTY_USAGE_SUBGROUP = 256 
    PROPERTY_USAGE_CLASS_IS_BITFIELD = 512 
    PROPERTY_USAGE_NO_INSTANCE_STATE = 1024 
    PROPERTY_USAGE_RESTART_IF_CHANGED = 2048 
    PROPERTY_USAGE_SCRIPT_VARIABLE = 4096 
    PROPERTY_USAGE_STORE_IF_NULL = 8192 
    PROPERTY_USAGE_UPDATE_ALL_IF_MODIFIED = 16384 
    PROPERTY_USAGE_SCRIPT_DEFAULT_VALUE = 32768 
    PROPERTY_USAGE_CLASS_IS_ENUM = 65536 
    PROPERTY_USAGE_NIL_IS_VARIANT = 131072 
    PROPERTY_USAGE_ARRAY = 262144 
    PROPERTY_USAGE_ALWAYS_DUPLICATE = 524288 
    PROPERTY_USAGE_NEVER_DUPLICATE = 1048576 
    PROPERTY_USAGE_HIGH_END_GFX = 2097152 
    PROPERTY_USAGE_NODE_PATH_FROM_SCENE_ROOT = 4194304 
    PROPERTY_USAGE_RESOURCE_NOT_PERSISTENT = 8388608 
    PROPERTY_USAGE_KEYING_INCREMENTS = 16777216 
    PROPERTY_USAGE_DEFERRED_SET_RESOURCE = 33554432 
    PROPERTY_USAGE_EDITOR_INSTANTIATE_OBJECT = 67108864 
    PROPERTY_USAGE_EDITOR_BASIC_SETTING = 134217728 
    PROPERTY_USAGE_READ_ONLY = 268435456 
    PROPERTY_USAGE_SECRET = 536870912

# from .structure import PromiseProperty, Promise

# class DefValue:
#     context : Context 

#     default : Any = None

#     _type : str|TypeMap = None
#     type = PromiseProperty("_type", None, Promise.Type.TYPE)    

#     def __init__(self, type:str|TypeMap, default:Any=None):
        
#         pass

# class DefProperty:
#     context : Context

#     _name : str = None
#     name = CollectionKeyProperty(str, "_name")
    
#     _type : str|TypeMap = None
#     type = PromiseProperty("_type", None, Promise.Type.TYPE)
    
#     default_value : Any = None
#     hint : HintMap
#     hint_string : str
#     usage : UsageMap
    
#     def __init__(self, name, type:TypeMap|str, default:Any=None, hint:HintMap=HintMap[0], hint_string:str="", usage:UsageMap=UsageMap[6]):
#         self.context = Context()
#         self.name = name
#         self.type = type
#         self.default_value = default_value
#         self.hint = hint
#         self.hint_string = hint_string
#         self.usage = usage

# class DefSignal:
#     context : Context
#     _name : str = None
#     name = CollectionKeyProperty(str, "_name")
#     flags : int
#     id : int
#     args : list[DefValue]
#     default_args : list[DefValue]
#     ret : DefValue

#     def __init__(self, name:str, flags:int, ret:DefValue, args:Iterable[DefValue]=tuple(), default_args:Iterable[DefValue]=tuple()):
#         self.name = name
#         self.flags = flags
#         self.id = id
#         self.args = args
#         self.default_args = default_args
#         self.ret = ret

# class DefType:
#     extends : DefType|None = None
#     context : Context

#     _identifier : str = None
#     identifier = CollectionKeyProperty(str|TypeMap, "_identifier")
    
#     properties : Collection[DefProperty]
#     signals : Collection[DefSignal]
    

#     def __init__(self, identifier:str, properties:Iterable[DefProperty], signals:Iterable[DefSignal]):
#         self.properties = Collection("_identifier")
#         self.signals = Collection("_identifier")
        