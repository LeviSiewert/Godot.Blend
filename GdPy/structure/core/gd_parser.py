from typing import Type, Callable
from lark.visitors import Transformer, v_args #type:ignore
from lark import Lark,Token #type:ignore
from .core import GdType, Context, PropertyCollection
from .primitives import CacheTreeNode
from contextvars import ContextVar
from typing import Any


class _BaseTransformer(Transformer):
    """ Utility for thin "wrapper" or "router" style tokens that are not instanced, IE Value """
    
    def value(self, children):
        return children[0]
    
    def parser(self, k,v):
        return (k,v)

    def property(self, kv):
        return kv

    def properties(self, props):
        res = PropertyCollection()
        for kv in props:
            res[kv[0]] = kv[1]
        return res

    def prim_resource(self, props):
        return props

    def resource_header(self, properties):
        return properties
    def resource_body(self, properties):
        return properties
    
    def packed_2(self, children): 
        return children
    def packed_2i(self, children): 
        return children
    def packed_3(self, children): 
        return children
    def packed_3i(self, children): 
        return children
    def packed_4(self, children): 
        return children
    def packed_4i(self, children): 
        return children
    def packed_6(self, children): 
        return children
    def packed_9(self, children): 
        return children
    def packed_12(self, children): 
        return children

    
    def NULL(self, *args):
        return None
    
    def INF(self,*args):
        return float("inf")
    def INF_NEG(self,*args):
        return -float("inf")
    
    def STRING(self, child:Token):
        return str(child).strip('"')
    
    def NUMBER(self, child:Token):
        return int(child)

    def FLOAT(self, child:Token):
        return float(child)

    def WORD(self, child:Token):
        return str(child)


class GdParser():
    types : list[Type]
    grammer : str
    _transformer : Transformer
    
    def __init__(self, grammer:str, types:list[Type]):
        self.grammer = grammer
        self.types = types
        super().__init__()
        self.construct_transformer()

    def construct_transformer_function(self,key,func)->Callable:
        def res(*args, **kwargs):
            return func(key, *args, **kwargs)
        return res

    def construct_transformer(self):
        class transformer(_BaseTransformer):
            pass

        for x in self.types:
            if (not hasattr(x,"parse_lark")) or (not hasattr(x,"lark_keys")):
                raise Exception("All supplied types must have parse_lark", x)
            for k in x.lark_keys():
                setattr(transformer, k, self.construct_transformer_function(k, x.parse_lark))
        transformer = v_args(inline=True)(transformer)
        self._transformer = transformer()

    def parse(self, context:Context, data:str, cache_tree:CacheTreeNode=None, start:str=None)->GdType|Any:
        parser = Lark(self.grammer, maybe_placeholders=True, start=start)
        tree = parser.parse(data) 
        result = self._transformer.transform(tree)
        if isinstance(result, GdType) and cache_tree:
            with cache_tree.traverse(True):
                self.build_cache_tree(result)
        return result
    
    def build_cache_tree(self, result:GdType):
        ''' Iterate over objects here '''

        if getattr(result,"_cache_layers"):
            result.cache_tree_node = CacheTreeNode(result, result._cache_layers)
            with result.cache_tree_node.traverse():
                for x in result.get_struct_children():
                    if isinstance(x, GdType):
                        self.build_cache_tree(x)
        else:
            for x in result.get_struct_children():
                if isinstance(x, GdType):
                    self.build_cache_tree(x)
