from __future__ import annotations

from ....GdPy.structure.core import GdType
from ....GdPy.structure.core.primitives import MultiKeyCollection

from ..core.primitives import BlContext
from ..core.structure import _all as bl_core_all

from abc import ABC, abstractmethod
from typing import Any, Type, Callable, Iterable

from inspect import is_generator_function


class Transformer[A,B, KEY:str|Any, TRFM:TransformerModule[A,B]]():
    
    data : dict[str|A|B, list[TRFM]]
    _cache : dict[TRFM, dict[str|Type]]

    def __init__(self, modules:tuple[TRFM]=None): #, additional:tuple[TRFM]=None):
        self.data = {}

    def fr_blender(self, c:BlContext, bl_item:A):
        return self._tree_iterator(c, bl_item, "fr_blender", lambda x: x.get_struct_children())
    def to_blender(self, c:BlContext, gd_item:B):
        return self._tree_iterator(c, gd_item, "to_blender", lambda x: x.get_struct_children())
    
    def _tree_iterator(self, c:BlContext, node:A|B, function_id:str, get_children:Callable[...,Iterable|None])->B|A|None:
        key, transformer = self.matcher(node)
        
        func = getattr(transformer, function_id)

        if func.is_generator_function(func):
            _children = {}
            gen = func(c, key, node, _children)
            children = next(gen)
            if children is None:
                children = get_children(node)
            for child in children:
                _children[child] = self._tree_iterator(child,c, node, function_id, get_children)
            return next(gen)
        else:
            _children = {}
            children = get_children(node)
            for child in children:
                _children[child] = self._tree_iterator(child,c, node, function_id, get_children)
            return func(c, key, node, _children)

    def matcher(self, item:A|B)->tuple[KEY,TRFM]:
        if isinstance(item, GdType):
            pass
        elif isinstance(item, bl_core_all):
            pass
        else:
            raise KeyError("")

class TransformerModule(ABC):
    module_info : dict

    @classmethod
    @abstractmethod
    def get_gdbl_keys(cls)->tuple[str|GdType|Any]:
        return tuple()

    # def register(self,):
    #     ''' Use to register & unregister Property Groups onto import/export settings & addon preferences '''
    
    # def unregister(self,):
    #     ''' Use to register & unregister Property Groups onto import/export settings & addon preferences '''

    # def draw_import(self, layout, context):
    #     ''' Use to draw on import window '''
    #     pass

    # def draw_export(self, layout, context):
    #     ''' Use to draw on export window '''
    #     pass

    # def draw_preferences(self, layout, context):
    #     ''' Use to draw on preferences window '''
    #     pass
        
    @abstractmethod
    def fr_blender(self, k:Any, c:BlContext, bl_item, _children:dict):
        ''' Transformer method, supports pre and post node traversal (depth-first) via yield w/a 
        return: return instance of target object (in bl, assumed to already be in data struct) 
        yield:
            - use of Yield provides children to parse next, otherwise defaults to parsing (get_struct_children) results  
            - _children (dict argument) populated after yield
            - _children is dict[pre:post]
            - context is shared down/up the entire tree
        primary reasons for this 2 step system:
            - Ability to populate prereq info for children
                - IE Settup of project settings, changing of Collection location, scene or even file
            - Ability to allow children to manage value location/allocation
                - IE distributed TRES w/ unknown addresses, gathered
            - Ability to cull/bypass a linear equivlent tree
                - IE it's possible to have (4 BlNode) == (1 GdNode)
            - Ubiquity between transformers (Bl->Gd) & (Gd->Bl)
                - BL is *primarly* root first
                - GD is *primarly* depth first
        '''
        ## Pre-Child Transform
        yield ## Transform children
        ## _children is now populated
        ## Post-Depth transform
        return ## New object, added to parent's children

    @abstractmethod
    def to_blender(self, k:Any, c:BlContext, gd_item, _children:dict):
        ''' Transformer method, supports pre and post node traversal (depth-first) via yield w/a 
        return: return instance of target object (in bl, assumed to already be in data struct) 
        yield:
            - use of Yield provides children to parse next, otherwise defaults to parsing (get_struct_children) results  
            - _children (dict argument) populated after yield
            - _children is dict[pre:post]
            - context is shared down/up the entire tree
        primary reasons for this 2 step system:
            - Ability to populate prereq info for children
                - IE Settup of project settings, changing of Collection location, scene or even file
            - Ability to allow children to manage value location/allocation
                - IE distributed TRES w/ unknown addresses, gathered
            - Ability to cull/bypass a linear equivlent tree
                - IE it's possible to have (4 BlNode) == (1 GdNode)
            - Ubiquity between transformers (Bl->Gd) & (Gd->Bl)
                - BL is *primarly* root first
                - GD is *primarly* depth first
        '''
        ## Pre-Child Transform
        yield ## Tranform Children
        ## _children is now populated
        ## Post-Depth Transform
        return ## New object, added to parent's children