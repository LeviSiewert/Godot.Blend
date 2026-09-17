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

class GdToPy_Options(TransformerOptions): ... ## Instanciated at session creation.
class PyToGd_Options(TransformerOptions): ...

class _Properties():
    class GdToPy(GdToPy_Transformer):
        keys = ["properties"]
    class PyToGd(PyToGd_Transformer):
        types = [Properties]
class _Project():
    class GdToPy(GdToPy_Transformer):
        keys = ["project"]
    class PyToGd(PyToGd_Transformer):
        types = [Project]
class _ExtResource():
    class GdToPy(GdToPy_Transformer):
        keys = ["ext_resource"]
    class PyToGd(PyToGd_Transformer):
        types = [ExtResource]
class _Resource():
    class GdToPy(GdToPy_Transformer):
        keys = ["sub_resource"]
    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_resource"]
    class PyToGd(PyToGd_Transformer):
        types = [Resource]
class _NodePath():
    class GdToPy(GdToPy_Transformer):
        keys = ["node_path"]
    class PyToGd(PyToGd_Transformer):
        types = [NodePath]
class _GdSignal():
    class GdToPy(GdToPy_Transformer):
        keys = ["gd_signal"]
    class PyToGd(PyToGd_Transformer):
        types = [GdSignal]
class _Node():
    class GdToPy(GdToPy_Transformer):
        keys = ["node_resource"]
    class GdToPy_File(GdToPy_Transformer):
        keys = ["file_scene"]
    class PyToGd(PyToGd_Transformer):
        types = [Node]
class _Settings():
    class GdToPy(GdToPy_Transformer):
        keys = ["file_settings"]
    class PyToGd(PyToGd_Transformer):
        types = [Settings]
class _Category():
    class GdToPy(GdToPy_Transformer):
        keys = ["category"]
    class PyToGd(PyToGd_Transformer):
        types = [Category]

gd_to_py = GdToPy_TransformerSet("STD::structure.py", [  
    _Properties.GdToPy,
    _Project.GdToPy,
    _ExtResource.GdToPy,
    _Resource.GdToPy,
    _Resource.GdToPy_File,
    _NodePath.GdToPy,
    _GdSignal.GdToPy,
    _Node.GdToPy,
    _Node.GdToPy_File,
    _Settings.GdToPy,
    _Category.GdToPy,
], 
options = {"structure":GdToPy_Options}
)

py_to_gd = PyToGd_TransformerSet("STD::structure.py", [
    _Properties.PyToGd,
    _Project.PyToGd,
    _ExtResource.PyToGd,
    _Resource.PyToGd,
    _NodePath.PyToGd,
    _GdSignal.PyToGd,
    _Node.PyToGd,
    _Settings.PyToGd,
    _Category.PyToGd,
], 
options = {"structure":PyToGd_Options} 
)