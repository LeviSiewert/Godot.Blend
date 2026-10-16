from .properties import *

from ._test_utils import addon_ensure

class _Base():
    attach = ["test_attr", bpy.types.Scene]
    struct = Properties

    @property
    def value(self)->Properties:
        return getattr(bpy.data.scenes[0], self.attach[0])

    def setup_class(self):
        addon_ensure(True)
        setattr(self.attach[1], self.attach[0], PointerProperty(type=self.struct))

    def teardown_class(self):
        getattr(bpy.data.scenes[0], self.attach[0]).clear()
        delattr(self.attach[1], self.attach[0])
        addon_ensure(False)

class TestSanity(_Base):
    def test(self):
        raise Exception(self.value)

class TestBasics(_Base):
    def test_stringval(self):
        assert len(self.value.data) == 0
        assert len(self.value.bin_string.data) == 0

        self.value.set("a", "value")

        assert len(self.value.data) == 1
        assert len(self.value.bin_string.data) == 1

        assert "value" == self.value.get("a").value

        self.value.clear()

        assert len(self.value.data) == 0
        assert len(self.value.bin_string.data) == 0

    def data(self):
        yield self.value.bin_string, "key", "value"
        yield self.value.bin_int, "key", 0
        yield self.value.bin_int, "key", 1
        yield self.value.bin_float, "key", 0.5
        yield self.value.bin_float, "key", 1.5

    def test_data(self):
        for _bin, _key, _val in self.data():
            try:
                assert len(self.value.data) == 0
                v = self.value.set(_key, _val, wrap=False)

                assert v.name != _key # As is pointer
                assert v.value == _val

                assert self.value.get(_key, wrap=False) == v
                assert len(self.value.data) == 1
                assert len(_bin.data) == 1

                self.value.remove(_key)

                assert len(self.value.data) == 0
                assert len(_bin.data) == 0
                
            except Exception as e :
                raise Exception(dict(self.value.items()), e)