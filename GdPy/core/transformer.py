from __future__ import annotations
from typing import Generator, Any, Callable, Iterable
from inspect import isgeneratorfunction, isgenerator, isclass
from contextvars import ContextVar, copy_context
from contextlib import contextmanager
from collections import namedtuple

class _UNSET:...
_EMPTY_DICT = {}

@contextmanager
def cvar_as(cvar:ContextVar, value):
    t = cvar.set(value)
    yield
    cvar.set(t)

class Flag():
    ''' Am abstract class who's implimentations are yielded by a `Transformer.transform` ('Inner Generator') to a `Session._transform` ("Middle Generator")
    The Middle Generator then calls `{Flag}.integrate(...)` and recieves (do_yield, yield_val, send_val)
    '''
    def intigrate(self, session:Session, uid:Any, memo:MemoEntry, settings:dict, contextual:bool, memoized:bool, caching:bool)->Any:
        ''' Called by 'Middle Generator', returns tuple(do_yield, yield_val, send_val)
        Returns
        - do_yield : bool -> escapes the 'Middle Generator' with the yield_val 
        - yield_val : Any -> step value of the 'Middle Generator' when `do_yield`
        - send_val : Any -> value sent back to 'Inner Generator' unless 'Middle Generator' settings override this value. 
        '''
        raise NotImplementedError(self.__class__)

class STEP(Flag):
    ''' Allows for a caller to interupt construction, and cache w/a '''
    __slots__ = tuple()
    # __slots__ = ("caching","step","value") 
    caching : bool = True
    step : str
    value : Any|None|_UNSET = _UNSET

    def __init__(self, step:str, value:Any=_UNSET, /, caching : bool = True):
        self.step = step
        self.value = value
        self.caching = caching

    def intigrate(self, session, uid, memo, settings, contextual:bool, memoized:bool, caching:bool)->Any:
        do_yield = self.step == settings.get("step",None)

        if (memoized and caching and self.caching and (not (self.value is _UNSET))):
            if memo.cache is None:
                session.set_cache(uid, {self.step:self.value})
            else:
                memo.cache[self.step] = self.value
        elif self.caching and (not (self.value is _UNSET)):
            raise Exception("Caching is enabled but value is not set!")

        # do_yield, yield_val, send_val
        return do_yield, self.value, self.step
        
class TRANSFORM(Flag):
    ''' Essentially a macro for session.transform(...), but is prefered in use for clarity '''
    __slots__ = tuple()
    # __slots__ = ("item", "settings")
    item : Any
    settings : dict

    def __init__(self, item:Any, **settings):
        self.item = item
        self.settings = settings

    def intigrate(self, session, uid, memo, settings, contextual:bool, memoized:bool, caching:bool)->Any:
        return False, None, session.transform(self.item, **self.settings)

class TRANSFORM_CHILDREN(Flag):
    ''' Essentially a macro for session.transform(...), but is prefered in use for clarity '''
    __slots__ = tuple()
    # __slots__ = ("children", "as_generator", "settings")
    children : Iterable
    as_generator : bool
    settings : dict

    def __init__(self, children:Iterable, /, as_generator:bool=False, **settings):
        self.children = children
        self.settings = settings
        self.as_generator = as_generator

    def intigrate(self, session, uid, memo, settings, contextual:bool, memoized:bool, caching:bool)->Any:

        def _generator():
            # try:
            for i in self.children:
                yield session.transform(i, **self.settings)
            # except TypeError as e:
            #     raise TypeError(self.children, "is not Iterable!")
            # except:
            #     raise

        if self.as_generator:
            return False, None, _generator()
        
        return False, None, tuple(_generator())    

