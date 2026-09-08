from __future__ import annotations
from typing import Any, Generator, Iterable
from contextvars import ContextVar
from inspect import isgenerator, isclass

""" This transformer module is best thought of as a methodology for ordering individual transform functions & function substates, and \n
implimentation of dependency transformation via yielding `Flags` that the outer scope respects.

It does this through a generator per `id(node)`, as generators allow for sequencial & interuptable operations.
Matching of `node` to function is dependent on the implimentation of `TransformModule.match`, and is called seq by `TransformerSet`, called seq within `Session.rulesets`

Rulesets should be a contextual variable! 
This means point means that the ruleset can be changed during transformation for any sub-tree.
However; Creating secondary sessions with a second ruleset is a method to get around this, but escapes and similar from sub-Sessions will have to be handled within the transformation function

Through handling of rulesets and session generation, user-created modules will be supported to alter behavior bi-directionally.

Future plans for V2 include:
- BLOCKING / DEPENDENCIES
    - 
- ESCAPE sequences
    - Nested partial transformations (level one - level 2 > level 3 :: ESCAPE -> ?? > level one)
    - Similar to raising exceptions, but using generators and caching to maintain state of sub-transformations & dependencies
- Context variables re-work (implied by escape sequences)
    - semi-local dict that looks upwared within the tree upon missing value (dict is localized on set)
    - dict will be saved within the memo per node
    - Ordering of calls cross the tree will not always be determinisitc, so context and thus dict values could change between yields
- BUFFER
    - Automated list "context" variable w/ callback.
    - Should only be readable by the creator of the buffer. 
    - Usefull for listing nested children for inter-step processing
    - Clearing the buffer should *optionally* be Blocking (Lambda in memo!) 
- CALLBACK_INSERT
    - Append lambda to BUFFER object, one-off func call that sends a value to the generator
    - Blocking !!
    - Blocking via flag in memo?
    - Usefull for (nested object - value insertion) that doesnt rely on `session.context` values
- CALLBACK
    - Append lambda to BUFFER object, call that sends a value.
"""

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

class TRANFORM(Flag):
    def __init__(self, child=None, **settings):
        self.value = child
        self.settings = settings

    def integrate(self, session:Session, tranformer_id:int, indv_cache)->Any:
        return session.transform(self.value, **self.settings)
    
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

    def integrate(self, session:Session, tranformer_id:int, indv_cache)->tuple[Generator,Any]:
        ## Value is replacement for transform.val, used in generator.send() for value insertion from outer scope
        return self.generator, self.value

class TRANFORM_CHILDREN_GENERATOR(Flag):
    # CURRENTLY the results would have to be processed by the caller if any flags ESCAPE
    # In the future it should be a SWAP_GENERATOR that wraps the original somehow?

    def __init__(self, children:Iterable, **settings):
        self.children = children 
        self.settings = settings

    def intigrate(self, session:Session, tranformer_id:int, indv_cache:dict)->tuple[Generator,Any]:
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

    def intigrate(self, session:Session, transformer_id:int, indv_cache:dict)->tuple[Generator,Any]:
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

    def __init__(self, rulesets:list[TransformerSet], memo:Any|None=None):
        self.memo = {}
        if not (memo is None):
            self.memo.update(memo``)
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
                    elif isinstance(res, TRANFORM):
                        send_val = res.integrate(self, id(node), indv_cache)
                        ## Handling an escape sequence here may be required, and some sort of wrapped-resume for outer.
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

    

