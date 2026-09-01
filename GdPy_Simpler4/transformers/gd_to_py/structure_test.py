from ...core.structure import Resource, ExtResource, Node
from ._test_utils import _StructureTest

class Test_Resource():

    class Test_Simple(_StructureTest):
        _parser_key = "start"
        def data(self):
            txt = ''' 
[gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"] 
[resource]
val = "VAL"
            '''
            res = Resource(type="Resource", uid="b52f332102m2l", properties={"val":"VAL"})
            yield txt, res

    
    class Test_NestedSubRes(_StructureTest):
        _parser_key = "start"
        def data(self):
            txt = '''
[gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"]

[sub_resource type="Resource" id="a"]

[sub_resource type="Resource" id="b"]
reference=SubResource("a")

[sub_resource type="Resource" id="c"]
reference=SubResource("b")

[resource]
reference=SubResource("c")
'''
            res = Resource(type="Resource", uid="uid://b52f332102m2l", properties={
                "reference": Resource(type="Resource", id = "c", properties={
                    "reference": Resource(type="Resource", id = "b", properties={
                        "reference": Resource(type="Resource", id = "a")
                    })
                })
            }) 
            yield txt, res


    class Test_ExtRes(_StructureTest):
        _parser_key = "start"
        def data(self):
            txt = """
[gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"]

[ext_resource type="Resource" uid="uid://cjkvk7qbv5oby" path="res://ext_res.tres" id="1_2f6dx"]

[resource]
reference = ExtResource("1_2f6dx")
"""
            extres = ExtResource(type="Resource", resource="uid://cjkvk7qbv5oby", file="res://ext_res.tres", id="1_2f6dx")
            res = Resource(
                ext_resources=[extres],
                properties={"reference":extres}
            )
            yield txt, res
    
    
    class Test_ExtResNestedSubRes(_StructureTest):
        _parser_key = "start"
        def data(self):
            txt = """
[gd_resource type="Resource" format=3 uid="uid://b52f332102m2l"]

[ext_resource type="Resource" uid="uid://cjkvk7qbv5oby" path="res://ext_res.tres" id="1_2f6dx"]

[sub_resource type="Resource" id="a"]
reference = ExtResource("1_2f6dx")

[resource]
reference=SubResource("a")
"""
            extres = ExtResource(type="Resource", resource="uid://cjkvk7qbv5oby", file="res://ext_res.tres", id="1_2f6dx")
            a = Resource(id="a", properties={"reference":extres})
            res = Resource(
                ext_resources=[extres],
                properties={"reference":a}
            )
            yield txt, res