class Transformer[I:Any, O:Any]():
    ''' A container for evaluating matches against a node and returning a "inner generator" that yields flags and a result '''
    contextual : ContextVar|bool = True ## Copies or doesnt copy the current context
    memoized : ContextVar|bool = True
    caching : ContextVar|bool = True
    identifier : str|None = None

    def __init__(self, identifier:str|None=None):
        self.identifier = identifier

    def __repr__(self)->str:
        if not self.identifier is None:
            return f"Transformer({self.identifier})"
        return self.__class__.__name__

    def transform(self, session:Session, node:I)->Generator[Flag, Any, O]:
        ''' AKA : Inner Generator
        A generator that yields flags for the session (via 'Middle Generator') and finally returns a result. 
        
        Notes:
        - The generator itself is cached in a memo until a result is returned if `memoized` and `caching` (See session)
        - The context is copy-on-start of generator, and re-entered whenever the generator is stepped. 

        Instructions:
        - yield flags such as TRANSFORM for all components that can be changed by other session transformers.
            - the 'return' of the `yield flag` via send(transform()) is the resulting changed object
        - yield flags such as STEP for allowing construction interuption, such as width-first transformation.
            - `session.transform(node, step='...')` will refer to cached, otherwise run until step yielded OR transformer completes. 
        - use session.options[...].contextvar to change session state contextually w/a
        - only `Tranformer.memoized = True` if `session.get_id` is unique in session for this object type && it's faster to get_id -> return memo.result 
        - only `Tranformer.caching = True` if Steps are yielded 
        - only `Tranformer.contextual = True` if ContextVars are set && Interupts/Steps are yielded.

        Suggestions:
        - consider `yield from` for repeated operations 
            - ie `res = yield from MACROS_CLASS.Macro(...)`
        '''
        raise NotImplementedError("Abstract class!")
        yield

    def match(self, session:Session, node:Any|I)->bool:
        ''' When part of a TransformerSet this will be checked to see  '''
        raise NotImplementedError("Abstract class!")

class TransformerOptions():
    ''' Class that is instanciated at session creation to hold ContextVars and 'shift' the Cache id space, allowing for context dependent caching.
    TODO: a factory method to generate context vars from type annotations
        IE: `value : ContextVar = False` ->> `self.value = ContextVar(...+"value",default=False)` 
    '''
    def __init__(self, session:Session):
        pass

    def get_id_contributer(self, session:Session, obj:Any)->int:
        ''' Cache id space "shifting", called per get_id '''
        return 0

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

    def match[D:Any](self, session, node:Any, default:D=None)->Transformer|D:
        for t in self.transformers:
            if t.match(session, node):
                return t
        return default


MemoEntry = namedtuple("Memo", ["result", "cache", "generator", "context"])

