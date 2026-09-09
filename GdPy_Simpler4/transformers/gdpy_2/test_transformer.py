# from __future__ import annotations
# from typing import Iterable, Generator, Any, Callable
# from inspect import isgenerator

from .transformer import *



def test_basic():
    class _transformer(Transformer):
        def match(self, session, node):
            return True
        def transform(self, session, node:list)->Generator:
            node.append("PRE")

            res = yield STEP("A", "a", caching=False)
            node.append(res)

            res = yield STEP("B", "b", caching=False)
            node.append(res)

            res = yield STEP("C", "c", caching=True)
            node.append(res)

            return "D"

    session = Session([TransformerSet("", [_transformer])])
    node = []
    assert "a" == session.transform(node, step="A")
    assert "b" == session.transform(node, step="B")
    assert "c" == session.transform(node, step="C")
    assert "D" == session.transform(node)

    assert "c" == session.get_cache(id(node), create=False).get("C", None)
    assert None == session.get_cache(id(node), create=False).get("A", None)

    node == ["PRE", "A", "B", "C"]



# class N():
#     name : str
#     children : list[N]
#     def __init__(self, name:str, children:Iterable[N]=tuple()):
#         self.name = name
#         self.children = list(children)

#     def __repr__(self):
#         return f'Node("{self.name}" children={len(self.children)})'

# class N_Transformer(TransformerModule):
#     def __init__(self, tool:Callable):
#         self.transform = tool
#     # def transform(self, session, node):
#     #     res = yield from self.tool(session, node)
#     #     return res
#     def match(self, obj)->bool:
#         return True

# class Test_Basic:
#     def test_construction(self):
#         session = Session([TransformerSet("basic", TransformerModule())])

# def make_tree():
#     return N("A", [
#         N("B",[
#             N("B2"),
#         ]),
#         N("C"),
#         N("D", [
#             N("D1"),
#         ]),
#     ])

# class Test_Flags:
#     class Test_TRANSFORM:
#         def test_basic(self):
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 new_children = []
#                 for c in node.children:
#                     child = yield TRANFORM(c)
#                     new_children.append(child)
#                 assert new_children == node.children

#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#     class Test_TRANFORM_CHILDREN:
#         def test_basic(self):
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 children = yield TRANFORM_CHILDREN(node.children)
#                 assert isinstance(children, list)
#                 assert len(children) == len(node.children)
#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#     class Test_TRANFORM_CHILDREN_GENERATOR:
#         def test_basic(self):
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 children = yield TRANFORM_CHILDREN_GENERATOR(node.children)
#                 assert isinstance(children, Generator)
#                 children = tuple(children)
#                 assert len(children) == len(node.children)
#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())
        
#     class Test_STEP:
#         def test_basic(self):
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 yield STEP("ONE", "one")
#                 yield STEP("TWO", "two")
#                 yield STEP("THREE", "three")
#                 return "FINAL"
                
#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             tree = make_tree()

#             res = session.transform(tree, step = "ONE")
#             assert res == "one"
#             assert "ONE" in session.memo[id(tree)][1].keys()
#             assert not "TWO" in session.memo[id(tree)][1].keys()

#             res = session.transform(tree, step = "TWO")
#             # assert "ONE" in session.memo[id(tree)][1].keys()
#             # assert "TWO" in session.memo[id(tree)][1].keys()
#             raise Exception(session.memo)
#             assert res == "two"

#             # res = session.transform(tree)
#             # ## res in this case is final return
#             # assert res is None
#             # assert "THREE" in session.memo[id(tree)][1].keys()
#             # assert "RETURN" in session.memo[id(tree)][1].keys()
            

#     class Test_RESULT:
#         def test_basic(self):
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 yield RESULT("ONE")
#                 return "TWO"
#             tree = make_tree()
#             session = Session([TransformerSet("basic", N_Transformer(transform))])

#             res = session.transform(tree, step = "RESULT")
#             assert res == "ONE"

#             res = session.transform(tree)
#             assert res == "TWO"


# class Test_Ordering:

#     class Test_Transform:
#         def test_rootfirst(self):
#             lst = []
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 lst.append(node.name)
#                 for n in node.children:
#                     session.transform(n)

#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#             assert lst == ["A","B","B2","C","D","D1"]

#         def test_depthfirst(self):
#             lst = []
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 for n in node.children:
#                     session.transform(n)
#                 lst.append(node.name)
                
#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#             assert lst == ["B2", "B", "C", "D1", "D", "A"]

#     class Test_TRANFORM_CHILDREN:
#         def test_depthfirst(self):
#             lst = []
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 yield TRANFORM_CHILDREN(node.children)
#                 lst.append(node.name)

#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#             assert lst == ["B2", "B", "C", "D1", "D", "A"]

#         def test_rootfirst(self):
#             lst = []
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 lst.append(node.name)
#                 yield TRANFORM_CHILDREN(node.children)

#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#             assert lst == ["A","B","B2","C","D","D1"]

