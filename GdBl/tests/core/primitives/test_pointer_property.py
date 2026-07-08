import bpy 

from ..._utils import BlenderPytestAttr as _BlenderPytestAttr

from ....core.primitives.pointer_collection import (
    BlPropertyItem,
    BlPointerArrayItem,
    BlPointerArray,
    BlPointerDictionaryItem,
    BlPointerDictionary,
    PointerCollection,
)

_all = (
    BlPropertyItem,
    BlPointerArrayItem,
    BlPointerArray,
    BlPointerDictionaryItem,
    BlPointerDictionary,
    # PointerCollection,
)


class _PointerCollectionTest(_BlenderPytestAttr):
    ''' Testing of local PointerCollection, override LocalPointerCollection and types w/ relevent info '''

    class LocalPointerCollection(PointerCollection):
        pass

    types = (
        LocalPointerCollection
    )

    property_type = bpy.props.PointerProperty(type=LocalPointerCollection)

    @classmethod
    def _register(cls):
        for c in (*_all, *cls.types):
            bpy.utils.register_class(c)

    @classmethod
    def _unregister(cls):
        for c in reversed((*_all, *cls.types)):
            bpy.utils.unregister_class(c)

    @classmethod
    def setup_class(cls):
        cls._register()
        setattr(cls.mount_onto, cls.property_name, cls.property_type)

    @classmethod
    def teardown_class(cls):
        delattr(cls.mount_onto, cls.property_name)
        cls._unregister()


class Test_PointerCollection(_PointerCollectionTest):

    def test(self,):
        raise NotImplementedError()
