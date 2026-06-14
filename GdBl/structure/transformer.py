from __future__ import annotations
from abc import ABC, abstractmethod
from ...GdPy.structure.core import GdType
from contextvars import ContextVar
from typing import Any
from inspect import isgeneratorfunction

class BlContext():
    gd_project : ContextVar
    gd_file : ContextVar
    gd_resource : ContextVar
    gd_subresource : ContextVar
    
    bl_project : ContextVar
    bl_file : ContextVar
    bl_resource : ContextVar
    bl_subresource : ContextVar

    bl_collection : ContextVar

class Transformer():
    transfomers : list[TransformerModule]
    
    def fr_blender(self, bl_item):
        pass

    def to_blender(self, gd_item):
        pass

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

class TransformerModule(ABC):
    module_info : dict

    @classmethod
    @abstractmethod
    def get_gd_keys(cls)->tuple[str|GdType]:
        """ Return Keys for GD->BL transformer """
        return tuple()

    @classmethod
    @abstractmethod
    def get_bl_keys(cls)->tuple[str|Any]:
        """ Return Keys for BL->GD transformer """
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
        

class TransformerModuleSubResource(TransformerModule):
    @abstractmethod
    def fr_blender(self, c:BlContext, bl_item, _children:dict):
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
    def to_blender(self, c:BlContext, gd_item, _children:dict):
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