from ..structure import *
from ..resources import grammer
from typing import Type
from lark import Lark

parser = Lark(grammer, maybe_placeholders=True)
transformer = GdType.generate_transformer()()

class ParserTest():
    ''' A lark testing class, takes key as start, parses, transforms and compares against output '''
    _type     : Type 
    lark_key : str 
    expects  : bool 
    input    : str
    output   : Any

    def __init__(self, lark_key:str, expects:bool, input:str, output:Any):
        pass
    def __call__(self):
        try:
            tree = transformer(parser.parse(self.input, start=self.lark_key))
            if self.expects:
                assert(isinstance(tree, self._type))
                assert(tree == self.output)
            else:
                assert(tree != self.output)
        except:
            if self.expects: 
                raise

def test_GdType()->list[ParserTest]:
    """ tests for GdType """
    return [

    ]

def test_GdResource()->list[ParserTest]:
    """ tests for GdResource """
    return [

    ]

def test_GdTyping()->list[ParserTest]:
    """ tests for GdTyping """
    return [

    ]

def test_GdTypingVARIANT()->list[ParserTest]:
    """ tests for GdTypingVARIANT """
    return [

    ]

def test_GdProperty()->list[ParserTest]:
    """ tests for GdProperty """
    return [

    ]

def test_GdValue()->list[ParserTest]:
    """ tests for GdValue """
    return [

    ]

def test__GdValueNull()->list[ParserTest]:
    """ tests for _GdValueNull """
    return [

    ]

def test__GdValueFloat()->list[ParserTest]:
    """ tests for _GdValueFloat """
    return [

    ]

def test__GdValueString()->list[ParserTest]:
    """ tests for _GdValueString """
    return [

    ]

def test__GdValueInteger()->list[ParserTest]:
    """ tests for _GdValueInteger """
    return [

    ]

def test_GdValueExtResource()->list[ParserTest]:
    """ tests for GdValueExtResource """
    return [

    ]

def test_GdValueNodePath()->list[ParserTest]:
    """ tests for GdValueNodePath """
    return [

    ]

def test_GdValueSubResource()->list[ParserTest]:
    """ tests for GdValueSubResource """
    return [

    ]

def test_GdValueStringName()->list[ParserTest]:
    """ tests for GdValueStringName """
    return [

    ]

def test_GdValueArray()->list[ParserTest]:
    """ tests for GdValueArray """
    return [

    ]

def test_GdValueVector2()->list[ParserTest]:
    """ tests for GdValueVector2 """
    return [

    ]

def test_GdValueVector3()->list[ParserTest]:
    """ tests for GdValueVector3 """
    return [

    ]

def test_GdValueVector4()->list[ParserTest]:
    """ tests for GdValueVector4 """
    return [

    ]

def test_GdValueVector2i()->list[ParserTest]:
    """ tests for GdValueVector2i """
    return [

    ]

def test_GdValueVector3i()->list[ParserTest]:
    """ tests for GdValueVector3i """
    return [

    ]

def test_GdValueVector4i()->list[ParserTest]:
    """ tests for GdValueVector4i """
    return [

    ]

def test_GdValueColor()->list[ParserTest]:
    """ tests for GdValueColor """
    return [

    ]

def test_GdValueAABB()->list[ParserTest]:
    """ tests for GdValueAABB """
    return [

    ]

def test_GdValueQuaternion()->list[ParserTest]:
    """ tests for GdValueQuaternion """
    return [

    ]

def test_GdValueTransform3D()->list[ParserTest]:
    """ tests for GdValueTransform3D """
    return [

    ]

def test_GdValuePackedByteArray()->list[ParserTest]:
    """ tests for GdValuePackedByteArray """
    return [
        ParserTest(GdValuePackedByteArray._lark_key, True, "PackedByteArray(\"abc\")", GdValuePackedByteArray([b"a",b"b",b"c"]))
    ]

def test_GdValuePackedInt32Array()->list[ParserTest]:
    """ tests for GdValuePackedInt32Array """
    return [
        ParserTest(GdValuePackedInt32Array._lark_key, True, "PackedInt32Array(0, 1, 10)", GdValuePackedInt32Array([0, 1, 10]))
    ]

def test_GdValuePackedInt64Array()->list[ParserTest]:
    """ tests for GdValuePackedInt64Array """
    return [
        ParserTest(GdValuePackedInt64Array._lark_key, True, "PackedInt64Array(0, 1, 10)", GdValuePackedInt64Array([0, 1, 10]))
    ]


def test_GdValuePackedFloat32Array()->list[ParserTest]:
    """ tests for GdValuePackedFloat32Array """
    return [
        ParserTest(GdValuePackedFloat32Array._lark_key, True, "PackedFloat32Array(0, 1.0, 10.5)", GdValuePackedFloat32Array([0, 1.0, 10.5]))
    ]

def test_GdValuePackedFloat64Array()->list[ParserTest]:
    """ tests for GdValuePackedFloat64Array """
    return [
        ParserTest(GdValuePackedFloat64Array._lark_key, True, "PackedFloat64Array(0, 1.0, 10.5)", GdValuePackedFloat64Array([0, 1.0, 10.5]))
    ]

def test_GdValuePackedStringArray()->list[ParserTest]:
    """ tests for GdValuePackedStringArray """
    return [
        ParserTest(GdValuePackedStringArray._lark_key, True, "PackedStringArray(\"a\", \"bb\", \"\")", GdValuePackedStringArray(["a","bb",""]))
    ]

