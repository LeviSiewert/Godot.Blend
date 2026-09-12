from __future__ import annotations
from typing import Any, Generator, Iterable, Callable
from contextvars import ContextVar, Context
from inspect import isgenerator, isgeneratorfunction, isclass
from contextlib import contextmanager
# """ This transformer module is best thought of as a methodology for ordering individual transform functions & function substates, and \n
# implimentation of dependency transformation via yielding `Flags` that the outer scope respects.

# It does this through a generator per `self.id_func(node)`, as generators allow for sequencial & interuptable operations.
# Matching of `node` to function is dependent on the implimentation of `TransformModule.match`, and is called seq by `TransformerSet`, called seq within `Session.rulesets`

# Rulesets should be a contextual variable! 
# This means point means that the ruleset can be changed during transformation for any sub-tree.
# However; Creating secondary sessions with a second ruleset is a method to get around this, but escapes and similar from sub-Sessions will have to be handled within the transformation function

# Through handling of rulesets and session generation, user-created modules will be supported to alter behavior bi-directionally.

# Future plans for V2 include:
# - BLOCKING / DEPENDENCIES
#     - 
# - ESCAPE sequences
#     - Nested partial transformations (level one - level 2 > level 3 :: ESCAPE -> ?? > level one)
#     - Similar to raising exceptions, but using generators and caching to maintain state of sub-transformations & dependencies
# - Context variables re-work (implied by escape sequences)
#     - semi-local dict that looks upwared within the tree upon missing value (dict is localized on set)
#     - dict will be saved within the memo per node
#     - Ordering of calls cross the tree will not always be determinisitc, so context and thus dict values could change between yields
# - BUFFER
#     - Automated list "context" variable w/ callback.
#     - Should only be readable by the creator of the buffer. 
#     - Usefull for listing nested children for inter-step processing
#     - Clearing the buffer should *optionally* be Blocking (Lambda in memo!) 
# - CALLBACK_INSERT
#     - Append lambda to BUFFER object, one-off func call that sends a value to the generator
#     - Blocking !!
#     - Blocking via flag in memo?
#     - Usefull for (nested object - value insertion) that doesnt rely on `session.context` values
# - CALLBACK
#     - Append lambda to BUFFER object, call that sends a value.
# """

class _UNSET:...


class Flag():
    def __init__(self):
        ...
    def intigrate(self, session:Session, node_id:int, settings:dict)->Any:
        ...


class STEP(Flag):
    step_id : str
    obj : Any
    caching : bool

    def __init__(self, step_id:str, obj:Any, caching:bool=False):
        self.step_id = step_id
        self.obj = obj
        self.caching = caching

    def intigrate(self, session:Session, node_id:int, settings:dict)->tuple[bool, Any, Any]:
        ''' Returns tuple(Do_Yield:bool, Yield_Value:Any, Send_Echo_Value (Overridable):Any)'''
        if self.caching:
            session.get_cache(node_id)[self.step_id] = self.obj
        return (self.step_id == settings.get("step",_UNSET)), self.obj, self.step_id

class TRANSFORM(Flag):

    def __init__(self, item:Any, **settings):
        self.item = item
        self.settings = settings

    def intigrate(self, session, node_id, settings):
        ''' Returns a call to session.transform '''
        return session.transform(self.item, **self.settings)

class TRANSFORM_CHILDREN(Flag):

    def __init__(self, items:Iterable[Any], as_generator:bool=False, **settings):
        self.items = items
        self.settings = settings
        self.as_generator = as_generator

    def intigrate(self, session, node_id, settings):
        ''' Returns a call to session.transform '''
        
        def _generator():
            for i in self.items:
                yield session.transform(i, **self.settings)

        if self.as_generator:
            return _generator()
        else:
            return tuple(_generator())

class Transformer():
    identifier : str|None = None

    def __init__(self, identifier:str|None=None):
        self.identifier = identifier

    def __repr__(self)->str:
        if not self.identifier is None:
            return f"Transformer({self.identifier})"
        return self.__class__.__name__

    def transform(self, session:Session, node:Any)->Generator[Flag, Any, None]:
        """AKA : Inner Generator"""
        raise NotImplementedError("Abstract class!")
        yield

    def match(self, session:Session, node:Any)->bool:
        raise NotImplementedError("Abstract class!")
        return False

