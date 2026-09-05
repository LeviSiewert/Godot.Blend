from ._transformer import GdToPyModule, PyToGdModule, GdToPyRuleset, PyToGdRuleset

from ...core.structure_promise import StructReference, RefType

class GdToPy_StructReference(GdToPyModule):
    _keys = ("subresourceref", "extresourceref", "rid",)

    def transform(self, c, node):
        key : str = c.key.get()
        yield node.children
        ref_id : str = c.children.get() 
        ref_type : RefType = None

        match key:
            case "subresourceref":
                ref_type = RefType.SUB_RESOURCE
            case "extresourceref":
                ref_type = RefType.EXT_RESOURCE
            case "rid":
                ref_type = RefType.RESOURCE

        return StructReference(key=ref_id, ref_type=ref_type)

class PyToGd_StructReference(PyToGdModule):
    _keys = (StructReference,)

    def transform(self, c, node:StructReference):
        match node.ref_type:
            
            case RefType.SUB_RESOURCE:
                return f'SubResource("{node.key}")'
            case RefType.EXT_RESOURCE:
                return f'ExtResource("{node.key}")'

            case RefType.RID:
                return f'RID("{node.key}")'
            case RefType.RESOURCE:
                return f'RID("{node.key}")'
                # raise Exception("non-normalized structure!, Resource ref should be converted to ExtResource before serialization")
            case RefType.FILE:
                raise Exception("non-normalized structure!, file ref should be converted to RID before serialization")
            case RefType.DEFER:
                raise Exception("non-normalized structure!, Non-fullfilled structureReference")
            case _:
                raise Exception("UNKNWON REF TYPE:", node.ref_type)


gd_to_py_ruleset = GdToPyRuleset("STD_Resources", *[
    GdToPy_StructReference,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Resources", *[
    PyToGd_StructReference,
])