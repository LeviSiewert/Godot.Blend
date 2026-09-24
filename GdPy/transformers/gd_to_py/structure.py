from ...core.transformer import Flag, STEP, TRANSFORM, TRANSFORM_CHILDREN, Session, TransformerOptions, cvar_as
from ._transformer import GdToPy_TransformerSet, PyToGd_TransformerSet, PyToGd_Transformer, GdToPy_Transformer, PyToGd_Session, GdToPy_Session
from ...core.structure import (
    Properties,
    Project,
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
#             result = yield from MACROS.gdtopy_pairs_to_dict(node.children.children)
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
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            return ExtResource(**options)

    class PyToGd(PyToGd_Transformer):
        types = [ExtResource]

class _Resource():
    class GdToPy(GdToPy_Transformer):
        keys = ["sub_resource"]
        def transform(self, session, node):
            _options, _properties = node.children
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)
            return Resource(**options, properties = properties)

    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_resource"]
        def transform(self, session, node):
            _options, _ext_resources, _sub_resources, _properties = node.children

            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            ext_resources : tuple[ExtResource] = yield TRANSFORM_CHILDREN(_ext_resources)
            sub_resources : tuple[Resource] = yield TRANSFORM_CHILDREN(_sub_resources)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)

            return Resource(**options, ext_resources=ext_resources, sub_resources=sub_resources, properties = properties)
        
    class PyToGd(PyToGd_Transformer):
        types = [Resource]

class _GdSignal():
    class GdToPy(GdToPy_Transformer):
        keys = ["connection"]
        def transform(self, session, node):
            _options = node.children[0]
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            options["fr"] = options["from"]
            del options["from"]
            return GdSignal(**options)

    class PyToGd(PyToGd_Transformer):
        types = [GdSignal]

class _Node():
    class GdToPy(GdToPy_Transformer):
        keys = ["node_resource"]
        def transform(self, session, node):
            _options, _properties = node.children
            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)

            options["id"] = options.pop["unique_id"]
            _parent = options.pop("parent")

            res = Node(**options, properties = properties)
            res._parent = _parent

    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_scene"]

        def transform(self, session, node):
            _options, _ext_resources, _sub_resources, _node_resources, _edit_flags, _connections = node.children
            # _options, _ext_resources, _sub_resources, _properties = node.children
            assert len(_node_resources.children) > 0
            result : Node = yield TRANSFORM(_node_resources.children[0])


            options : dict = yield from MACROS.gdtopy_pairs_to_dict(_options.children)
            result.__setup_file__(uid=options["uid"])
            result.format= options["format"]

            ext_resources : tuple[ExtResource] = yield TRANSFORM_CHILDREN(_ext_resources.children)
            sub_resources : tuple[Resource] = yield TRANSFORM_CHILDREN(_sub_resources.children)

            edit_flags = [] 
            for n in _edit_flags.children:
                edit_flags.append(NodePath(n.children[0][0]))

            ## Prepare tree dependencies:
            result.ext_resources.extend(ext_resources)
            result.sub_resources.extend(sub_resources)

            node_namespace = {".": result}
            nodes_unclaimed = {}
            node_resources : tuple[Node] = yield TRANSFORM_CHILDREN(_node_resources.children[1:], as_generator=True)

            for n in node_resources:
                ## Construct node structure from paths, remove temp variable from node.
                p_path = n._parent
                del n._parent
                fullpath : str|None = None

                if p_path == ".":
                    result.children.append(n)
                    fullpath = n.name.key
                    node_namespace[fullpath] = n
                else:
                    fullpath = (p_path + "/" + n.name.key)
                    if p_path in node_namespace.keys():
                        node_namespace[p_path].children.append(n)
                        node_namespace[fullpath] = n
                    else:
                        ## Instance-Overlay edited 
                        nodes_unclaimed[fullpath] = n

                if fullpath in edit_flags:
                    edit_flags.remove(fullpath)
                    n.instance_editable = True

            result.nodes_unclaimed = nodes_unclaimed
            result.edits_unclaimed = edit_flags

            return result
        
    class PyToGd(PyToGd_Transformer):
        types = [Node]

class _Settings():
    class GdToPy(GdToPy_Transformer):
        keys = ["file_settings"]
        def transform(self, session, node):
            _properties, _categories = node.children
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)
            categories : tuple[Category] = yield from TRANSFORM_CHILDREN(_categories)
            return Settings(properties=properties, categories=categories)

    class PyToGd(PyToGd_Transformer):
        types = [Settings]

class _Category():
    class GdToPy(GdToPy_Transformer):
        keys = ["category"]
        def transform(self, session, node):
            _name, _properties = node.children
            properties : dict = yield from MACROS.gdtopy_pairs_to_dict(_properties.children)
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