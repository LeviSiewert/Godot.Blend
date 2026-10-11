''' Session that integrates a list of trawled ModuleGroup objects into the blender preferences, updating in place and removing w/a '''

from typing import Iterable

from ....GdPy.core.transformer import Session, TransformerSet, Transformer, TransformerOptions, TRANSFORM, TRANSFORM_CHILDREN, STEP
from ...preferences import ModuleGroup as BlModuleGroup, ModuleVersion as BlModuleVersion, ModuleOption as BlModuleOption, Project as BlProject, Preferences as BlPreferences
from ...modules import ModuleGroup as PyModuleGroup, ModuleVersion as PyModuleVersion, ModuleOption as PyModuleOption


def make_integrate(extras:Iterable[TransformerSet], project:BlProject): 
    return Session([]) #TODO: Stub