from contextvars import ContextVar
from typing import Generator

class Flag():
    def __init__(self, id, obj):
        self.identifier = id
        self.obj = obj

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

def middle(generator:Generator, settings:dict):
    ''' Storing send_value state inside this generator '''
    send_val = None
    c = True
    while c:
        try:
            resulting_val = generator.send(send_val)
            send_val = resulting_val.identifier
            if resulting_val.identifier == settings["stop"]:
                yield send_val
        except StopIteration as e:
            return e.value
        except:
            raise

cache = {}
def outer(obj, **settings):
    ''' Accessor, settings '''

    if not (id(obj) in cache.keys()):
        cache[id(obj)] = (middle(gen(), settings), settings)
    else:
        cache[id(obj)][1].clear()
        cache[id(obj)][1].update(settings)
    _gen, settings = cache[id(obj)]
    try:
        return next(_gen)
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