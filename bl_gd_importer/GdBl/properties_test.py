from .properties import *

from ._test_utils import addon_ensure

class _Base():
    attach = ["test_attr", bpy.types.Scene]
    struct = Properties

    def setup(self):
        addon_ensure(True)
        setattr(self.attach[1], self.attach[0], Properties)

    def teardown(self):
        delattr(self.attach[1], self.attach[0])
        addon_ensure(False)