def test_GdValuePackedVector2Array()->list[ParserTest]:
    """ tests for GdValuePackedVector2Array """
    return [
        ParserTest(GdValuePackedVector2Array._lark_key, True, "PackedVector2Array(0, 0)", GdValuePackedVector2Array([0, 0])),
        ParserTest(GdValuePackedVector2Array._lark_key, True, "PackedVector2AGdValuePackedVector2Array(1, 1, 0, 0)", GdValuePackedVector2Array([1, 1, 0, 0])),
        ParserTest(GdValuePackedVector2Array._lark_key, True, "PackedVector2Array(1, 1, 1, 0, 0, 0)", GdValuePackedVector2Array([GdValueVector2([1, 1]), GdValueVector2([0, 0])] )),
    ]

def test_GdValuePackedVector3Array()->list[ParserTest]:
    """ tests for GdValuePackedVector3Array """
    return [
        ParserTest(GdValuePackedVector3Array._lark_key, True, "PackedVector3Array(0, 0, 1)", GdValuePackedVector3Array([0, 0, 1])),
        ParserTest(GdValuePackedVector3Array._lark_key, True, "PackedVector3AGdValuePackedVector3Array(1, 1, 1, 0, 0, 0)", GdValuePackedVector3Array([1, 1, 1, 0, 0, 0])),
        ParserTest(GdValuePackedVector3Array._lark_key, True, "PackedVector3Array(1, 1, 1, 0, 0, 0)", GdValuePackedVector3Array([GdValueVector3([1, 1, 1]), GdValueVector3([0, 0, 0])] )),
    ]

def test_GdValuePackedVector4Array()->list[ParserTest]:
    """ tests for GdValuePackedVector4Array """
    return [
        ParserTest(GdValuePackedVector4Array._lark_key, True, "PackedVector4Array(0, 0, 0, 1)", GdValuePackedVector4Array([0, 0, 0, 1])),
        ParserTest(GdValuePackedVector4Array._lark_key, True, "PackedVector4AGdValuePackedVector4Array(1, 1, 1, 1, 0, 0, 0, 0)", GdValuePackedVector4Array([1, 1, 1, 1, 0, 0, 0, 0])),
        ParserTest(GdValuePackedVector4Array._lark_key, True, "PackedVector4Array(1, 1, 1, 1, 0, 0, 0, 0)", GdValuePackedVector4Array([GdValueVector4([1, 1, 1, 1,]), GdValueVector4([0, 0, 0, 0])] )),
    ]

def test_GdValuePackedColorArray()->list[ParserTest]:
    """ tests for GdValuePackedColorArray """
    return [
        ParserTest(GdValuePackedColorArray._lark_key, True, "PackedColorArray(0, 0, 0, 1)", GdValuePackedColorArray([0, 0, 0, 1])),
        ParserTest(GdValuePackedColorArray._lark_key, True, "PackedColorArray(1, 1, 1, 1, 0, 0, 0, 0)", GdValuePackedColorArray([1, 1, 1, 1, 0, 0, 0, 0])),
        ParserTest(GdValuePackedColorArray._lark_key, True, "PackedColorArray(1, 1, 1, 1, 0, 0, 0, 0)", GdValuePackedColorArray([GdValueColor([1, 1, 1, 1,]), GdValueColor([0, 0, 0, 0])] )),
    ]

def test_GdValueDictionary()->list[ParserTest]:
    """ tests for GdValueDictionary """
    return [
        ParserTest(GdValueDictionary._lark_key, True, "{Null:Null}", GdValueDictionary({None:None}, (VARIANT,VARIANT))),
        ParserTest(GdValueDictionary._lark_key_explicit, True, "Dictionary[Variant,Variant]({Null:Null})", GdValueDictionary({None:None}, (VARIANT,VARIANT))),

        ParserTest(GdValueDictionary._lark_key, True, "{}", GdValueDictionary({}, (VARIANT,VARIANT))),
        ParserTest(GdValueDictionary._lark_key_explicit, True, "Dictionary[Variant,Variant]({})", GdValueDictionary({None:None}, (VARIANT,VARIANT))),
    ]

# def test__packed_vector2()->list[ParserTest]:
#     """ tests for _packed_vector2 """
#     return [
#         ParserTest(_packed_vector2._lark_key, True, "[0.0, 0.0, 0.0]", _packed_vector2([0.0, 0.0], VARIANT)),
#     ]

# def test__packed_vector3()->list[ParserTest]:
#     """ tests for _packed_vector3 """
#     return [
#         ParserTest(_packed_vector3._lark_key, True, "[0.0, 0.0, 0.0]", _packed_vector3([0.0, 0.0, 0.0], VARIANT)),
#     ]

# def test__packed_vector4()->list[ParserTest]:
#     """ tests for _packed_vector4 """
#     return [
#         ParserTest(_packed_vector4._lark_key, True, "[0.0, 0.0, 0.0, 0.0]", _packed_vector4([0.0, 0.0, 0.0, 0.0], VARIANT)),
#     ]

# def test__packed_color()->list[ParserTest]:
#     """ tests for _packed_color """
#     return [
#         ParserTest(_packed_color._lark_key, True, "[0.0, 0.0, 0.0, 0.0]", _packed_color([0.0, 0.0, 0.0, 0.0], VARIANT)),
#     ]

