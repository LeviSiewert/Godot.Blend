from __future__ import annotations
from abc import ABC, abstractmethod
from ...GdPy.structure.core import GdType
from contextvars import ContextVar
from typing import Any

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

    def matcher(self,item)->TransformerModule:
        if isinstance(item,GdType):
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
    def fr_blender(self, c:BlContext, gd_item, _children:dict, gltf_node=None, edit_subres=None):
        pass