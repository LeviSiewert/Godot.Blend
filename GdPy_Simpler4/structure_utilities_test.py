from .structure_utilities import copy, deepcopy, check_recursion, singulate, localize, format_extresources

# class Test_Normalize:
#     # Test Singulation
#     # Test Inlcusion/Localization
#     # Test instance_load & Fix
#     # Test Scope limitation
#     # Test session join?s


#     class Test_Project:

#         def test_resource_singulation_localization(self):
#             Sr0 = Node(name="Sr0")
#             R0 = Resource.construct(name="R0", uid="R0", subresources=[Sr0])
#             R1 = Resource.construct(name="R1", uid="R1", subresources=[Sr0])
#             P = Project.construct(resources=[R0,R1])

#             P.normalize(singulate=True, localize=True, in_place=True)

#             Sr0_a = R0.subresources[0]
#             Sr0_b = R1.subresources[0]

#             # structure declaration:
#             assert not (Sr0_a is Sr0_b)
#             assert (Sr0_a is Sr0) or (Sr0_b is Sr0)


#             assert Sr0_a in R0.subresources
#             assert Sr0_a.context._extends is R0.subresources.context
#             assert len(R0.subresources) == 1
#             assert Sr0_b in R1.subresources
#             assert Sr0_b.context._extends is R1.subresources.context
#             assert len(R1.subresources) == 1

#         def test_implied_resource_singulation_localization(self):
#             Sr0 = Node(name="Sr0")
#             Sr1_a = Node(name="Sr1", properties={"ref":Sr0})
#             R0 = Resource.construct(name="R0", uid="R0", subresources=[Sr1_a])
#             Sr1_b = Node(name="Sr1", properties={"ref":Sr0})
#             R1 = Resource.construct(name="R1", uid="R1", subresources=[Sr1_b])
#             P = Project.construct(resources=[R0,R1])

#             P.normalize(singulate=True, localize=True, in_place=True)

#             Sr0_a = Sr1_a.properties["ref"]
#             Sr0_b = Sr1_b.properties["ref"]

#             # structure declaration:
#             assert not (Sr0_a is Sr0_b)
#             assert (Sr0_a is Sr0) or (Sr0_b is Sr0)

#             assert Sr0_a in R0.subresources
#             assert Sr0_a.context._extends is R0.subresources.context
#             assert len(R0.subresources) == 2
#             assert Sr0_b in R1.subresources
#             assert Sr0_b.context._extends is R1.subresources.context
#             assert len(R1.subresources) == 2

#         def test_node_singulation_localization(self):
#             ## Note; Root Node / File's root is notated with (Sn) for Scene-node
#             N0 = Node(name="N0")
#             Sn0 = Node.construct(name="Sn0", uid="Sn0", children=[N0])
#             Sn1 = Node.construct(name="Sn1", uid="Sn1", children=[N0])
#             P = Project.construct(resources=[Sn0,Sn1])

#             P.normalize(singulate=True, localize=True, in_place=True)

#             N0_a = Sn0.children[0]
#             N0_b = Sn1.children[0]

#             # structure declaration:
#             assert not (N0_a is N0_b)
#             assert (N0_a is N0) or (N0_b is N0)

#             # structure management;
#             assert N0_a in Sn0.nodes
#             assert len(Sn0.children) == 1
#             assert len(Sn0.nodes) == 1 
#             assert N0_a.context._extends is Sn0.children.context

#             assert N0_b in Sn1.nodes
#             assert len(Sn1.children) == 1
#             assert len(Sn1.nodes) == 1
#             assert N0_b.context._extends is Sn1.children.context

#         def test_implied_node_singulation_localization(self):
#             # Node-depth implied singulate-localize
#             N0 = Node(name="N0")
#             N1_a = Node(name="N1", children=[N0])
#             N1_b = Node(name="N1", children=[N0])
#             Sn0 = Node.construct(name="Sn0", uid="Sn0", children=[N1_a])
#             Sn1 = Node.construct(name="Sn1", uid="Sn1", children=[N1_b])

#             P = Project.construct(resources=[Sn0,Sn1])

