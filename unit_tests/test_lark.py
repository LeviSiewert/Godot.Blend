from lark import Lark
from lark.visitors import Transformer, v_args
from pathlib import Path

from structure_values import *
from structure_resources import *

from typing import Any

cwd = Path.cwd()
grammer = (cwd / "tscn.lark").read_text()
file = (cwd / "test.tscn").read_text()

parser = Lark(grammer, parser="earley")
tree = parser.parse(file)

class _PropertyMedium():
    ## Temp data container.
    name : str
    value : GdTypeValue
    def __init__(self, name:str, value:GdTypeValue):
        self.name = name
        self.value = value

# class _ResourceHeaderMedium():
#     ## temp Resource header container
#     ## Definition of *type* of file
#     _type : str
#     comments : list[str]
#     properties : list[_PropertyMedium]

#     def __init__(self, header_properties: list[_PropertyMedium] _type:str, comments:list[str], properties:list[_PropertyMedium]):
#         self._type = _type
#         self.header_properties = 
#         self.comments = comments
#         self.properties = properties

@v_args(meta=True)
class lark_transformer(Transformer):
    # def __default__(self, obj:Any)->Any:
    #     return obj
    def file_project(self, meta, children:list)->GdTypeResourceFileProject:
        ## Project settings
        inst = GdTypeResourceFileProject.new()        
        return inst
        
    def file_resource_tres(self, meta, children:list)->GdTypeResourceFile:
        inst = GdTypeResourceFile.new()        
        return inst

    def file_resource_tscn(self, meta, children:list)->GdTypeResourceFile:
        inst = GdTypeResourceFile.new()        
        return inst
    
    def resource_header(self, meta, children:list)->_ResourceMedium:
        inst = _ResourceHeaderMedium.new()        
        return inst

    def sub_resource(self, meta, children:list)->GdTypeResourceFile:
        inst = _ResourceHeaderMedium.new()        
        return inst
    
    @v_args(inline=True)
    def property(self, meta, name, value:GdTypeValue)->_PropertyMedium:
        pass
    
    # def resource(self,meta,children)->Any:
    #     return 
    # def sub_resource


print(tree.pretty())