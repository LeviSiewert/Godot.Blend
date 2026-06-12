from ..structure.resources import SubresourceCollection, GdSubResource, GdSubResourceNode

def test_base_behavior():
    col = SubresourceCollection()
    res = GdSubResource()
    res.headertype = "TYPETEST"
    res.header_props["type"] = "TYPETEST"
    res.header_props["id"] = "IDTEST"
    col.append(res)
    assert(res in col.by_restype("TYPETEST"))
    assert(not (res in col.by_restype("WRONGTYPE")))
    assert(res == col["IDTEST"])

    # raise Exception(SubresourceCollection, "Tests not yet implimented!")

def test_tree_construction():
    nodea = GdSubResourceNode.new("A", "")
    nodeb = GdSubResourceNode.new("B", "/")
    nodec = GdSubResourceNode.new("C", "/B/")
    noded = GdSubResourceNode.new("D", "/B/")
    
    col = SubresourceCollection()
    col.extend((nodea, nodeb, nodec))
    col.build_tree()
    assert(col.tree_root is nodea)
    assert(nodea.children == (nodeb,))
    assert(nodeb.children == (nodec,noded))