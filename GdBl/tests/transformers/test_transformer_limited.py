from ...structure.transformers.core import TransformerModule, Transformer
from ...structure.core.primitives import BlContext

class TrfmString(TransformerModule):
    _terminal = True

    @classmethod
    def get_gdbl_keys(cls):
        return (str,)
    
    def to_blender(self, c:BlContext, key, gd_item, _children):
        assert(key in self.get_gdbl_keys())
        assert(isinstance(gd_item,str))
        assert(len(_children) == 0)
        yield
        assert(len(_children) == 0)
        return str(gd_item)

    def fr_blender(self, c:BlContext, key, bl_item, _children):
        assert(key in self.get_gdbl_keys())
        assert(isinstance(bl_item,str))
        assert(len(_children) == 0)
        yield
        assert(len(_children) == 0)
        return str(bl_item)

class TrfmInt(TransformerModule):
    _terminal = True

    @classmethod
    def get_gdbl_keys(cls):
        return (int,)
    
    def to_blender(self, c:BlContext, key, gd_item, _children):
        return gd_item+1

    def fr_blender(self, c:BlContext, key, bl_item, _children):
        return bl_item-1

class TrfmArray():
    @classmethod
    def get_gdbl_keys(cls):
        return (list,)

    def to_blender(self, c:BlContext, key, gd_item, _children):
        assert(key in self.get_gdbl_keys())
        assert(isinstance(gd_item,list))
        assert(len(_children) == 0)
        
        yield tuple(gd_item)
        
        assert(len(_children) == 3)
        return list(_children.values())

    def fr_blender(self, c:BlContext, key, bl_item, _children):
        assert(key in self.get_gdbl_keys())
        assert(isinstance(bl_item,list))
        assert(len(_children) == 0)
        
        yield tuple(bl_item)

        assert(len(_children) == 3)
        return list(_children.values())

def test_equivilents():
    transformer = Transformer([TrfmString,TrfmArray])
    i = ["a","b","c"]
    c = BlContext()
    to_res = transformer.to_blender(c,i)
    fr_res = transformer.fr_blender(c,i)
    assert(to_res)
    assert(fr_res)
    assert(to_res == fr_res)
    assert(to_res == i)
    assert(fr_res == i)
    
def test_altered():
    transformer = Transformer([TrfmString,TrfmArray,TrfmInt])
    i = [1,2,3]
    o = [2,3,4]
    c = BlContext()
    assert(transformer.to_blender(c,i) == o)
    assert(transformer.fr_blender(c,o) == i)