from inspect import getmembers, get_annotations
class TransformerOptions():
    ''' Class that is instancated at session creation, and has a factory method to generate context vars from type annotations
    IE: 
        - `value : ContextVar = False` ->> `self.value = ContextVar(...+"value",default=False)` 
        - where `...` in above is `str(self.id_func(self))`, which prevents overlap of contextvars across sessions w/ the same options objects (and across options objects in the same session)
    '''

    def _generate_contextvars(self):
        # annotations = get_annotations(self)
        for item in getmembers(self):
            if (item[0].startswith("_")): 
                continue
            if (anno:=get_annotations(item[1])) is None:
                continue
            elif (anno is ContextVar) or ((not isclass(anno)) and (isinstance(anno, ContextVar))):
                setattr(self, anno, ContextVar(str(self.id_func(self))+item[0],default=item[1]))

    def __init__(self, session):
        self._generate_contextvars()
        
    
class TransformerSet[T:Transformer, O:TransformerOptions]():
    identifier : str|None = None
    transformers : tuple[T]
    options : dict[str, O]

    def __init__(self, identifier:str, transformers:Iterable[T], options:dict[str,O|Any]=tuple()):
        self.identifier = identifier

        self.options = {}
        self.options.update(options)

        self.transformers = []
        for t in transformers:
            if isclass(t):
                t = t()
            self.transformers.append(t)

    def match[D:Any](self, session, node:Any, default:D=None)->Generator|D:
        for t in self.transformers:
            if t.match(session, node):
                return t.transform
        return default

_EMPTYDICT = {}

class Session[T:TransformerSet, O:TransformerOptions]():
    memo : dict[int, tuple[Any|_UNSET, Generator|None, dict|None, Context|None]] # [result, generator, cache, context]
    ## Context should be nullable, and entered-exited via middle
    transformer_sets : tuple[T]
    options: dict[str, O]
    id_func: Callable = id

    def __init__(self, transformer_sets:Iterable[T], id_func:Callable=id):
        self.id_func = id_func
        self.memo = {}
        self.transformer_sets = tuple(transformer_sets)

        self.options = {}
        _options_template = {}
        for ts in self.transformer_sets:
            _options_template.update(ts.options)
        for k,v in _options_template.items():
            self.options[k] = v(self)

    def find_transformer(self, node)->Generator:
        for ts in self.transformer_sets:
            res = ts.match(self, node, None)
            if not (res is None):
                return res
        raise KeyError("Could not determine transformer for:", node)


    def get_cache(self, node_id, create=True):
        entry = self.memo[node_id]
        cache = entry[2]
        if (entry[2] is None) and create:
            cache = {}
            self.memo[node_id] = entry[0], entry[1], cache, entry[3]
        return cache

    def transform(self, node, **settings):
        ''' AKA: Outer 
        Ensure a memo entry [result,generator,cache] exists, call next() on generator.
        - Inner Generator changes values
        - Middle Generator handles flags (including cache population)
        - Outer function handles ensure memo[item], cache retrival, indexing of middle generator
        '''

        entry = self.memo.get(self.id_func(node), _UNSET)

        if entry is _UNSET:

            maybe_generator = self.find_transformer(node)
            if not( isgenerator(maybe_generator) or isgeneratorfunction(maybe_generator)):
                ctx = Context()
                val = ctx.run(maybe_generator, self, node)
                entry = (val, None, None, None)
                self.memo[self.id_func(node)] = entry
                return val
            
            transformer = self._transform(self.id_func(node), self.find_transformer(node)(self,node), settings)
            entry = (_UNSET, transformer, None, Context())
            self.memo[self.id_func(node)] = entry

            # Fresh transformer; requires next() instead of send()
            try:
                ctx = entry[3]
                return ctx.run(next, entry[1])
            except StopIteration as e:
                self.memo[self.id_func(node)] = (e.value, None, entry[2], None)
                return e.value

        ## Cache retrieval:
        if _cache:=self.get_cache(self.id_func(node), create=False) and (not ((_step_id := settings.get("step", _UNSET) is _UNSET))) :
            if not ((_res:=_cache.get(_step_id, _UNSET)) is _UNSET):
                return _res
        elif not entry[0] is _UNSET:
            return entry[0]

        try:
            ctx = entry[3]
            return ctx.run(entry[1].send, settings)
        except StopIteration as e:
            self.memo[self.id_func(node)] = (e.value, None, entry[2], None)
            return e.value

    def _transform(self, node_id:int, generator:Generator, settings:dict):
        ''' AKA: Middle
        Storing send_value & sub-generator state inside this generator, also handles cache population '''

        send_val = None
        _settings = None

        c = True
        while c:
            try:
                if not ((_val := settings.get("send", _UNSET)) is _UNSET):
                    send_val = _val
                    del _val

                flag = generator.send(send_val)

                ## IMPLIMENT FLAGS BELOW:

                if isinstance(flag, STEP):
                    do_yield, yield_val, send_val = flag.intigrate(self, node_id, settings)
                    if do_yield:
                        _settings = yield yield_val
                    del do_yield
                    del yield_val

                elif isinstance(flag, TRANSFORM):
                    send_val = flag.intigrate(self, node_id, settings)

                elif isinstance(flag, TRANSFORM_CHILDREN):
                    send_val = flag.intigrate(self, node_id, settings)

                ## Outer this.send(...) sends settings for next step(s)
                if not (_settings is None):
                    settings = _settings
                else:
                    settings = _EMPTYDICT

            except StopIteration as e:
                c = False
                return e.value
            except:
                raise

