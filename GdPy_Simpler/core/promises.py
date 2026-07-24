from .property_collection import DelayedReference
from .collections import CollectionRef
from .structure import ExtResourceRef, Resource, StructContext
from .signals import Signal

class SubResource(DelayedReference, CollectionRef):
    ''' Construction utility object, as delayed references they are replaced on population of target object. 
    As a safe fallback these will write to disk even when not fullfilled. 
    w/ self.context context will be fullfilled by property objects.
    '''
    
    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.updated = Signal(self)
        self.context.callback("resource", self._on_resource_set)

    def __init__(self, key:str):
        self.__setup__()
        self.set_key(key, update=False)
    
    def _on_resource_set(self, res:Resource|None):
        if res is None:
            self.set_col(None)
            return
        self.set_col(res.subresources)

    def _on_updated(self, k, v:Resource|None):
        if not (v is None):
            self.replace(v)

class ExtResource(DelayedReference, CollectionRef):
    ''' Construction utility object, as delayed references they are replaced on population of target object. 
    As a safe fallback these will write to disk even when not fullfilled. 
    w/ self.context context will be fullfilled by property objects.
    '''

    def __setup__(self):
        super().__setup__()
        self.context = StructContext()
        self.updated = Signal(self)
        self.context.callback("resource", self._on_resource_set)

    def __init__(self, key:str):
        self.__setup__()
        self.set_key(key, update=False)
    
    def _on_resource_set(self, res:Resource|None):
        if res is None:
            self.set_col(None)
            return
        self.set_col(res.extresources)

    def _on_updated(self, k, v:ExtResourceRef|None):
        if not (v is None):
            v.updated

    def _on_extresource_found(self, key:None, res:Resource):
        pass