from __future__ import annotations
from types import Any,Callable,Generator,Iterable
from ..core.transformer_v2 import TransformerModule, TransformerModuleTest
from ..core.primitives import MultiKeyCollection, Context

class GdPyModuleCollection(): #MultiKeyCollection):
    ''' Module container that fetches, previews and loads files that contain GdPyModules
    It also provides the active modules as defined by an external series of settings.
    Future allowences will include hooking/bypassing
    '''
    # DEFER: Determine better methods for possible multi-step/graph transformer resolution??

_MODULE_REQUIRED_KEYS = ("dev","name","desc","version")

class GdPyModuleEntry():
    ''' Container for any series of modules that contain the same name and different versions 
    Only one of any particlar version of a module can be enabled at a time
    '''
    
    name : str
    modules : list[str,GdPyModule]
    active : GdPyModule = None
    registered : bool = False

    def register(self, c:Context, version=None):
        ''' Called when the module is enabled in the env '''

    def unregister(self, c:Context):
        ''' Called when module is disabled in the env, and presented modules will no longer be called '''

    def get_transformers(self, c:Context, key:tuple[str,str]):
        if self.active:
            return self.active.get_transformers(c,key)
        return tuple()

    
    def get_transformer_tests(self, c:Context):
        pass

    def run_transformer_tests():
        pass
    

class GdPyModule():
    ''' Module class that should be implemented in a distributed maner '''

    info : dict[str,Any] = {
        "dev" : "",
        "name" : "",
        "desc" : """ """,
        "version" : "",
        "transformer_modules" : { ## Accessed via get_transformers by deffault
            "py_to_gd" : Iterable[TransformerModule],
            "gd_to_py" : Iterable[TransformerModule],
            "bl_to_py" : Iterable[TransformerModule],
            "py_to_bl" : Iterable[TransformerModule],
        },
        "tests" : { ## Accessed via get_transformer_test
            "a_to_b" : (TransformerModuleTest[...] | Callable | Generator),
        }
    }

    def register(self, c:Context):
        ''' Called when the module is enabled in the env '''

    def unregister(self, c:Context):
        ''' Called when module is disabled in the env, and presented modules will no longer be called '''

    def get_transformers(self, c:Context, key:tuple[str,str])->Iterable[TransformerModule]:
        ''' Return transformers asc with the keys presented. Keys are presented as (from, to) 
        Default is to quiery `self.info["transformer_modules"]["f{key[0]}_to_f{key[1]}"]`
        TODO: Centralize some standard key notations 
        '''
        return self.info.get("transformer_modules", {}).get(f"{key[0]}_to_{key[1]}")
        
    def get_transformer_tests(self, c:Context, key:tuple[str,str])->Iterable[TransformerModuleTest]:
        ''' Return tests asc with a given key set, either to display tests or run tests '''
        return tuple()    
        


