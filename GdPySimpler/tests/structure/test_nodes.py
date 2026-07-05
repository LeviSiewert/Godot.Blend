from ...core.structure import SignalNotation, EditFlag, ExtReference
from ...core.nodes import (
    ResourceScene,
    Node,
)


        
class Test_Node():
    def get_nodes(self):
        names = ("NodeA","NodeB","NodeC","NodeD","NodeE")

        ## Tree structure should be in all cases:
        ## A
        ## |-B
        ## |-C : Instance "SceneB"
        ## | |- ... : InsertedScene
        ## |-D : w/ defered owner
        ##   |-E
        ##     |-F : w/ defered owner

        ## Defered Parent:
        node_a = Node.construct("NodeA")
        node_b = Node.construct("NodeB",
            _defered_parent = "",
        )
        node_c = Node.construct("NodeC",
            instance = "SceneB",
            _defered_parent = "",
        )
        node_d = Node.construct("NodeD",
            _defered_apply_owner = True,
            _defered_parent = "",
        )
        node_e = Node.construct("NodeE",
            _defered_parent = "NodeD",
        )
        node_f = Node.construct("NodeF",
            _defered_apply_owner = True,
            _defered_parent = "NodeD/NodeE",
        )


        yield (node_a, node_b, node_c, node_d, node_e, node_f)
        # yield reversed((node_a, node_b, node_c, node_d, node_e, node_f))


        ## Applied parent:
        node_a = Node.construct("NodeA")
        node_b = Node.construct("NodeB",
            parent = node_a,
        )
        node_c = Node.construct("NodeC",
            instance = "SceneB",
            parent = node_a,
        )
        node_d = Node.construct("NodeD",
            parent = node_a,
            _defered_apply_owner = True,
        )
        node_e = Node.construct("NodeE",
            parent = node_d,
        )
        node_f = Node.construct("NodeF",
            parent = node_e,
            _defered_apply_owner = True,
        )
        yield (node_a, node_b, node_c, node_d, node_e, node_f)
        # yield reversed((node_a, node_b, node_c, node_d, node_e, node_f))


        ## Applied children:
        node_f = Node.construct("NodeF",
            _defered_apply_owner = True,
            )
        node_e = Node.construct("NodeE",
            children = (node_f,),
        )
        node_d = Node.construct("NodeD",
            children = (node_e,),
            _defered_apply_owner = True,
        )
        node_c = Node.construct("NodeC",
            instance = "SceneB",
        )
        node_b = Node.construct("NodeB")
        node_a = Node.construct("NodeA",
            children = (node_b, node_c, node_d, node_e)
        )

        yield (node_a, node_b, node_c, node_d, node_e, node_f)
        # yield reversed((node_a, node_b, node_c, node_d, node_e, node_f))
        

        ## Mixed test:
        node_a = Node.construct("NodeA",
        )
        node_b = Node.construct("NodeB",
            _defered_parent = ""
        )
        node_c = Node.construct("NodeC",
            instance = "SceneB",
            parent = node_a
        )
        node_d = Node.construct("NodeD",
            _defered_apply_owner = True,
            _defered_parent = "",
            parent = node_a
        )
        node_e = Node.construct("NodeE", 
            _defered_parent = "NodeD"
        )
        node_f = Node.construct("NodeF", 
            _defered_apply_owner = True,
            parent = node_e,
        )
        yield (node_a, node_b, node_c, node_d, node_e, node_f)
        # yield reversed((node_a, node_b, node_c, node_d, node_e, node_f))

        
    def test_basic_construction(self,):
        node = Node.construct()
        assert (node.name == "Node")

        node = Node.construct(
            properties={
                "a":"a",
                "b":"b",
                "c":"c",
            },
        )
        assert (node.properties["a"] == "a")

    def test_construction_owner(self):
        i = 0
        for tree in self.get_nodes():
            node_a, node_b, node_c, node_d, node_e, node_f = tree

            scene = ResourceScene.construct(f"TestIndex:{i}",
                nodes=tree,
                set_nodes_owner=False,
            )

            # raise Exception(node_d.context._extends._extends.resource)

            assert node_d.context._extends._extends.resource is scene
            assert node_d.context._extends._extends is scene.context
            assert node_d.context._extends.resource is scene
            
            assert node_d.context._extends is scene.nodes.context
            assert node_d.context.resource == scene

            assert node_b.owner is None 
            assert node_c.owner is None 
            assert node_d.owner is scene 
            assert node_e.owner is None
            assert node_f.owner is scene

            i = i+1

    def test_construction_tree(self):
        for tree in self.get_nodes():
            node_a, node_b, node_c, node_d, node_e, node_f = tree

            scene = ResourceScene.construct(
                nodes=tree
            )

            assert node_b._parent is node_a
            assert node_c._parent is node_a
            assert node_d._parent is node_a
            assert node_e._parent is node_d
            assert node_f._parent is node_e
    
    def test_construction_instance(self):
        for tree in self.get_nodes():
            node_a, node_b, node_c, node_d, node_e, node_f = tree
            ext_ref = ExtReference("scene", "SceneB", "SceneB", "SceneB") 

            scene_a = ResourceScene.construct("SceneA",
                nodes=tree,
                ext_references=[ext_ref],
                # edit_resources=[
                #     EditFlag("NodeC")
                # ],
                # _construct_tree = False,
                # _load_references = False,
            )

            assert (scene_a.ext_references["SceneB"] is ext_ref)

            scene_b = ResourceScene.construct("SceneB",
                nodes=(
                    Node.construct("Root", 
                        properties = {
                            "a":"A",
                            "z":"Z",
                        }
                    ),
                )
            )
            
            assert node_c.instance.context.resource is scene_a

            assert node_c.instance.cached_value() is ext_ref
            assert node_c.instance_editable is False
            assert node_c.overlay is None

            scene_a.setup_tree(load_instances=False)
            
            # scene.setup_tree(load_instances=True)
            ## This should error out!!