# class _UNSET:...

# class Flag():
#     def integrate(session, indv_cache, res):
#         raise NotImplementedError()
        
# class RESULT(Flag):
#     obj:Any
#     def __init__(self, obj:Any):
#         self.obj = obj
#     def integrate(self, session:Session, transformer_id:int, indv_cache:dict):
#         indv_cache["RESULT"] = self.obj
# # class ESCAPE_RESULT(Flag): EXACT BEHAVIOR UNKOWN

# class STEP(Flag):
#     step_id : str
#     obj : Any
#     def __init__(self, step_id:str, obj:Any):
#         self.step_id = step_id
#         self.obj = obj
#     def integrate(self, session:Session, transformer_id:int, indv_cache:dict):
#         indv_cache[self.step_id] = self.obj
#         return self.step_id

# class TRANFORM(Flag):
#     def __init__(self, child=None, **settings):
#         self.value = child
#         self.settings = settings

#     def integrate(self, session:Session, tranformer_id:int, indv_cache)->Any:
#         return session.transform(self.value, **self.settings)
    
# # class ESCAPE_STEP(Flag): EXACT BEHAVIOR UNKOWN

# # class BUFFER(Flag):
# #     def __init__(self, buffer_id:str, obj:str):
# #         super().__init__()

# # class MAKE_BUFFER():
# #     def __init__(self, buffer_id:str):
# #         self.buffer_id = buffer_id
# #     def __integrate__():
# #         pass
# #     def enterscope() # Add and remove from ctx? As interupt would *kinda* fuck with it 
# #     def exitscope() # Add and remove from ctx? As interupt would *kinda* fuck with it 


# class SWAP_GENERATOR(Flag):
#     def __init__(self, generator, value=None):
#         self.generator = generator
#         self.value = value

#     def integrate(self, session:Session, tranformer_id:int, indv_cache)->tuple[Generator,Any]:
#         ## Value is replacement for transform.val, used in generator.send() for value insertion from outer scope
#         return self.generator, self.value

# class TRANFORM_CHILDREN_GENERATOR(Flag):
#     # CURRENTLY the results would have to be processed by the caller if any flags ESCAPE
#     # In the future it should be a SWAP_GENERATOR that wraps the original somehow?

#     def __init__(self, children:Iterable, **settings):
#         self.children = children 
#         self.settings = settings

#     def intigrate(self, session:Session, tranformer_id:int, indv_cache:dict)->tuple[Generator,Any]:
#         children = self.children.__iter__()
#         settings = self.settings

#         def wrapped():
#             for child in children:
#                 _r = session.transform(child, **settings)
#                 yield _r

#         return wrapped()
        
    
# class TRANFORM_CHILDREN(SWAP_GENERATOR):
#     def __init__(self, children:Iterable, **settings):
#         self.children = children 
#         self.settings = settings

#     def intigrate(self, session:Session, transformer_id:int, indv_cache:dict)->tuple[Generator,Any]:
#         ''' Methodolodgy is nesting the generator to structure for the future ESCAPE logic that has undefined desired behavior '''
#         r = session.memo[transformer_id]
#         current_generator = r[2]

#         children = self.children.__iter__()
#         settings = self.settings

#         def wrapped():

#             result = []

#             c = True
#             while c:
#                 try: 
#                     child = next(children)
#                     _r = session.transform(child, **settings)
#                     result.append(_r)
#                 except StopIteration:
#                     c = False

#             # current_generator.send(result) ## Return results to original generator
#             yield SWAP_GENERATOR(current_generator, value=result)
#             ## Swap back to current generator

