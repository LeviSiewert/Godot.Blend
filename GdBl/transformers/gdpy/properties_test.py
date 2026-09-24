import bpy

from contextvars import ContextVar
from typing import Iterable

from ._core import make_bl_to_gd, make_gd_to_bl
from ....GdBl import register, unregister

is_registered : ContextVar[bool] = ContextVar("is_registered", default=False)

from ....GdPy.transformers.gd_to_py import (
    values_test as T_PyValues, 
)

from ....GdPy.core.structure import (
    Promise as PyPromise,
)

class _Unit():
    ''' Setup and breakdown of object type at location per-test '''
    property_type : bpy.types = bpy.types.StringProperty()
    property_name : str = "attr"
    property_clss : bpy.types.scene 

    def get_attr(self)->tuple[object, str]:
        return bpy.data.scene, self.property_name
    
    def get_value(self)->tuple[object, str]:
        return getattr(*self.get_attr())
    
    @classmethod
    def setup_class(cls):
        if not is_registered.get():
            register()
            is_registered.set(True)
            setattr(cls.property_clss, cls.property_name, cls.property_type)

    @classmethod
    def teardown_class(cls):
        if is_registered.get():
            delattr(cls.property_clss, cls.property_name)            
            unregister()

    _data : Iterable

    def data(self):
        yield from self._data

    def test(self):
        bl_to_gd = make_bl_to_gd()
        gd_to_bl = make_gd_to_bl()
        for x in self.data():
            self._round_trip(bl_to_gd, gd_to_bl, x)
            bl_to_gd.memo.clear()
            gd_to_bl.memo.clear()

    def _round_trip(self, bl_to_gd, gd_to_bl, py_obj):
        bl_obj = gd_to_bl.transform(py_obj)
        n_py_obj = bl_to_gd.transform(bl_obj)
        assert n_py_obj == py_obj

def data(gen):
    for txt, obj in gen: 
        yield obj

class Test_Values():
    ''' Extract values from tscn->python tests to verify against'''

    class Test_Array(_Unit): 
        _data = [*data(T_PyValues.Test_Array.data())]
    class Test_Vector2i(_Unit): 
        _data = [*data(T_PyValues.Test_Vector2i.data())]
    class Test_Vector3i(_Unit): 
        _data = [*data(T_PyValues.Test_Vector3i.data())]
    class Test_Vector4i(_Unit): 
        _data = [*data(T_PyValues.Test_Vector4i.data())]
    class Test_Rect2i(_Unit): 
        _data = [*data(T_PyValues.Test_Rect2i.data())]
    class Test_Vector2(_Unit): 
        _data = [*data(T_PyValues.Test_Vector2.data())]
    class Test_Vector3(_Unit): 
        _data = [*data(T_PyValues.Test_Vector3.data())]
    class Test_Vector4(_Unit): 
        _data = [*data(T_PyValues.Test_Vector4.data())]
    class Test_Rect2(_Unit): 
        _data = [*data(T_PyValues.Test_Rect2.data())]
    class Test_Plane(_Unit): 
        _data = [*data(T_PyValues.Test_Plane.data())]
    class Test_Color(_Unit): 
        _data = [*data(T_PyValues.Test_Color.data())]
    class Test_AABB(_Unit): 
        _data = [*data(T_PyValues.Test_AABB.data())]
    class Test_Quaternion(_Unit): 
        _data = [*data(T_PyValues.Test_Quaternion.data())]
    class Test_Transform2D(_Unit): 
        _data = [*data(T_PyValues.Test_Transform2D.data())]
    class Test_Transform3D(_Unit): 
        _data = [*data(T_PyValues.Test_Transform3D.data())]
    class Test_Basis(_Unit): 
        _data = [*data(T_PyValues.Test_Basis.data())]

    class Test_PackedInt32Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedInt32Array.data())]
    class Test_PackedInt64Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedInt64Array.data())]
    class Test_PackedFloat32Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedFloat32Array.data())]
    class Test_PackedFloat64Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedFloat64Array.data())]
    class Test_PackedStringArray(_Unit): 
        _data = [*data(T_PyValues.Test_PackedStringArray.data())]
    class Test_PackedVector2Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedVector2Array.data())]
    class Test_PackedVector3Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedVector3Array.data())]
    class Test_PackedVector4Array(_Unit): 
        _data = [*data(T_PyValues.Test_PackedVector4Array.data())]
    class Test_PackedColorArray(_Unit): 
        _data = [*data(T_PyValues.Test_PackedColorArray.data())]

    class Test_Object(_Unit): 
        _data = [*data(T_PyValues.Test_Object.data())]
    class Test_Dictionary(_Unit): 
        _data = [*data(T_PyValues.Test_Dictionary.data())]

    class Test_NodePath(_Unit): 
        _data = [*data(T_PyValues.Test_NodePath.data())]
    class Test_StringName(_Unit): 
        _data = [*data(T_PyValues.Test_StringName.data())]

class Test_Promises():
    ''' Promises are converted 1 to 1 '''
    def data(self):
        yield PyPromise("value", PyPromise.Type.FILE)
        yield PyPromise("value", PyPromise.Type.RESOURCE)
        yield PyPromise("value", PyPromise.Type.SUB_RESOURCE)
        yield PyPromise("value", PyPromise.Type.EXT_RESOURCE)
        yield PyPromise("value", PyPromise.Type.EXT_RESOURCE_DIRECT)

class Test_StructureRef():
    '''Modeling of correct behavior, including declaration of dependencies and data loss via non-eq
    Basis: deepending on settings objects may or may not be imported. 
    However object reference will be converted to promises. 
    '''
    def standin_test():
        raise NotImplementedError()



    