class Session[T:TransformerSet, O:TransformerOptions]():
    memo : dict[int, MemoEntry]
    transformer_sets : tuple[T]
    options: dict[str, O]
    
    def get_id (self, obj:Any|None)->int:
        return id(obj) + self.get_id_contributor_sum(obj)

    def get_id_contributor_sum(self, obj:Any|None):
        ''' Contibution from active TransformerOptions objects for caching ids, usually from options itself, 
        more effecient proportion than matching transformers again and asking them, same effect. '''
        contr_sum = 0
        for v in self.options.values():
            contr_sum = contr_sum+v.get_id_contributer(self, obj)
        return contr_sum

    def set_cache(self, uid:int, data:dict)->None:
        memo = self.memo[uid]
        if memo.cache is None:
            self.memo[uid] = MemoEntry(
                result = memo.result,
                cache = data,
                generator = memo.generator,
                context = memo.context,
            )

    def __init__(self, transformer_sets:Iterable[T]):
        self.memo = {}
        self.transformer_sets = tuple(transformer_sets)

        self.options = {}
        _options_template = {}
        for ts in self.transformer_sets:
            _options_template.update(ts.options)
        for k,v in _options_template.items():
            self.options[k] = v(self)

    def find_transformer(self, node)->tuple[Generator|Callable,bool]:
        for ts in self.transformer_sets:
            t = ts.match(self, node, None)
            if not (t is None):
                return t
        raise KeyError("Could not determine transformer for:", node)

    def transform(self, node:Any, step:str|None=None, allow_restart_generator:bool=False , **settings)->Any:
        ''' Header function for creating, accessing memo & stepping self.iterator while fetching caches w/a '''

        uid = self.get_id(node)

        if not ((memo:=self.memo.get(uid,None)) is None): ## Is memoized, has some sort of cache
            memo : MemoEntry

            if (not (step is None)) and (not (memo.cache is None)):
                ## Fetch cached and return w/a
                if not((res:=memo.cache.get(step, _UNSET)) is _UNSET):
                    return res

            elif (step is None) and (not (memo.result is _UNSET)):
                ## Fetch cached result and return w/a
                return memo.result
            
            if memo.generator:
                ## Run iterator with settings
                try:
                    return memo.context.run(memo.generator.send, {**settings, "step":step})
                except StopIteration as e:
                    return e.value

            elif not allow_restart_generator:
                ## Case where cache[step] is never fullfilled while executing, generator is complete and this is called again
                raise Exception("Tranform query already completed, request non-normal. \n Check requested step, caching & memoization flags, context dependent steps for caching options before considering the `allow_restart_generator` option  ")

        t : Transformer = self.find_transformer(node)

        ## Integrate flags/settings:
        _settings = {
            "step" : step,
            "memoized" : t.memoized if isinstance(t.memoized, bool) else t.memoized.get(),
            "caching" : t.caching if isinstance(t.caching, bool) else t.caching.get(),
            "contextual" : t.contextual if isinstance(t.contextual, bool) else t.contextual.get(),
        }
        _settings.update(settings)

        if (not isgeneratorfunction(t.transform)):
            ## if straight tra
            res = t.transform(self, node) 

            if _settings["memoized"]:
                self.memo[uid] = MemoEntry(
                result = res,
                cache = None,
                generator = None,
                context = None
            ) 
            return res

        ## create iterator and send first result
        if isgeneratorfunction:
            iterator = self.iterator(uid, t.transform(self, node), **_settings)
        else: 
            ## Generator that has already been started for some reason.
            iterator = self.iterator(uid, t.transform, **_settings)



        if _settings["memoized"]:

            if _settings["contextual"]:
                ctx = copy_context()
            else:
                ctx = None

            self.memo[uid] = MemoEntry(
                result = _UNSET,
                cache = None,
                generator = iterator,
                context = ctx, 
            )

        try:
            return next(iterator)
        
        except StopIteration as e:
            return e.value

    @staticmethod
    def _runw(_memo:MemoEntry, func, *args, **kwargs):
        if _memo.context is None:
            return func(*args, **kwargs)
        _memo.context.run(func, *args, **kwargs)

    def iterator(self, uid:int, transform:Generator, /, contextual:bool=True, memoized:bool=True, caching:bool=True, send_val:Any=None, **settings)->Generator:
        ''' AKA: 'Middle Generator' 
        - iterators through child transformer and integrates flags  
        - Added to Memo
        - Returns None if step not met, even if internal generator completes
        - Will clean self from memo at completion if `memoized` 
        - Settings are sent at/from every yield
        '''

        send_value = None

        if (not memoized):
            memo = MemoEntry(None,None,None,context=copy_context())

        c = True
        while c:

            try:
                ## Send value fr settings
                send_value = settings.get("send_value", send_value)

                ## Actual operation of 'Inner Generator'
                flag = transform.send(send_val)

                if memoized:
                    ## MemoEntry is immutable and entry may have changed per iter as flags integrate.
                    memo = self.memo[uid]

                if isinstance(flag, Flag):
                    do_yield, yield_val, send_val = flag.intigrate(self, uid, memo, settings, contextual=contextual, memoized=memoized, caching=caching)

                    if do_yield:
                        ## return yield_val, recieve settings from Session.Transform call
                        _settings = yield yield_val
                        if not (_settings is None):
                            settings = _settings
                        del _settings
                else: 
                    raise Exception("UNKNOWN Flag:", flag)

            except StopIteration as e:
                c = False
                if memoized:  
                    ## clean self from memo             
                    memo = self.memo[uid]
                    self.memo[uid] = MemoEntry(result=e.value, cache=memo.cache, generator=None, context=None)
                return e.value

            except:
                raise
            
    def __repr__(self):
        return self.__class__.__name__+"()"
