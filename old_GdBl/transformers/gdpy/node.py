from contextvars import ContextVar

from bpy.types import (
    Object as BlNode,
    Material as BlMaterial,
    Mesh as BlMesh,
    Collection as BlScene,
)

from ...core.structure import (
    GdNode as BlNodeData,
    GdScene as BlSceneData,

)

from ._transformer import (
    GdToBl_Transformer, 
    GdToBl_TransformerSet, 
    GdToBl_TransformerOptions, 
    BlToGd_Transformer, 
    BlToGd_TransformerSet, 
    BlToGd_TransformerOptions, 
    TRANSFORM_CHILDREN,
    TRANSFORM,
)

from ....GdPy.core.structure import (
    Properties as PyProperties,
    Promise as PyPromise,
    Node as PyNode,
    Resource as PyResource,
    File as PyFile,
)


## OPTIONS ##

class GdToBl_Options(GdToBl_TransformerOptions):
    def __init__(self, session):
        pass

class BlToGd_Options(BlToGd_TransformerOptions):
    def __init__(self, session):
        pass


class GdToBl_Scene(GdToBl_Transformer):
    _types = [BlScene]

    def node_tree_iterator(self, root_node:BlNode):
        ''' traverse and transform all trees '''
        raise NotImplementedError()

    def transform(self, session, node):
        blscene = session.options["structure"].blscene
        gdscene = session.options["structure"].gdscene

        
        gd : BlSceneData = node.gd

        t = blscene.set(node)
        root_node = yield TRANSFORM(gd.root_node, step="Initial")
        t0 = gdscene.set(root_node)

        ext_resources = yield TRANSFORM_CHILDREN(gd.ext_resources)
        sub_resources = yield TRANSFORM_CHILDREN(gd.sub_resources)
        root_node.uid = gd.uid
        root_node.file = gd.file
        root_node.ext_resources.extend

        yield TRANSFORM(gd.root_node)

        gdscene.reset(t0)
        blscene.reset(t)

        return root_node


class GdToBl_Node(GdToBl_Transformer):
    memoized = True
    _types = [BlNode]
    def transform(self, session, node:BlNode):
        gd : BlNodeData = node.gd

        res = PyNode(
            name=gd.name,
            type=gd.type,
            unique_id=gd.unique_id,
            )

        yield STEP("Intial", res)

        # script_type=gd.script_type ##TODO

        properties = yield TRANSFORM(node.properties)
        res.properties.update(properties)
        yield STEP("Properties", res)

        # if node.type is bpy.types.empty:
            # properties = yield TRANSFORM(Macros.dif_instance(node.properties))
            # res.properties.update(properties)
            # yield STEP("Properties", res)
            
            # res.instance=  ##TODO
            # session.dependencies.declare(instance)
            # res.instance_editable=  ##TODO
        # yield STEP("Instance", res)

        children = yield TRANSFORM_CHILDREN(node.children)
        res.children.extend(children)
        # node = session.options["structure"].node.get()

        return res

class BlToGd_Node(BlToGd_Transformer):
    memoized = True
    _types = [PyNode]
    def transform(self, session, node:PyNode):
        pass



class GdToBl_Mesh(GdToBl_Transformer):
    ''' Transform mesh from Resource Subtype [ArrayMesh] into the blender equivilent '''
    memoized = True

    def match(self, session, node):
        if (not isinstance(node,PyResource)) or (isinstance(node,PyNode)) :
            return
        return "ArrayMesh" in node.gdtype
    
    def transform(self, session, node):
        raise NotImplementedError()

class BlToGd_Mesh(BlToGd_Transformer):
    _types = [BlMaterial]
    memoized = True

    def transform(self, session, node):
        raise NotImplementedError()




## GROUPINGS ##

PROPCOL_gd_to_bl = GdToBl_TransformerSet("Properties", [
],
options={
    "properties":GdToBl_Options,
})

PROPCOL_bl_to_gd = BlToGd_TransformerSet("Properties", [
],
options={
    "properties":BlToGd_Options,
})
