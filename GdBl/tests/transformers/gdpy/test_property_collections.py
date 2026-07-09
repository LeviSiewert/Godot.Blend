import bpy
import pytest

from contextlib import contextmanager

from .....GdPy.tests.transformers.tscn.test_values import (
    Test_NodePath as _NodePath,
    Test_StringName as _StringName,
    Test_Object as _Object,
    Test_Dictionary as _Dictionary,
    Test_Array as _Array,
    Test_Vector2i as _Vector2i,
    Test_Vector3i as _Vector3i,
    Test_Vector4i as _Vector4i,
    Test_Rect2i as _Rect2i,
    Test_Vector2 as _Vector2,
    Test_Vector3 as _Vector3,
    Test_Vector4 as _Vector4,
    Test_Rect2 as _Rect2,
    Test_Plane as _Plane,
    Test_Color as _Color,
    Test_AABB as _AABB,
    Test_Quaternion as _Quaternion,
    Test_Transform2D as _Transform2D,
    Test_Transform3D as _Transform3D,
    Test_Basis as _Basis,
    Test_PackedInt32Array as _PackedInt32Array,
    Test_PackedInt64Array as _PackedInt64Array,
    Test_PackedFloat32Array as _PackedFloat32Array,
    Test_PackedFloat64Array as _PackedFloat64Array,
    Test_PackedStringArray as _PackedStringArray,
    Test_PackedVector2Array as _PackedVector2Array,
    Test_PackedVector3Array as _PackedVector3Array,
    Test_PackedVector4Array as _PackedVector4Array,
    Test_PackedColorArray as _PackedColorArray,
    Test_PackedByteArray as _PackedByteArray,
)


from ..._utils import BlenderPytestAttr

from ....core.property_collection import (
    GdPropertyCollection as BlGdPropertyCollection
)

from .....GdPy.core.property_collection import (
    PropertyCollection as PyPropertyCollection
)

from ....transformers.gdpy import (
    bl_to_py_transformer,
    py_to_bl_transformer,
    BlToPyContext,
    PyToBlContext,
) 

def data(x):
    for t,d in x().data():
        yield pytest.param(d, id=t) 

# from .test_resources import _StructureTest

class Test_PropertyCollection(BlenderPytestAttr):
    property_type = bpy.props.PointerProperty(type=BlGdPropertyCollection)

    @contextmanager
    def temp_attr(self,):
        try:
            yield self.get_attr()
        except:
            self.get_attr().clear()
            raise
        self.get_attr().clear()

    _arrays =[ 
        *data(_Array),
        *data(_Vector2i),
        *data(_Vector3i),
        *data(_Vector4i),
        *data(_Rect2i),
        *data(_Vector2),
        *data(_Vector3),
        *data(_Vector4),
        *data(_Rect2),
        *data(_Plane),
        *data(_Color),
        *data(_AABB),
        *data(_Quaternion),
        *data(_Transform2D),
        *data(_Transform3D),
        *data(_Basis),
    ]
    _packedarrays = [
        *data(_PackedInt32Array),
        *data(_PackedInt64Array),
        *data(_PackedFloat32Array),
        *data(_PackedFloat64Array),
        *data(_PackedStringArray),
        *data(_PackedVector2Array),
        *data(_PackedVector3Array),
        *data(_PackedVector4Array),
        *data(_PackedColorArray),
        # *data(_PackedByteArray),
    ]
    _dicts = [            
        *data(_Object),
        *data(_Dictionary),
    ]
    _simples = [
        *data(_NodePath),
        *data(_StringName),
    ]

    @pytest.mark.parametrize("pydata", _arrays)
    def test_round_trip_arrays(self,pydata):
        self._round_trip(pydata)

    @pytest.mark.parametrize("pydata",_packedarrays)
    def test_round_trip_packedarrays(self,pydata):
        self._round_trip(pydata)

    @pytest.mark.parametrize("pydata", _dicts)
    def test_round_trip_dicts(self,pydata):
        self._round_trip(pydata)

    @pytest.mark.parametrize("pydata",_simples)
    def test_round_trip_simples(self,pydata):
        self._round_trip(pydata)

    def _round_trip(self, pydata):        
        with self.temp_attr() as bl_properties:
            bl_properties : BlGdPropertyCollection
            
            c = PyToBlContext()
            c.existing_object.set(bl_properties)
            py_to_bl_transformer.transform_tree(c, PyPropertyCollection({"testattr":pydata}.items()))
            
            assert len(bl_properties) == 1
            assert bl_properties.get("testattr", wrap=False).subtype == pydata.__class__.__name__

            c = BlToPyContext()
            c.existing_object.set(bl_properties)
            res = bl_to_py_transformer.transform_tree(c, bl_properties)

            assert pydata == res["testattr"]