from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions, cvar_as
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
from ...core.structure import (
    Properties,
    Project,
    ExtResource,
    File,
    Resource,
    NodePath,
    GdSignal,
    Node,
    Settings,
    Category,
)


from contextvars import ContextVar
from typing import Generator, Any
from lark import (
    Token as LarkToken, 
    Tree as LarkTree,
    )

    

class MACROS:
    def default(item, /, default:Any=None, callable = lambda x:x):
        if item is None:
            return default
        return callable(item)

    def default_yield(item, /, default:Any=None, flag:Flag=TRANSFORM_CHILDREN, settings={}):
        if item is None:
            return default
        res = yield flag(item, **settings)
        return res

    def gdtopy_pairs_to_dict(item:list[LarkTree])->Generator[Flag,tuple,dict]:
        res = {}
        for pair in item:
            k,v = yield TRANSFORM_CHILDREN(pair.children)
            res[k] = v
        return res

    def pytogd_dict_to_str(item:dict, seperator="=", join=",")->Generator:
        res = []
        for pair in item.items():
            k,v = yield TRANSFORM_CHILDREN(pair) 
            res.append(k + seperator + v)
        return join.join(res)

class GdToPy_Options(TransformerOptions): ... ## Instanciated at session creation.
class PyToGd_Options(TransformerOptions): ...

# class _Properties():
#     class GdToPy(GdToPy_Transformer):
#         keys = ["properties"]
#         def transform(self, session, node:LarkTree):
#             result = yield from MACROS.gdtopy_pairs_to_dict(node.children)
#             return Properties(result)

#     class PyToGd(PyToGd_Transformer):
#         types = [Properties]
#         def transform(self, session, node:Properties):
#             result = yield from MACROS.pytogd_dict_to_str(node, join="\n")
#             return result

# class _Project():
#     class GdToPy(GdToPy_Transformer):
#         keys = ["project"]            
#     class PyToGd(PyToGd_Transformer):
#         types = [Project]

class _ExtResource():
    class GdToPy(GdToPy_Transformer):
        keys = ["ext_resource"]
        def transform(self, session, node):
            _options = node.children[0]
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options)
            return ExtResource(**options)

    class PyToGd(PyToGd_Transformer):
        types = [ExtResource]

class _Resource():
    class GdToPy(GdToPy_Transformer):
        keys = ["sub_resource"]
        def transform(self, session, node):
            _options, _properties = node.children
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties)
            return Resource(**options, properties = properties)

    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_resource"]
        def transform(self, session, node):
            _options, _ext_resources, _sub_resources, _properties = node.children

            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options)
            ext_resources : tuple[ExtResource] = yield TRANSFORM_CHILDREN(_ext_resources)
            sub_resources : tuple[Resource] = yield TRANSFORM_CHILDREN(_sub_resources)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties)

            return Resource(**options, ext_resources=ext_resources, sub_resources=sub_resources, properties = properties)
        
    class PyToGd(PyToGd_Transformer):
        types = [Resource]

class _GdSignal():
    class GdToPy(GdToPy_Transformer):
        keys = ["connection"]
        def transform(self, session, node):
            _options = node.children[0]
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options)
            return GdSignal(**options)

    class PyToGd(PyToGd_Transformer):
        types = [GdSignal]

class _Node():
    class GdToPy(GdToPy_Transformer):
        keys = ["node_resource"]
        def transform(self, session, node):
            _options, _properties = node.children
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties)
            return Node(**options, properties = properties)

    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_scene"]

        def transform(self, session, node):
            _options, _ext_resources, _sub_resources, _node_resources, _edit_flags, _connections = node.children
            # _options, _ext_resources, _sub_resources, _properties = node.children
            assert len(_node_resources.children) > 0
            result : Node = yield TRANSFORM_CHILDREN(_node_resources.children[0])

            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options)
            for k,v in options.items():
                setattr(result, k, v)

            ext_resources : tuple[ExtResource] = yield TRANSFORM_CHILDREN(_ext_resources.children)
            sub_resources : tuple[Resource] = yield TRANSFORM_CHILDREN(_sub_resources.children)
            node_resources : tuple[Node] = yield TRANSFORM_CHILDREN(_node_resources.children)
            # edit_flags : tuple[EditFlag] = yield TRANSFORM_CHILDREN(_edit_flags)

            #TODO: Incorperate edit flags.
            ## Cache that dumps on setup of instances?

            result.ext_resources.extend(ext_resources)
            result.sub_resources.extend(sub_resources)
            result.nodes.extend(node_resources)
            # result.edit_flags.extend(edit_flags)            

            return result
        
    class PyToGd(PyToGd_Transformer):
        types = [Node]

class _Settings():
    class GdToPy(GdToPy_Transformer):
        keys = ["file_settings"]
        def transform(self, session, node):
            _properties, _categories = node.children
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties)
            categories : tuple[Category] = yield from TRANSFORM_CHILDREN(_categories)
            return Settings(properties=properties, categories=categories)

    class PyToGd(PyToGd_Transformer):
        types = [Settings]

class _Category():
    class GdToPy(GdToPy_Transformer):
        keys = ["category"]
        def transform(self, session, node):
            _name, _properties = node.children
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties)
            return Category(str(_name), properties=properties)

    class PyToGd(PyToGd_Transformer):
        types = [Category]
        

gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    # _Properties.GdToPy,
    # _Project.GdToPy,
    _ExtResource.GdToPy,
    _Resource.GdToPy,
    _Resource.GdToPy_File,
    # _NodePath.GdToPy,
    _GdSignal.GdToPy,
    _Node.GdToPy,
    _Node.GdToPy_File,
    _Settings.GdToPy,
    _Category.GdToPy,
], 
options = {"structure":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::structure.py", [
    # _Properties.PyToGd,
    # _Project.PyToGd,
    _ExtResource.PyToGd,
    _Resource.PyToGd,
    # _NodePath.PyToGd,
    _GdSignal.PyToGd,
    _Node.PyToGd,
    _Settings.PyToGd,
    _Category.PyToGd,
], 
options = {"structure":PyToGd_Options} 
)