#     class Test_TRANFORM_CHILDREN_GENERATOR:
#         def test_rootfirst(self):
#             lst = []
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 children = yield TRANFORM_CHILDREN_GENERATOR(node.children)
#                 assert isgenerator(children)
#                 lst.append(node.name)
#                 tuple(children)

#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#             assert lst == ["A","B","B2","C","D","D1"]

#         def test_leaffirst(self):
#             lst = []
#             def transform(session, node:N)->Generator[Flag, Any, None]:
#                 children = yield TRANFORM_CHILDREN_GENERATOR(node.children)
#                 assert isgenerator(children)
#                 tuple(children)
#                 lst.append(node.name)

#             session = Session([TransformerSet("basic", N_Transformer(transform))])
#             session.transform(make_tree())

#             assert lst == ["A","B","B2","C","D","D1"]








#     def test_step_nested(self):
#         pass

#     # def test_deepcopy_simple(self):
#     #     class Transformer(TransformerModule):
#     #         def match(self, obj)->bool:
#     #             return True
#     #         def transform(self, session, node:_NodeA)->Generator[Flag,Any,Generator]:
#     #             new_children = []
#     #             for c in node.children:
#     #                 new_children.append(session.transform(c))
#     #             result = _NodeA(node.name+"_V2", new_children)
#     #             return result
            
#     #     session = Session([TransformerSet("basic", Transformer())])

#     #     tree = _NodeA("A", [
#     #         _NodeA("B", []),
#     #         _NodeA("C", []),
#     #         _NodeA("D", [
#     #             _NodeA("E", []),
#     #         ]),
#     #     ])

#     #     result = session.transform(tree)

#     #     assert result.name =="A_V2"
#     #     assert len(result.children) == 3

#     #     assert len(result.children[2]) == 1
#     #     assert result.children[2].name == "D_V2"

#     #     assert len(result.children[2].children) == 1
#     #     assert result.children[2][0].name == "E_V2"
        
#     # def test_deepcopy_subgenerator(self):
#     #     lst = []
#     #     class Transformer(TransformerModule):
#     #         def match(self, obj)->bool:
#     #             return True
#     #         def transform(self, session, node:_NodeA)->Generator[Flag,Any,Generator]:
#     #             children = yield TRANFORM_CHILDREN(node.children)
#     #             lst.append(node.name)
#     #             return _NodeA(node.name+"_V2", children)

#     #     session = Session([TransformerSet("basic", Transformer())])

#     #     tree = _NodeA("A", [
#     #         _NodeA("B", []),
#     #         _NodeA("C", []),
#     #         _NodeA("D", [
#     #             _NodeA("E", []),
#     #         ]),
#     #     ])

#     #     result = session.transform(tree)

#     #     ## Leaf first in order
#     #     assert lst == ["B", "C", "E", "D", "A"]

#     # def test_deepcopy_childgenerator(self):
#     #     lst = []
#     #     class Transformer(TransformerModule):
#     #         def match(self, obj)->bool:
#     #             return True
#     #         def transform(self, session, node:_NodeA)->Generator[Flag,Any,Generator]:
#     #             children = yield TRANFORM_CHILDREN_GENERATOR(node.children)
#     #             lst.append(node.name)
#     #             return _NodeA(node.name+"_V2", children)

#     #     session = Session([TransformerSet("basic", Transformer())])

#     #     tree = _NodeA("A", [
#     #         _NodeA("B", []),
#     #         _NodeA("C", []),
#     #         _NodeA("D", [
#     #             _NodeA("E", []),
#     #         ]),
#     #     ])

#     #     result = session.transform(tree)

#     #     ## Root first, as children convert on read (is generator)
#     #     assert lst == ["A", "B", "C", "D", "E"]

#     # def test_deepcopy_step(self):
#     #     lst = []
#     #     class Transformer(TransformerModule):
#     #         def match(self, obj)->bool:
#     #             return True
#     #         def transform(self, session, node:_NodeA)->Generator[Flag,Any,Generator]:
#     #             children = yield TRANFORM_CHILDREN(node.children, step = "Initial")
#     #             lst.append(node.name)
#     #             children = yield TRANFORM_CHILDREN(node.children)
#     #             return _NodeA(node.name+"_V2", children)

#     #     session = Session([TransformerSet("basic", Transformer())])

#     #     tree = _NodeA("A", [
#     #         _NodeA("B", []),
#     #         _NodeA("C", []),
#     #         _NodeA("D", [
#     #             _NodeA("E", []),
#     #         ]),
#     #     ])

#     #     result = session.transform(tree)

#     #     ## Root first, as children convert on read (is generator)
#     #     assert lst == ["A", "B", "C", "D", "E"]

        

# # def transform_0(session, node:A):
# #     result = A("1")
# #     children = yield TRANSFORM_CHILDREN(node.children, step="RESULT")
# #     cache_id = {}
# #     for c in children:
# #         cache_id[c.id] = c
# #     session.cache_id = cache_id
# #     children = yield TRANSFORM_CHILDREN(node.children, step="FINISH")
# #     result.children.extend(children)
# #     return result
    

# # def transform_1(session, node:Any):
# #     result = Node(node.id)
# #     yield STEP("RESULT", result)

# #     ...

# #     return result