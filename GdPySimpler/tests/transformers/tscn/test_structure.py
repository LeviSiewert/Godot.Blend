
from typing import Generator, Type, Any

from ....transformers.tscn import (
    gd_to_py_transformer,
    py_to_gd_transformer,
    GdToPyContext,
    PyToGdContext,
    make_parser,
)

from ....core.structure import (
    Project,
    FileLocal,
    FileForeign,
    ResourceScript,
    ResourceSettings,
    ResourceTres,
    ResourceScene,
    SubResource,
    SubResourceCollection,
    Node,
    NodeCollection,
    Category,
    CategoryCollection,
    ExtResourceRef,
    ExtResourceRefCollection,
    EditFlag,
    EditFlagCollection,
    GdType,
    GdTypeValueSet,
    SignalNotation,
    SignalNotationCollection,
    ExtResource,
    SubResourceRef,
    RID,
)

from ....core.values import (
    NodePath,
    StringName,
    Object,
    Dictionary,
    Array,
    Vector2i,
    Vector3i,
    Vector4i,
    Rect2i,
    Vector2,
    Vector3,
    Vector4,
    Rect2,
    Plane,
    Color,
    AABB,
    Quaternion,
    Transform2D,
    Transform3D,
    Basis,
    PackedInt32Array,
    PackedInt64Array,
    PackedFloat32Array,
    PackedFloat64Array,
    PackedStringArray,
    PackedVector2Array,
    PackedVector3Array,
    PackedVector4Array,
    PackedColorArray,
    PackedByteArray,
)

from ._utils import _StructureTest

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

class Test_ExtResourceRef(_StructureTest):
    _parser_key = "ext_reference"
    _type = ExtResourceRef

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
        res = ExtResourceRef(type="PackedScene", uid=self._project.resources.get("uid://bvshg3b45tq5b"), path=self._project.files.get("res://assets/blender.glb.tscn"), id="1_0xe7n")
        yield txt,res

        txt = '''[ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_w5rjj"] '''
        res = ExtResourceRef(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_w5rjj")
        yield txt,res
        
        txt = '''[ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="3_7d4mc"] '''
        res = ExtResourceRef(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="3_7d4mc")
        yield txt,res
    

class Test_ExtResourceRefCollection(Test_ExtResourceRef):
    _type = ExtResourceRefCollection
    _parser_key = "ext_references"


    def data():
        txt = '''
[ext_resource type="PackedScene" uid="uid://bvshg3b45tq5b" path="res://assets/blender.glb.tscn" id="1_0xe7n"]
[ext_resource type="PackedScene" uid="uid://cocfi2vsn5qt2" path="res://assets/blender.glb" id="1_w5rjj"]
[ext_resource type="Script" uid="uid://cr1tpol7u62kd" path="res://assets/script.gd" id="3_7d4mc"]
'''     
        res = ExtResourceRefCollection(
            ExtResourceRef(type="PackedScene", uid="uid://bvshg3b45tq5b", path="res://assets/blender.glb.tscn", id="1_0xe7n"),
            ExtResourceRef(type="PackedScene", uid="uid://cocfi2vsn5qt2", path="res://assets/blender.glb", id="1_w5rjj"),
            ExtResourceRef(type="Script", uid="uid://cr1tpol7u62kd", path="res://assets/script.gd", id="3_7d4mc"),
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
            EditFlag("GlbInhheritedEditable"),
            EditFlag("GlbEditable"),
            EditFlag("GlbEditableAddScript"),
            EditFlag("GlbEditableEditProp"),
        )
        yield txt, res

class Test_GdType(_StructureTest):
    _type = GdType 
    _parser_key = 'type_anno' 
    cases = {
        "Dictionary" : Dictionary,
        "Array" : Array,
        "Vector2i" : Vector2i,
        "Vector3i" : Vector3i,
        "Vector4i" : Vector4i,
        "Vector2" : Vector2,
        "Vector3" : Vector3,
        "Vector4" : Vector4,
        "Rect2" : Rect2,
        "Rect2i" : Rect2i,
        "Plane" : Plane,
        "Color" : Color,
        "AABB" : AABB,
        "Quaternion" : Quaternion,
        "Transform2D" : Transform2D,
        "Transform3D" : Transform3D,
        "Basis" : Basis,
        "PackedByteArray" : PackedByteArray,
        "PackedInt32Array" : PackedInt32Array,
        "PackedInt64Array" : PackedInt64Array,
        "PackedFloat32Array" : PackedFloat32Array,
        "PackedFloat64Array" : PackedFloat64Array,
        "PackedStringArray" : PackedStringArray,
        "PackedVector2Array" : PackedVector2Array,
        "PackedVector3Array" : PackedVector3Array,
        "PackedVector4Array" : PackedVector4Array,
        "PackedColorArray" : PackedColorArray,

        "Object" : Object,
        "Object(Type)" : Object(type == Type),

        'NodePath[ExtResource("ABC")]' : NodePath(None, typing=ExtResource("ABC")),
        'NodePath': NodePath,
        
        'SubResource("ABC")' : SubResourceRef("ABC"),
        'SubResource' : SubResourceRef,
        
        'ExtResource("ABC")' : ExtResource("ABC"),
        'ExtResource' : ExtResource,
        
        'RID("ABC")' : RID("ABC"),
        'RID' : RID,
    }
    def data(self,):
        for k,v in self.cases.items():
            yield k,v

class Test_GdTypeValueSet(_StructureTest):
    _type = GdTypeValueSet 
    _parser_key = 'type_anno'
    
    def data(self):
        Test_GdType.cases
        keys = Test_GdType.cases.keys()

        for i in range(int(Test_GdType.cases.keys()/2)):
            txt_a, res_a = keys[i]
            txt_b, res_b = keys[i+1]
            yield f'[{txt_a}, {txt_b}]', GdTypeValueSet(res_a, res_b)


class Test_SignalNotation(_StructureTest):
    _type = SignalNotation
    _parser_key = "signal"
    def data(self,):
        
        txt = '''[connection signal="body_entered" from="." to="." method="_on_door_body_entered"]'''     
        res = SignalNotation(signal="body_entered", fr=".", to=".", method="_on_door_body_entered"),
        yield txt, res

        txt = '''[connection signal="body_exited" from="." to="." method="_on_door_body_exited"]'''
        res =SignalNotation(signal="body_exited", fr=".", to=".", method="_on_door_body_exited"),
        yield txt, res
    

class Test_SignalNotationCollection(_StructureTest):
    _type = SignalNotationCollection
    _parser_key = "signals"

    def data(self,):
        txt = '''
[connection signal="body_entered" from="." to="." method="_on_door_body_entered"]
[connection signal="body_exited" from="." to="." method="_on_door_body_exited"]
'''     
        res = SignalNotationCollection(
            SignalNotation(signal="body_entered", fr=".", to=".", method="_on_door_body_entered"),
            SignalNotation(signal="body_exited", fr=".", to=".", method="_on_door_body_exited"),
        )

        yield txt, res

