import bpy 

from typing import Any
from contextvars import ContextVar
from enum import Enum as _Enum
from abc import (
    ABC as _ABC, 
    abstractmethod as _abstractmethod
)

from ....GdPy.core.transformer import Transformer, TransformerRuleset, TransformerModule, Context
from ....GdPy.core.property_collection import PropertyCollection as _PropertyCollection
from ....GdPy.core.structure import _Resource

class _Dependency():
    pass

class DependencyInterface(_ABC):
    ''' Standard interface for declaring and resolving deps during transformation
    Deps are assumed to be resolved at *latest* allowence.
    '''
    class Scope(_Enum):
        ANY = 0
        SUB_RES = 1 # SubResource() : Resource scope
        EXT_RES = 2 # ExtResource() : Resource routed-Project scope 
        DIR_RES = 3 # RID() | ResourceRef() : Project scope

    resource : _Resource
    dependencies : dict[Scope, list[_Dependency]]

    def __init__(self, resource:_Resource):
        self.resource = resource
        self.dependencies = {
            self.Scope.SUB_RES : [],
            self.Scope.EXT_RES : [],
            self.Scope.DIR_RES : [],
        }

    @_abstractmethod
    def resolve(self, *args):
        pass

    @_abstractmethod
    def fetch(self, scope:Scope=Scope.ANY, id:str=None, uid:str=None, path:str=None, now:bool=False, default:Any=None)->tuple[Any,Any|None]|None:
        ''' Same settings as declare, but fetching. '''

    @_abstractmethod
    def declare(self, scope:Scope=Scope.ANY, id:str=None, uid:str=None, path:str=None, now:bool=False)->tuple[Any,Any|None]:
        ''' Declare and optionally resolve a dependency

        scope: 
            determines required scope. `ANY` allows `( c.settings | object | Type[object] ` to determine this.
            Otherwise it's considered to be required.

        uid :
            Overrides to this variable in the scope.
        path: 
            Overrides to this variable in the scope.
        id:
            force `sub_res.id` or `ext_res.id`
        now:
            require that this object is transformed NOW and returned

        returns:
            a tuple[ref,obj|None]
            [obj|None] : 
                depends on if the object has already been transformed  
            [ref] : 
                can be str or reference object depending on system needs.
                # into blender may require a string to attach to props 
        '''
        

class PyToBlContext(Context):
    def __init__(self):
        super().__init__()
        self.existing_object = ContextVar("existing_object", default=None)
        self.property_collection = ContextVar("property_collection", default=None)
        self.collection = ContextVar("collection", default=None)


PyToBlTransformer = Transformer

PyToBlRuleset = TransformerRuleset

PyToBlModule = TransformerModule


class BlToPyContext(Context):
    existing_object : ContextVar[Any]
    property_collection : ContextVar[_PropertyCollection]
    collection : ContextVar[bpy.types.Collection]
    dependencies : ContextVar[DependencyInterface]

    def __init__(self):
        super().__init__()
        self.existing_object = ContextVar("existing_object", default=None)
        self.property_collection = ContextVar("property_collection", default=None)
        self.collection = ContextVar("collection", default=None)
        self.dependencies = ContextVar("dependencies", default=None)

BlToPyTransformer = Transformer

BlToPyRuleset = TransformerRuleset

BlToPyModule = TransformerModule
