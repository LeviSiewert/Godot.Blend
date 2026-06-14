from ...structure.transformers.core import TransformerModule, Transformer
from ...structure.core.primitives import BlContext

from ...structure.transformers.properties import TrfmProperty
from ..utils import BlenderPytest

class TestAltered(BlenderPytest):
    def test_primary(self):
        c = BlContext()
        transformer = Transformer([TrfmProperty])
        raise Exception("Not yet implimented")

    