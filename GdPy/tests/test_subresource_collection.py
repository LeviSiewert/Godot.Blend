from ..structure.sub_resource_collections import CollectionSubRes, CollectionNodeRes
from ..structure.sub_resources import SubResourceNode, SubResource


# def test_base_behavior():
#     col = CollectionSubRes()
#     res = SubResource()
#     res.restype = "TYPETEST"
#     res.type = "TYPETEST"
#     res.id = "IDTEST"
    # col.append(res)
    # assert(res in list(col.by_restype("TYPETEST")))
    # assert(not (res in col.by_restype("WRONGTYPE")))
    # assert(res == col["IDTEST"])

    # raise Exception(SubresourceCollection, "Tests not yet implimented!")

def test_tree_construction():

    nodea = SubResourceNode.new(name="A", parent=None)
    nodeb = SubResourceNode.new(name="B", parent=".")
    nodec = SubResourceNode.new(name="C", parent="B")
    noded = SubResourceNode.new(name="D", parent="B")

    col = CollectionNodeRes()
    col.extend((nodea, nodeb, nodec, noded))
    col.build_tree()
    assert(col.root is nodea)
    assert(nodea.get_children() == (nodeb,))
    assert(nodeb.get_children() == (nodec,noded))