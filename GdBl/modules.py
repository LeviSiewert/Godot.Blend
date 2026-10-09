from __future__ import annotations

from typing import Type, Any
from ..GdPy.core.transformer import TransformerSet, Session

class ModuleOption():
    _type = "Option"
    id : str
    desc : str

    type : Type[str|int|bool|list[str]]
    default : str|int|bool = None
    value : str|int|bool

class Module():
    _type = "ModuleVersion"
    ''' Versionable Module that produces a Transformer set
    - if placed in standalone file, mark with .bl.py to load. file will be loaded as a module with GdPy, GdBl as global modules
    - to_gdpy_settings & fr_gdpy_settings are displayed to the user on export. Options should be integrated into the transformer set.
        - Settings are headed with Module name
    '''
    uid : str       ## Matcheed to groups via this
    name : str      ## Display to user
    version : str   ## Selected fr groups via this
    desc : str      ## Display to user
    
    global_settings : dict[str,ModuleOption]

    to_gdpy_settings : dict[str, ModuleOption]
    fr_gdpy_settings : dict[str, ModuleOption]

    def get_fr_GdPy_set(self, session:Session, global_settings:dict[str,Any], settings:dict[str,Any])->TransformerSet|None:
        ''' Return a TransformerSet instance or None, factoring settings into options as req, 
        session will have internal/default TransformerSets already incorperated, but not other modules '''

    def get_to_GdPy_set(self, session:Session, global_settings:dict[str,Any], settings:dict[str,Any])->TransformerSet|None:
        ''' Return a TransformerSet instance or None, factoring settings into options as req, 
        session will have internal/default TransformerSets already incorperated, but not other modules '''

class ModuleGroup():
    _type = "ModuleGroup"
    uid : str
    active : Module
    modules : list[Module]

    def get_fr_GdPy_set(self, session, global_settings:dict[str,Any], settings:dict[str,Any])->TransformerSet|None:
        if self.active is None:
            return None
        return self.active.get_fr_GdPy_set(session, global_settings, settings)
        
    def get_to_GdPy_set(self, session, global_settings:dict[str,Any], settings:dict[str,Any])->TransformerSet|None:
        if self.active is None:
            return None
        return self.active.get_to_GdPy_set(session, global_settings, settings)
        
