from contextvars import ContextVar
from typing import Generator, Any

class Flag():
    def __init__(self, id, obj):
        self.identifier = id
        self.obj = obj

    def intigrate(self)->tuple[Any, Any]:
        ''' Return a value that will be yielded, and a value that will be echod back into yield (unless external settings insert) '''
        return self.identifier, self.identifier

class STEP(Flag):
    ...

cvar = ContextVar("")

def gen():
    cvar.get().append("PRE")

    res = yield STEP("A", "a")
    cvar.get().append(res)

    res = yield STEP("B", "b")
    cvar.get().append(res)

    res = yield STEP("C", "c")
    cvar.get().append(res)

    return "D"

class _UNSET:...

def middle(generator:Generator, settings:dict):
    ''' Storing send_value state inside this generator '''
    send_val = None
    c = True
    _settings = None
    while c:
        try:
            if not ((_val := settings.get("send",_UNSET))is _UNSET):
                send_val = _val
                del _val 

            flag = generator.send(send_val)

            if isinstance(flag, STEP) and (flag.identifier == settings.get("step")):
                yieldval, send_val = flag.intigrate()
                _settings = yield yieldval
            else:
                yieldval, send_val = flag.intigrate()
                _settings = yield send_val

            if not (_settings is None):
                if not (_settings is None):
                    settings = _settings
                else:
                    settings = {} 
                    ## I think? Outer generator step replaces settings when it occurs

        except StopIteration as e:
            return e.value
        except:
            raise

cache = {}

def outer(obj, insert_val=None, **settings):
    ''' Accessor, settings '''

    if not (id(obj) in cache.keys()):
        cache[id(obj)] = (middle(gen(), settings), settings)
    else:
        cache[id(obj)][1].clear()
        cache[id(obj)][1].update(settings)
    _gen, settings = cache[id(obj)]
    try:
        # return next(_gen)
        return _gen.send(insert_val)
    except StopIteration as e:
        return e.value

def test_full():
    cvar.set([])
    generator = gen()

    assert "A" == outer(generator, stop = "A")
    assert "B" == outer(generator, stop = "B")
    assert "C" == outer(generator, stop = "C")
    assert "D" == outer(generator, stop = None)
    cvar.get() == ["PRE", "A", "B", "C"]
