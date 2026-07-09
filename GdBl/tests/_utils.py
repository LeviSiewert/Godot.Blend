import bpy

from typing import Any
from contextvars import ContextVar
from contextlib import contextmanager

from ...GdBl import register, unregister

class BlenderPytest():
    @classmethod
    def setup_class(cls):
        register()

    @classmethod
    def teardown_class(cls):
        unregister()

is_registered : ContextVar[bool] = ContextVar("is_registered", default=False)

class BlenderPytestAttr():
    ''' Provide a property of the given type on a scene for testing purposes
    self.get_attr & self.get_attr_loc are accessors
    '''
    property_type : Any #= bpy.props.StringProperty()
    property_name : str = "TESTATTR"
    mount_onto : Any = bpy.types.Scene

    @contextmanager
    def temp_attr(self,):
        raise NotImplementedError()
        yield

    @classmethod
    def get_attr(cls):
        return getattr(bpy.data.scenes[0], cls.property_name)

    @classmethod
    def get_attr_loc(cls)->tuple[Any,str]:
        return (bpy.data.scenes[0], cls.property_name)

    @classmethod
    def setup_class(cls):
        if not is_registered.get():
            register()    
            is_registered.set(True)
        setattr(cls.mount_onto, cls.property_name, cls.property_type)

    @classmethod
    def teardown_class(cls):
        delattr(cls.mount_onto,  cls.property_name)
        if is_registered.get():
            unregister()
            is_registered.set(False)