from __future__ import annotations
from typing import Any, Generator, Iterable
from contextvars import ContextVar

def tranform(session, node:Any)->Generator[Flag, None|Any, Any]:
    yield RESULT(...)

    yield STEP("", ...)
    ## Outer scope, return is None

    children : Any = yield TRANFORM_CHILDREN(...)
    ## Calls outer scope to call transform, blocking and within the current session
    ## Best pracitce atm due to desire for:
        # Tree traversal siblings first
        # Blocking child escape // dependent transformations
            # Ie child Escapes, but isnt fully transformed due to waitng on another flag?

    children : Generator = yield TRANFORM_CHILDREN_GENERATOR(...)
    ## Calls session to transform each upon read.


    return result

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

class STEP(Flag):
    step_id : str
    obj : Any
    def __init__(self, step_id:str, obj:Any):
        self.step_id = step_id
        self.obj = obj
    def integrate(self, session:Session, transformer_id:int, indv_cache:dict):
        indv_cache[self.step_id] = res

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

# class ABSTRACT_STEP():
#     ''' Run children until 2nd level child returns fullfilled on abstract step? '''
#     ''' Unly'''
#     pass

class Session():
    memo = dict[int, tuple[Any|_UNSET, dict|None, Generator|None]] #Map of id(node) : result, cache, generator, ...

    def make_generator(self, node)->Generator:
        pass

    def ensure_transform(self, node:Any)->tuple[dict,Generator|None]:
        ## Ensure a cache and generator exists.
        res = self.memo[id(node),None]
        if not (res is None):
            return res
        res = (_UNSET, {}, self.make_generator(node))
        self.memo[id(node)] = res
        return res

    def transform(self, node, step:str|None=None):

        result, indv_cache, generator = self.ensure_transform(node)
        if not ((res:=indv_cache.get(step, result)) is _UNSET):
            return res

        res = ContextVar("", default=_UNSET)
        def generator_escape()->Generator:
            result = yield from generator
            res.set(result)

        c = False
        generator : Generator = generator_escape()
        val = None
        while c:
            try:
                res = generator.send(val)

                if isinstance(res, Flag):
                    if isinstance(res, STEP) and (res.step_id == step):
                        val = res.integrate(self, id(node), indv_cache)
                        return res.value
                    elif isinstance(res, SWAP_GENERATOR):
                        generator, val = res.integrate(self, id(node), indv_cache)
                        _current = self.memo[id(node)]
                        self.memo[id(node)] = (_current[0], _current[1], generator)
                        del _current 
                        continue
                    else:
                        val = res.integrate(self, id(node), indv_cache)
                    
                else:
                    val = None
                    raise Exception("Non-Flag yielded, unknown desire!")

            except StopIteration:
                c = False
            
        ret_value = res.get()
        if ret_value is None:
            indv_cache["RETURN"] = indv_cache.get("RESULT", None)
        else:
            indv_cache["RETURN"] = ret_value

        self.memo[id(node)] = (ret_value, indv_cache, None) ## Clear the empty generator
        return ret_value

    

