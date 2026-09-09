from contextvars import ContextVar
from typing import Generator, Any

class Flag():
    def __init__(self, id, obj):
        self.identifier = id
        self.obj = obj

    def intigrate(self)->Any:
        return self.identifier

cvar = ContextVar("")

def gen():
    cvar.get().append("PRE")

    res = yield Flag("A", "a")
    cvar.get().append(res)

    res = yield Flag("B", "b")
    cvar.get().append(res)

    res = yield Flag("C", "c")
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

            resulting_val = generator.send(send_val)
            send_val = resulting_val.intigrate()
            
            if resulting_val.identifier == settings["stop"]:
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