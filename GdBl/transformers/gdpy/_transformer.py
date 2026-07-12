import bpy 

from typing import Any, Generator
from contextvars import ContextVar
from enum import Enum as _Enum
from abc import (
    ABC as _ABC, 
    abstractmethod as _abstractmethod
)

from ....GdPy.core.transformer import Transformer, TransformerRuleset, TransformerModule, Context
from ....GdPy.core.property_collection import PropertyCollection as _PropertyCollection
from ....GdPy.core.structure import _Resource

from ....GdPy.core.nodes import (
    ResourceScene,
    Node,
)
from ....GdPy.core.resources import (
    ResourceTres,
    ExtResource,
    ExtResourceRef,
    SubResource,
    SubResourceRef,
)
from ....GdPy.core.structure import (
    ResourceRef,
    RID,
)


class Scope(_Enum):
    ANY = 0
    SUB_RES = 1 # SubResource() : Resource scope
    EXT_RES = 2 # ExtResource() : Resource routed-Project scope 
    DIR_RES = 3 # RID() | ResourceRef() : Project scope

class _Dependency(_ABC):
    resulting_obj : Any = None

    @_abstractmethod
    def fetch(self,)->None|Any:
        pass

    @_abstractmethod
    def make_reference(self,):
        pass

    @_abstractmethod
    def resolve(self,):
        pass

class DirResDependency(_Dependency):
    pass

class ExtResDependency(_Dependency):
    pass

class SubResDependency(_Dependency):
    pass

    # source : Any

    # scope : Scope

    # id : str|int
    # uid : str|None = None
    # path : str|None = None

    # def __init__(self, source:Any=None, id:str=None, uid:str=None, path:str=None):
    #     pass

class DependencyInterface(_ABC):
    ''' Standard interface for declaring and resolving deps during transformation
    Deps are assumed to be resolved at *latest* allowence.
    '''

    resource : _Resource

    def __init__(self, c, resource:_Resource):
        self.resource = resource
        self.data = {
            Scope.SUB_RES : [],
            Scope.EXT_RES : [],
            Scope.DIR_RES : [],
        }

    @_abstractmethod
    def resolve_subres(self)->Generator:
        ## Call and resolve iterativly, with new objects populating the lists.
        pass

    @_abstractmethod
    def resolve_extres(self)->Generator:
        ## Call and resolve iterativly, with new objects populating the lists.
        pass

    @_abstractmethod
    def resolve_dirres(self)->Generator:
        ## Call and resolve iterativly, with new objects populating the lists.
        pass


    def declare(self, c, src:Any, scope:Scope=Scope.ANY, resolve_now=False, **kwargs)->tuple[Any,_Resource|None] | None:
        ## TODO: Force new within scope, force context.
        ## TODO ISSUE:
        # if context *could* affect the result, discovery order *would* affect object generation results
        # The only ways to fix would be to:
        #   - Not have context matter
        #   - Re-export each time context is different and merge w/a

        # determines required scope. `ANY` allows `( c.settings | object | Type[object] ` to determine this.
        if scope is Scope.ANY:
            scope, def_data = self.get_depdata_from_obj(src)
        else:
            _, def_data = self.get_dep_data_from_obj(src)

        kwargs = def_data | kwargs
        
        dep : _Dependency = None
        
        match scope:
            case Scope.EXT_RES:
                dep = self.declare_subresource(c, src, **kwargs)
            case Scope.SUB_RES:
                dep = self.declare_extresource(src, **kwargs)
            case Scope.DIR_RES:
                dep = self.declare_resource(src, **kwargs)
            case _:
                raise Exception()
        
        assert dep

        if resolve_now:
            dep.resolve()

        return (dep.make_reference(), dep.resulting_obj)


    def declare_subresource(self, c, src:Any, id:str):
        existing = filter(lambda x: any((x.src is src), ((x.id == id) and id)), self.data[Scope.SUB_RES])
        assert len(existing) <= 1
        if existing: 
            return existing[0]

        dep = SubResDependency(c, src, id:str)
        self.data[Scope.SUBRES].append(dep)
        return dep 

    def declare_extresource(self, src:Any, id:str, uid:str, path:str):
        existing = filter(lambda x: any((x.src is src), ((x.id == id) and id), ((x.uid == uid) and uid), ((x.path == path) and path)), self.data[Scope.EXT_RES])
        assert len(existing) <= 1
        if existing: 
            return existing[0]
        
        res_dep = self.declare_resource(src, uid, path)
        
        dep = ExtResDependency(res_dep)
        self.data[Scope.EXT_RES].append(dep)
        return dep 


    def declare_resource(self, src:Any, uid:str, path:str):
        existing = filter(lambda x: any((x.src is src), ((x.uid == uid) and uid), ((x.path == path) and path)), self.data[Scope.DIR_RES])
        assert len(existing) <= 1
        if existing: 
            return existing[0]

        dep = DirResDependency(src, )
        self.data[Scope.DIR_RES].append(dep)
        return dep 
    


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