#         return wrapped(), None

# class TransformerModule[I:Any, O:Any]():

#     def __init__(self, identifier:str|None=None):
#         self.identifier = identifier

#     def __repr__(self):
#         if self.identifier is None:
#             return self.__class__.__name__
#         else:
#             return f"{self.__class__.__name__}::{self.identifier}"

#     def match(self, obj:I)->bool:
#         return False

#     def transform(self, session:Session, node:I)->Generator[Flag,Any,O]:
#         raise NotImplementedError(f"Abstract Transformer module {self.__class__.__name__} called with {node}")
#         yield

# class TransformerSet():
#     def __init__(self, identifier:str, *modules):
#         self.identifier = identifier
#         m = []
#         for r in modules:
#             if isclass(r):
#                 m.append(r())
#             else:
#                 m.append(r)
#         self.modules = tuple(m)

#     def match[D](self, node:Any, default:D)->D|Generator:
#         for m in self.modules:
#             if m.match(node):
#                 return m.transform
#         return default

# class Session():
#     memo : dict[int, tuple[Any|_UNSET, dict|None, Generator|None]] #Map of self.id_func(node) : result, cache, generator, ...
#     # buffers : ContextVar[dict[str, list]]
#     rulesets : ContextVar[list[TransformerSet]]

#     def __init__(self, rulesets:list[TransformerSet], memo:Any|None=None):
#         self.memo = {}
#         if not (memo is None):
#             self.memo.update(memo)
#         # self.buffers = ContextVar("Buffers", default={})
#         self.rulesets = ContextVar("Rulesets", default=rulesets)

#     def make_generator(self, node)->Generator:
#         rulesets = self.rulesets.get()
#         for r in rulesets:
#             t = r.match(node, _UNSET)
#             if not (t is _UNSET):
#                 if not (isgenerator(t) or (isgeneratorfunction(t))):
#                     def T(*args, **kwargs):
#                         return t(*args, **kwargs) 
#                         yield
#                     return T(self, node)
#                 return t(self, node)
#         raise KeyError("Could not match node to TransformModule!", node)

#     def ensure_transform(self, node:Any)->tuple[dict,Generator|None]:
#         ''' Ensure a cache and generator exists. '''
#         res = self.memo.get(self.id_func(node), None)
#         if not (res is None):
#             return res
#         res = (_UNSET, {}, self.make_generator(node))
#         self.memo[self.id_func(node)] = res
#         return res


#     @staticmethod
#     def generator_escape(g:Generator[Flag, Any, Any], cvar:ContextVar)->Generator:
#         result = yield from g
#         cvar.set(result)

#     def transform(self, node, step:str|None=None):

#         result, indv_cache, generator = self.ensure_transform(node)
#         if not ((res:=indv_cache.get(step, result)) is _UNSET):
#             return res

#         cvar = ContextVar("", default=_UNSET)
#         escape_generator : Generator = self.generator_escape(generator, cvar)

#         c = True
#         send_val = None
#         while c:
#             try:
#                 res = escape_generator.send(send_val)

#                 if not isinstance(res, Flag):
#                     raise Exception("Non-Flag yielded, unknown desire!", res)

#                 if (not (step is None)) and isinstance(res, STEP) and (res.step_id == step):
#                     send_val = res.integrate(self, self.id_func(node), indv_cache)
#                     return res.obj  
                
#                 elif isinstance(res, SWAP_GENERATOR):
#                     generator, send_val = res.integrate(self, self.id_func(node), indv_cache)
#                     _current = self.memo[self.id_func(node)]
#                     self.memo[self.id_func(node)] = (_current[0], _current[1], generator)
#                     del _current 
#                     escape_generator = self.generator_escape(self.generator, cvar)
                
#                 elif isinstance(res, TRANFORM):
#                     send_val = res.integrate(self, self.id_func(node), indv_cache)
#                     ## Handling an escape sequence here may be required, and some sort of wrapped-resume for outer.
#                 else:
#                     send_val = res.integrate(self, self.id_func(node), indv_cache)
#                 res = None

#             except StopIteration:
#                 c = False
#             except:
#                 raise

#         raise Exception(cvar.get())
#         ret_value = cvar.get()
#         if ret_value is None:
#             indv_cache["RETURN"] = indv_cache.get("RESULT", None)
#         else:
#             indv_cache["RETURN"] = ret_value

#         self.memo[self.id_func(node)] = (ret_value, indv_cache, None) ## Clear the empty generator
#         return ret_value

    

