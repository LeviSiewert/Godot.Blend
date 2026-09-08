from __future__ import annotations
from typing import Any, Generator, Iterable
from contextvars import ContextVar
from inspect import isgenerator, isclass

# def tranform(session, node:Any)->Generator[Flag, None|Any, Any]:
#     yield RESULT(...)

#     yield STEP("", ...)
#     ## Outer scope, return is None

#     children : Any = yield TRANFORM_CHILDREN(...)
#     ## Calls outer scope to call transform, blocking and within the current session
#     ## Best pracitce atm due to desire for:
#         # Tree traversal siblings first
#         # Blocking child escape // dependent transformations
#             # Ie child Escapes, but isnt fully transformed due to waitng on another flag?

#     children : Generator = yield TRANFORM_CHILDREN_GENERATOR(...)
#     ## Calls session to transform each upon read.


#     return result

class _UNSET:...

class Flag():
    def integrate(session, indv_cache, res):
        raise NotImplementedError()
        
class RESULT(Flag):
    obj:Any
    def __init__(self, obj:Any):
        self.obj = obj
    def integrate(self, session:Session, transformer_id:int, indv_cache:dict):
        indv_cache["RESULT"] = self.obj
# class ESCAPE_RESULT(Flag): EXACT BEHAVIOR UNKOWN

class STEP(Flag):
    step_id : str
    obj : Any
    def __init__(self, step_id:str, obj:Any):
        self.step_id = step_id
        self.obj = obj
    def integrate(self, session:Session, transformer_id:int, indv_cache:dict):
        indv_cache[self.step_id] = self.obj
# class ESCAPE_STEP(Flag): EXACT BEHAVIOR UNKOWN

# class BUFFER(Flag):
#     def __init__(self, buffer_id:str, obj:str):
#         super().__init__()

# class MAKE_BUFFER():
#     def __init__(self, buffer_id:str):
#         self.buffer_id = buffer_id
#     def __integrate__():
#         pass
#     def enterscope() # Add and remove from ctx? As interupt would *kinda* fuck with it 
#     def exitscope() # Add and remove from ctx? As interupt would *kinda* fuck with it 


class SWAP_GENERATOR(Flag):
    def __init__(self, generator, value=None):
        self.generator = generator
        self.value = value

    def integrate(self, session, indv_cache, res)->Generator:
        ## Value is replacement for transform.val, used in generator.send() for value insertion from outer scope
        return self.generator, self.value

class TRANFORM_CHILDREN_GENERATOR(Flag):
    # CURRENTLY the results would have to be processed by the caller if any flags ESCAPE
    # In the future it should be a SWAP_GENERATOR that wraps the original somehow?

    def __init__(self, children:Iterable, **settings):
        self.children = children 
        self.settings = settings

    def intigrate(self, session:Session, tranformer_id:int, indv_cache:dict)->Generator:
        children = self.children.__iter__()
        settings = self.settings

        def wrapped():
            for child in children:
                _r = session.transform(child, **settings)
                yield _r

        return wrapped()
        
    
class TRANFORM_CHILDREN(SWAP_GENERATOR):
    def __init__(self, children:Iterable, **settings):
        self.children = children 
        self.settings = settings

    def intigrate(self, session:Session, transformer_id:int, indv_cache:dict)->Generator:
        ''' Methodolodgy is nesting the generator to structure for the future ESCAPE logic that has undefined desired behavior '''
        r = session.memo[transformer_id]
        current_generator = r[2]

        children = self.children.__iter__()
        settings = self.settings

        def wrapped():

            result = []

            c = True
            while c:
                try: 
                    child = next(children)
                    _r = session.transform(child, **settings)
                    result.append(_r)
                except StopIteration:
                    c = False

            # current_generator.send(result) ## Return results to original generator
            yield SWAP_GENERATOR(current_generator, value=result)
            ## Swap back to current generator

        return wrapped(), None

class TransformerModule[I:Any, O:Any]():

    def __init__(self, identifier:str|None=None):
        self.identifier = identifier

    def __repr__(self):
        if self.identifier is None:
            return self.__class__.__name__
        else:
            return f"{self.__class__.__name__}::{self.identifier}"

    def match(self, obj:I)->bool:
        return False

    def transform(self, session:Session, node:I)->Generator[Flag,Any,O]:
        raise NotImplementedError(f"Abstract Transformer module {self.__class__.__name__} called with {node}")
        yield

class TransformerSet():
    def __init__(self, identifier:str, *modules):
        self.identifier = identifier
        m = []
        for r in modules:
            if isclass(r):
                m.append(r())
        self.modules = tuple(m)

    def match[D](self, node:Any, default:D)->D|Generator:
        for m in self.modules:
            if m.match(node):
                return m.transform
        return default

class Session():
    memo : dict[int, tuple[Any|_UNSET, dict|None, Generator|None]] #Map of id(node) : result, cache, generator, ...
    # buffers : ContextVar[dict[str, list]]
    rulesets : ContextVar[list[TransformerSet]]

    def __init__(self, rulesets:list[TransformerSet]):
        self.memo = {}
        # self.buffers = ContextVar("Buffers", default={})
        self.rulesets = ContextVar("Rulesets", default=rulesets)

    def make_generator(self, node)->Generator:
        rulesets = self.rulesets.get()
        for r in rulesets:
            t = r.match(node, _UNSET)
            if not (t is _UNSET):
                if not isgenerator(t):
                    def t(*args, **kwargs):
                        return t(*args, **kwargs) 
                        yield
                return t(self, node)
        raise KeyError()

    def ensure_transform(self, node:Any)->tuple[dict,Generator|None]:
        ''' Ensure a cache and generator exists. '''
        res = self.memo[id(node),None]
        if not (res is None):
            return res
        res = (_UNSET, {}, self.make_generator(node))
        self.memo[id(node)] = res
        return res


    @staticmethod
    def generator_escape(g:Generator, cvar:ContextVar)->Generator:
        result = yield from g
        cvar.set(result)

    def transform(self, node, step:str|None=None):

        result, indv_cache, generator = self.ensure_transform(node)
        if not ((res:=indv_cache.get(step, result)) is _UNSET):
            return res

        res = ContextVar("", default=_UNSET)
        generator : Generator = self.generator_escape(generator, res)

        c = False
        send_val = None
        while c:
            try:
                res = generator.send(send_val)

                if isinstance(res, Flag):
                    if isinstance(res, STEP) and (res.step_id == step):
                        send_val = res.integrate(self, id(node), indv_cache)
                        return res.value
                    elif isinstance(res, SWAP_GENERATOR):
                        generator, send_val = res.integrate(self, id(node), indv_cache)
                        _current = self.memo[id(node)]
                        self.memo[id(node)] = (_current[0], _current[1], generator)
                        del _current 
                        continue
                    else:
                        send_val = res.integrate(self, id(node), indv_cache)
                    
                else:
                    raise Exception("Non-Flag yielded, unknown desire!", res)

            except StopIteration:
                c = False

            
        ret_value = res.get()
        if ret_value is None:
            indv_cache["RETURN"] = indv_cache.get("RESULT", None)
        else:
            indv_cache["RETURN"] = ret_value

        self.memo[id(node)] = (ret_value, indv_cache, None) ## Clear the empty generator
        return ret_value

    

