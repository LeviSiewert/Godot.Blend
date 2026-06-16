from __future__ import annotations

from ....GdPy.structure.core import GdType
from ....GdPy.structure.core.primitives import MultiKeyCollection

from ..core.primitives import BlContext
from ..core import _all as bl_core_all

from abc import ABC, abstractmethod
<<<<<<< HEAD:GdBl/structure/transformer.py
from ...GdPy.structure.core import GdType
from contextvars import ContextVar
from typing import Any
from inspect import isgeneratorfunction
=======
from typing import Any, Type, Callable, Iterable
>>>>>>> bd96feba7fb3a0548806ac0b71e8b553defb5134:GdBl/structure/transformers/core.py

from inspect import isgeneratorfunction


class Transformer[A,B, KEY:str|Any, TRFM:TransformerModule[A,B]]:
    data : dict[str|A|B, list[TRFM]]

    def __init__(self, modules:tuple[TRFM]=None): #, additional:tuple[TRFM]=None):
        self.data = {}
        for m in modules:
            m = m()
            for k in m.get_gdbl_keys():
                assert(not (k in self.data.keys()))
                self.data[k] = m

    def fr_blender(self, c:BlContext, bl_item:A):
        if c.meta_tree.get() is None:
            t = c.meta_tree.set(tuple())
            reset = True
        res = self._tree_iterator(c, bl_item, "fr_blender", lambda x: x.get_struct_children())
        if reset:
            c.meta_tree.reset(t)
        return res
    
    def to_blender(self, c:BlContext, gd_item:B):
        if c.meta_tree.get() is None:
            t = c.meta_tree.set(tuple())
            reset = True
        res = self._tree_iterator(c, gd_item, "to_blender", lambda x: x.get_struct_children())
        if reset:
            c.meta_tree.reset(t)
        return res
    
    def _tree_iterator(self, c:BlContext, node:A|B, function_id:str, get_children:Callable[...,Iterable|None])->B|A|None:
        key, transformer = self.matcher(node)

        func = getattr(transformer, function_id)
        meta_tree_token = c.meta_tree.set((*c.meta_tree.get(),node))
        if isgeneratorfunction(func):
            _children = {}
            gen = func(c, key, node, _children)
            
            children = next(gen)
            ## TODO: allow yielding of TERMINAL enum (or similar)

<<<<<<< HEAD:GdBl/structure/transformer.py
    def tree_traversal(self, node, funcname, default_getchild_func:str)->Any:
        _children = {}
        _transformer = self.matcher(node)
        if _transformer is None:
            return None
        transform = getattr(_transformer, funcname)
        
        if isgeneratorfunction(transform):
            ## Call once, transform children!
            tfm_children = transform(node)
            if tfm_children is None:
                tfm_children = getattr(node, default_getchild_func)
            for _node in tfm_children:
                _children[_node] = self.tree_traversal(_node, funcname, default_getchild_func)
            return transform()
            
        else:
            # tfm_children = getattr(node, default_getchild_func)
            # for _node in tfm_children:
            #     _children[_node] = self.tree_traversal(_node, funcname, default_getchild_func)
            # return transform(node)
            raise Exception("Tranform function must be Generator with one step!")        

    def matcher(self,key)->TransformerModule:
        ## TODO: for res/subres/nodes this needs to reference the cls_db 

        if isinstance(key,GdType):
            key = self._gd_key_extractor(key)
        else:
            key = self._bl_key_extractor(key)

    def _gd_key_extractor(key)->tuple[str]:
        ## Get key from 
        pass

    def _bl_key_extractor(key)->tuple[str]:
        pass
=======
            if (children is None) and (transformer._terminal):
                return next(gen)
            
            if (children is None):
                children = get_children(node) 
            
            for child in children:
                _children[child] = self._tree_iterator(c, child, function_id, get_children)
            
            res = next(gen)
            c.meta_tree.reset(meta_tree_token)
            return res
        else:
            _children = {}
            if not transformer._terminal:
                children = get_children(node)
                for child in children:
                    _children[child] = self._tree_iterator(c, child, function_id, get_children)
            res = func(c, key, node, _children)
            c.meta_tree.reset(meta_tree_token)
            return res

    def matcher(self, item:A|B|Any)->tuple[KEY,TRFM]:
        return (item.__class__, self.data[item.__class__])
>>>>>>> bd96feba7fb3a0548806ac0b71e8b553defb5134:GdBl/structure/transformers/core.py

class TransformerModule(ABC):
    _terminal = False 
    ## Flag to stop iteration and not call for children
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
    def fr_blender(self, c:BlContext, k:Any,  bl_item, _children:dict):
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
    def to_blender(self, c:BlContext, k:Any,  gd_item, _children:dict):
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
<<<<<<< HEAD:GdBl/structure/transformer.py
        return ## New object, added to parent's children
    
class TransformerModuleNodeResource(TransformerModule):
    @abstractmethod
    def to_blender(self, c:BlContext, gd_item, _children:dict, gltf_node=None, edit_subres=None):
        pass

    @abstractmethod
    def fr_blender(self, c:BlContext, bl_item, _children:dict):
        pass

# class _ExampleTransformer():    
#     @classmethod
#     def get_gd_keys(cls)->tuple[str|GdType]:
#         return ("uid://", SubResourceNode)

#     @classmethod
#     def get_bl_keys(cls)->tuple[str|Any]:
#         return ("uid://", bpy.types.Node)
=======
        return ## New object, added to parent's children
>>>>>>> bd96feba7fb3a0548806ac0b71e8b553defb5134:GdBl/structure/transformers/core.py
