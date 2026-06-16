from .primitives import Context
from .transformer_v2 import Transformer, TransformerModule, TransformerRuleset, TERMINAL, IGNORE, DEFAULT, TransformerContext
from lark.visitors import Tree, Token #type:ignore
from typing import Any, Iterable, Type, Callable
from .property_collection import PropertyCollection

''' Custom transformer for lark types of (Tree|Token) for uniformity of first and second pass transformer implementations, along with parsing flexibility '''

class LarkTransformerRuleset(TransformerRuleset):
    def _key_extractor(self, key:Tree|Token|None):
        if isinstance(key, Tree):
            return (str(key.data),)
            # return key.data
        
        if isinstance(key, Token):
            return (str(key.type),)
        
        return super()._key_extractor(key)
    
class LarkTransformerModule(TransformerModule):
    ''' Attempting eq behavior to Lark.visitors.Transformer.transform() to a new tree by calling _transform() with expanded children and depth-first '''

    def get_keys(self):
        return tuple()
    
    def _get_children_default(self, node:Tree|Token|None):
        if isinstance(node, Tree):
            return node.children
        
        if isinstance(node, Token):
            return TERMINAL

        if node is None:
            return None
        
        raise KeyError("Could not determine children of unknown object:", node)
    
    def transform(self, node:Tree|Token, tc:TransformerContext, gdc:Context, *args, **kwargs):
        ''' Called on each token, children already exist, are ordered and are nullable '''
        key = tc.key.get()
        children = tc.children.get()
        if children is None:
            children = tuple()
        return self._transform(key, tc, gdc, *children)
    
    def _transform(self, key:str, tc:TransformerContext, gdc:Context, *children)->Any:
        return IGNORE

class LarkTransformerModuleCentralized(LarkTransformerModule):
    ''' A central transformer module for extracting lark_keys and parse_lark.
    Planned to be depreciated in the future in favor of GdType subclasses OR seperate files. 
    '''
    transformers : dict[str, Callable]
    _get_parse_keys = "lark_keys"
    _get_parse_func = "parse_lark"

    def get_keys(self,):
        return self.transformers.keys()

    def __init__(self, objects:Iterable[Type]):
        self.transformers = {}
        for obj in objects:
            for k in getattr(obj, self._get_parse_keys)():
                v = getattr(obj, self._get_parse_func)
                self.transformers[k] = v 
        super().__init__()

    # def _transform(self, key:str, c:Context, *args, **kwargs)->Any:
    def _transform(self, key:str, tc:TransformerContext, gdc:Context, *children)->Any:
        if isinstance(tc.node.get(), Tree):
            return self.transformers[key](key, tc, gdc, *children)
        else:
            return self.transformers[key](key, tc, gdc, tc.node.get())


class LarkTransformerModuleTerminals(LarkTransformerModule):
    def get_keys(self):
        return ( "value", "property", "properties", "resource_header", "resource_body", "packed_2", "packed_2i", "packed_3", "packed_3i", "packed_4", "packed_4i", "packed_6", "packed_9", "packed_12", "BOOL", "NULL", "INF", "INF_NEG", "STRING", "NUMBER", "FLOAT", "WORD", DEFAULT, None )

    # def _transform(self, key:str|DEFAULT, c:Context, *args, **kwargs)->Any:
    def _transform(self, key:str, tc:TransformerContext, gdc:Context, *children)->Any:
        if key is None:
            return None
        if key is DEFAULT:
            return self.__default__(key, tc, gdc, *children)
        if isinstance(tc.node.get(), Tree):
            return getattr(self,key)(key, tc, gdc, *children)
        if isinstance(tc.node.get(), Token):
            return getattr(self,key)(key, tc, gdc, tc.node.get())
        raise Exception("Should not get here")
        
    def __default__(self, key, c, gdc, *children):
        raise Exception("DEFAULT", key, c.node.get())

    def value(self, key, c, gdc, child):
        return child
        # raise Exception(node, c, child)

    def property(self, key, c, gdc, pkey, pvalue):
        # raise Exception(c, k,v)
        if (key is None):
            return IGNORE
        return (pkey, pvalue)

    def properties(self, key, c, gdc, *props):
        res = PropertyCollection()
        for kv in props:
            if kv is None: 
                continue
            res[kv[0]] = kv[1]
        return res

    def resource_header(self, key:str, tc:TransformerContext, gdc:Context, properties):
        return properties
    def resource_body(self, key:str, tc:TransformerContext, gdc:Context, properties):
        return properties

    def packed_2(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_2i(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_3(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_3i(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_4(self, key:str, tc:TransformerContext, gdc:Context, *children):
        return children
    def packed_4i(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_6(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_9(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children
    def packed_12(self, key:str, tc:TransformerContext, gdc:Context, *children): 
        return children

    def BOOL(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        if tc.node.get() == "true": 
            return True
        return False
    
    def NULL(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return None
    
    def INF(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return float("inf")
    
    def INF_NEG(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return -float("inf")
    
    def STRING(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return str(tc.node.get()).strip('"')
    
    def NUMBER(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return int(tc.node.get())

    def FLOAT(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return float(tc.node.get())

    def WORD(self, key:str, tc:TransformerContext, gdc:Context, token:Token):
        return str(tc.node.get())
