from ...structure.core import PropertyCollection

def test_behavior():
    props = PropertyCollection()
    props.extend({"a":"A", "b":"B"}.items())
    assert(props["a"] == "A")
    assert(props["b"] == "B")
    # raise Exception(PropertyCollection, "Tests not yet implimented!")