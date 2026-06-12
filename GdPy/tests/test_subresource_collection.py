from ..structure.resources import SubresourceCollection, SubresourceNodeCollection, GdSubResource, GdSubResourceNode

def test_base_behavior():
    col = SubresourceCollection()
    res = GdSubResource()
    res.restype = "TYPETEST"
    res.header_props["type"] = "TYPETEST"
    res.header_props["id"] = "IDTEST"
    col.append(res)
    assert(res in list(col.by_restype("TYPETEST")))
    assert(not (res in col.by_restype("WRONGTYPE")))
    assert(res == col["IDTEST"])

    # raise Exception(SubresourceCollection, "Tests not yet implimented!")

def test_tree_construction():

    nodea = GdSubResourceNode.new("A", None)
    nodeb = GdSubResourceNode.new("B", ".")
    nodec = GdSubResourceNode.new("C", "B")
    noded = GdSubResourceNode.new("D", "B")

    col = SubresourceNodeCollection()
    col.extend((nodea, nodeb, nodec, noded))
    col.build_tree()
    assert(col.root is nodea)
    assert(nodea.get_children() == (nodeb,))
    assert(nodeb.get_children() == (nodec,noded))