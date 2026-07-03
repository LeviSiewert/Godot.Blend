
from typing import Generator, Type, Any

from ....transformers.tscn import (
    gd_to_py_transformer,
    py_to_gd_transformer,
    GdToPyContext,
    PyToGdContext,
    make_parser,
)

from ....core.structure import (
    ResourceSettings,
    ResourceTres,
    ResourceScene,
    SubResource,
    SubResourceCollection,
    Node,
    NodeCollection,
    Category,
    CategoryCollection,
    ExtReference,
    ExtReferenceCollection,
    EditFlag,
    EditFlagCollection,
    GdType,
    GdTypeValueSet,
    Signal,
    SignalCollection,
)

_parser_cache = {}
def make_parser_cached(key):
    if res:=_parser_cache.get(key,None):
        return res
    res = make_parser(key)
    _parser_cache[key] = res
    return res

class _StructureTest[T:Type]():
    _type : Type[T]
    _parser_key : str

    def data(self,)->Generator[str,T]:
        raise NotImplementedError()
        yield

    def _yield_gd_to_py(self,)->Generator[tuple[Any,Any]]:
        for txt, obj in self.data():
            parsed = make_parser_cached(self._parser_key).parse(txt)
            res = gd_to_py_transformer.transform_tree(self.make_gdtopy_context(), parsed)
            yield obj, res

    def _yield_py_to_gd(self,)->Generator[tuple[str,str]]:
        for txt, obj in self.data():
            parsed = make_parser_cached(self._parser_key).parse(txt)
            res = py_to_gd_transformer.transform_tree(self.make_pytogd_context(), obj)
            yield txt, res
    
    def test_py_to_gd(self,):
        for a,b in self._yield_py_to_gd():
            self.gd_compare(a,b)
    
    def test_gd_to_py(self,):
        for a,b in self._yield_gd_to_py():
            self.py_compare(a,b)
    
    def make_pytogd_context(self,)->PyToGdContext:
        return PyToGdContext()

    def make_gdtopy_context(self,)->GdToPyContext:
        return GdToPyContext()

    def py_compare(self, a:T, b:T):
        assert (isinstance(b, self._type))
        assert (a == b)

    def gd_compare(self, a:str, b:str):
        assert(a.replace("/n","").replace(" ","") == b.replace("/n","").replace(" ",""))


class Test_ResourceSettings(_StructureTest):
    _parser_key = "resource_settings"
    _type = ResourceSettings

class Test_ResourceTres(_StructureTest):
    _parser_key = "resource_tres"
    _type = ResourceTres

class Test_ResourceScene(_StructureTest):
    _parser_key = "resource_scene"
    _type = ResourceScene

class Test_SubResource(_StructureTest):
    _parser_key = "sub_resource"
    _type = SubResource

class Test_SubResourceCollection(_StructureTest):
    _parser_key = "sub_resources"
    _type = SubResourceCollection

class Test_Node(_StructureTest):
    _parser_key = "node_resource"
    _type = Node

class Test_NodeCollection(_StructureTest):
    _parser_key = "node_resources"
    _type = NodeCollection

class Test_Category(_StructureTest):
    _parser_key = "cat_resource"
    _type = Category

class Test_CategoryCollection(_StructureTest):
    _parser_key = "cat_resources"
    _type = CategoryCollection

class Test_ExtReference(_StructureTest):
    _parser_key = "ext_reference"
    _type = ExtReference

    def setup_class(self,):
        raise NotImplementedError()
        self._project = Project.construct()

    def make_gdtopy_context(self):
        c = GdToPyContext()
        return c

    def make_pytogd_context(self):
        c = PyToGdContext()
        return c
        
    def data(self):
        txt = '''[ext_resource type="PackedScene" uid="uid://bvshg3b45tq5b" path="res://assets/blender.glb.tscn" id="1_0xe7n"] '''
        res = ExtReference(type="PackedScene", uid=self._project.resources.get("uid://bvshg3b45tq5b"), path=self._project.files.get("res://assets/blender.glb.tscn"), id="1_0xe7n")
        yield txt,res

        txt = '''[ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_w5rjj"] '''
        res = ExtReference(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_w5rjj")
        yield txt,res
        
        txt = '''[ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="3_7d4mc"] '''
        res = ExtReference(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="3_7d4mc")
        yield txt,res
    

class Test_ExtReferenceCollection(Test_ExtReference):
    _type = ExtReferenceCollection
    _parser_key = "ext_references"


    def data():
        txt = '''
[ext_resource type="PackedScene" uid="uid://bvshg3b45tq5b" path="res://assets/blender.glb.tscn" id="1_0xe7n"]
[ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_w5rjj"]
[ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="3_7d4mc"]
'''     
        res = ExtReferenceCollection(
            ExtReference(type="PackedScene", uid="uid://bvshg3b45tq5b", path="res://assets/blender.glb.tscn" id="1_0xe7n"),
            ExtReference(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb" id="1_w5rjj"),
            ExtReference(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd" id="3_7d4mc"),
        )
        yield txt, res

class Test_EditFlag(_StructureTest):
    _type = EditFlag
    _parser_key = "edit_flag"
    def data(self,):
        txt = ''' [editable path="GlbInhheritedEditable"] '''
        res = EditFlag("GlbInhheritedEditable")
        yield txt, res
        
        txt = ''' [editable path="GlbEditable"] '''
        res = EditFlag("GlbEditable")
        yield txt, res
        
        txt = ''' [editable path="GlbEditableAddScript"] '''
        res = EditFlag("GlbEditableAddScript")
        yield txt, res
        
        txt = ''' [editable path="GlbEditableEditProp"] ''' 
        res = EditFlag("GlbEditableEditProp")
        yield txt, res

class Test_EditFlagCollection(_StructureTest):
    _type = EditFlagCollection
    _parser_key = "edit_flag"
    def data(self,):
        txt = '''
[editable path="GlbInhheritedEditable"]
[editable path="GlbEditable"]
[editable path="GlbEditableAddScript"]
[editable path="GlbEditableEditProp"]
''' 
        res = EditFlagCollection(
            EditFlag("GlbInhheritedEditable").
            EditFlag("GlbEditable").
            EditFlag("GlbEditableAddScript").
            EditFlag("GlbEditableEditProp").
        )
        yield txt, res

class Test_GdType(_StructureTest):
    ...

class Test_GdTypeValueSet(_StructureTest):
    ...

class Test_Signal(_StructureTest):
    _type = Signal
    def data(self,):
        
        txt = '''[connection signal="body_entered" from="." to="." method="_on_door_body_entered"]'''     
        res = Signal(signal="body_entered", fr=".", to=".", method="_on_door_body_entered"),
        yield txt, res

        txt = '''[connection signal="body_exited" from="." to="." method="_on_door_body_exited"]'''
        res =Signal(signal="body_exited", fr=".", to=".", method="_on_door_body_exited"),
        yield txt, res
    

class Test_SignalCollection(_StructureTest):
    _type = SignalCollection
    _parser_key = "signals"

    def data(self,):
        txt = '''
[connection signal="body_entered" from="." to="." method="_on_door_body_entered"]
[connection signal="body_exited" from="." to="." method="_on_door_body_exited"]
'''     
        res = SignalCollection(
            Signal(signal="body_entered", fr=".", to=".", method="_on_door_body_entered"),
            Signal(signal="body_exited", fr=".", to=".", method="_on_door_body_exited"),
        )

        yield txt, res