#             P.normalize(singulate=True, localize=True, in_place=True)

#             N0_a = N1_a.children[0]
#             N0_b = N1_b.children[0]

#             assert not (N0_a is N0_b)
#             assert (N0_a is N0) or (N0_b is N0)

#             assert N0_a in N1_a.children
#             assert len(Sn0.nodes) == 2
#             assert len(N1_a.children) == 1
#             assert N0_a.context._extends is N1_a.children.context

#             assert N0_b in N1_b.children
#             assert len(Sn0.nodes) == 2
#             assert len(N1_b.children) == 1
#             assert N0_b.context._extends is N1_b.children.context
            
#         def test_node_instance_singulation_localization(self):
#             ## Basically check if nothing happens to a directly or semi-directly referenced resource, w/out fix_instnace
#             Sn0 = Node.construct(name="Sn0", uid="Sn0")
#             Sn1 = Node.construct(name="Sn1", uid="Sn1", instance=Sn0)
#             Sn2 = Node.construct(name="Sn2", uid="Sn2", instance=Sn0)
#             P = Project.construct(resources = [Sn1, Sn2])

#             P.normalize()

#             assert Sn1.instance is Sn0
#             assert Sn2.instance is Sn0

#             assert len(P.resources) == 3
#             assert Sn0 in P.resources

#         def test_implied_node_instance_resource_inclusion():
#             Sn0 = Node.construct(name="Sn0", uid="Sn0")
#             N0 = Node.construct(name="N1", instance=Sn0)

#             Sn1 = Node.construct(name="Sn1", uid="Sn1", children=[N0])
#             Sn2 = Node.construct(name="Sn2", uid="Sn2", children=[N0])
#             P = Project.construct(resources = [Sn1, Sn2])

#             assert Sn1.children == Sn2.children

#             P.normalize()

#             assert P.resources == [Sn0,Sn1,Sn2]
#             assert Sn1.children != Sn2.children

#         def test_extresource_construction():
#             ## Normalization includes extresource construction??
#             pass

#     # class Test_Nodes():
#     #     def test_fix_instance(self):
#     #         raise NotImplementedError()

#     #     def test_fix_instance_noload(self):
#     #         raise NotImplementedError()

#     # class Test_SubResource:
#     #     def test_normalized_inclusion(self):
#     #         r = Resource(uid="id")
#     #         sr = Resource()
#     #         r.properties["a"] = sr
#     #         r.normalize()
#     #         assert sr in r.sub_resources
#     #         assert sr.context._extends is r.context

#     #     def test_normalized_inclusion_nested(self):
#     #         r = Resource(uid="id")
#     #         sr1 = Resource()
#     #         sr2 = Resource()
#     #         r.properties["a"] = sr1
#     #         sr1.properties["a"] = sr2
#     #         r.normalize()
#     #         assert sr1 in r.sub_resources
#     #         assert sr2 in r.sub_resources
#     #         assert sr1.context._extends is r.context
#     #         assert sr2.context._extends is r.context
            
#     # class Test_ExtResource:        
#     #     def test_normalized_conversion(self):
#     #         r1 = Resource("uid_a")
#     #         r2 = Resource("uid_b")
#     #         r1.properties["a"] = r2

#     #         r1.normalize()

#     #         assert len(r1.ext_resources) == 1
#     #         assert tuple(r1.ext_resources.values())[0]._resource.sref is r2
        
#     #     def test_normalized_conversion_nested(self):
#     #         r1 = Resource("uid_a")
#     #         r2 = Resource("uid_b")
#     #         r3 = Resource("uid_b")
#     #         r1.properties["a"] = r2
#     #         r2.properties["a"] = r3

#     #         r1.normalize()

#     #         assert len(r1.ext_resources) == 1
#     #         assert tuple(r1.ext_resources.values())[0]._resource.sref is r2
#     #         assert len(r2.ext_resources) == 1
#     #         assert tuple(r2.ext_resources.values())[0]._resource.sref is r3

# class Test_File:...

# class Test_Project:...

# class Test_Structure_Normalize:...