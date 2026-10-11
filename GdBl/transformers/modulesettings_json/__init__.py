''' Conversion of BlModuleGroup to and from preferences '''
from typing import Iterable

from ....GdPy.core.transformer import Session, TransformerSet, Transformer, TransformerOptions, TRANSFORM, TRANSFORM_CHILDREN, STEP
from ...preferences import ModuleGroup as BlModuleGroup, ModuleVersion as BlModuleVersion, ModuleOption as BlModuleOption, Project as BlProject, Preferences as BlPreferences
from ...modules import ModuleGroup as PyModuleGroup, ModuleVersion as PyModuleVersion, ModuleOption as PyModuleOption

def make_ds_to_json(extras : Iterable[TransformerSet]): 
    return Session([]) #TODO: Stub

def make_json_to_ds(extras : Iterable[TransformerSet]):
    return Session([]) #TODO: Stub