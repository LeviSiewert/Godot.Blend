from typing import Generator, Any, Callable
from inspect import isgeneratorfunction, isgenerator
from contextvars import ContextVar, copy_context
from collections import namedtuple

MemoEntry = namedtuple("Memo", ["result", "cache", "generator", "context"])

class _UNSET:...

class Transformer():
    contextual : ContextVar|bool = True
    memoized : ContextVar|bool = True
    caching : ContextVar|bool = True

_EMPTY_DICT = {}

class Session():
    memo : dict
    get_id : Callable = id

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
                return memo.context.run(memo.generator.send, **settings, step=step)

            elif not allow_restart_generator:
                ## Case where cache[step] is never fullfilled while executing, generator is complete and this is called again
                raise Exception("Tranform query already completed, request non-normal. \n Check requested step, caching & memoization flags, context dependent steps for caching options before considering the `allow_restart_generator` option  ")

        t : Transformer = self.find_transformer(node)

        ## Integrate flags/settings:
        contextual = t.contextual if isinstance(t.contextual, bool) else t.contextual.get()
        _settings = {
            "step" : step,
            "memoized" : t.memoized if isinstance(t.memoized, bool) else t.memoized.get(),
            "caching" : t.caching if isinstance(t.caching, bool) else t.caching.get(),
            "contextual" : t.contextual if isinstance(t.contextual, bool) else t.contextual.get(),
        }.update(settings)

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

            if contextual:
                ctx = copy_context
            else:
                ctx = None

            self.memo[uid] = MemoEntry(
                result = _UNSET,
                cache = None,
                generator = iterator,
                context = ctx, 
            )

        return iterator.send(settings)


    @staticmethod
    def _runw(_memo:MemoEntry, func, *args, **kwargs):
        if _memo.context is None:
            return func(*args, **kwargs)
        _memo.context.run(func, *args, **kwargs)

    def iterator(self, uid:int, transform:Generator, /, contextual:bool=True, memoized:bool=True, caching:bool=True, send_val:Any=None)->Generator[]:
        ''' iterators through child transformer and integrates flags  
        Adds to Memo
        Returns None if step not met, even if internal generator completes
        Will clean self from memo at completion if `memoized` 
        settings are sent from every yield
        '''

        settings = _EMPTY_DICT
        send_value = None

        if (not memoized):
            memo = MemoEntry(None,None,None,copy_context())

        c = True
        while c:
            if memoized:
                memo = self.memo[uid]
            send_value = settings.get("send_value", send_value)

            flag = transform.send(send_val)

            if isinstance(flag, STEP):
                do_yield, yield_val, send_val = flag.intigrate(self, )



    #     while c:
    #         if memoized:
    #             memo = self.memo[uid]

    #         try:
    #             res = self._runw(self.memo.send, send_val)

    #             if isinstance(res, Flag):
    #                 res.integrate()
    #                 ... #if:
    #                 settings = yield res

    #             else:
    #                 raise Exception(...)
            

    #         except StopIteration as e:
    #             if memoized:
    #                 self.memo[uid] = MemoEntry(result=e.value, generator=memo.generator, context=memo.context, cache=memo.cache)
    #             return e.value
        
