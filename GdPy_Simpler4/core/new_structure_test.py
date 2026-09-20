from .new_structure import (
    Collection,
    Context,
    Promise,
    Type,
    PromiseContextual,
    PromiseProperty,
    Properties,
    Project,
    File,
    Settings,
    Category,
    FileIO,
    Resource,
    NodePath,
    Node,
)

from typing import Any
from contextvars import ContextVar

class Test_Promise:
    def test_construction(self):
        Promise("", Promise.Type.FILE)
        Promise("", Promise.Type.RESOURCE)
        Promise("", Promise.Type.SUB_RESOURCE)
        Promise({}, Promise.Type.EXT_RESOURCE)
        Promise("", Promise.Type.EXT_RESOURCE_DIRECT)

    def test_resolve(self):
        ''' Utilizing a dummy project object, resolve from project.resources '''
        class _DummyProject():
            def __init__(self):
                self.resources = Collection(key_attr="")

        project = _DummyProject()
        project.resources.data["key"] = "dummy_resource"
        
        context = Context(project = project)
        promise = Promise("key", Promise.Type.RESOURCE)

        assert "dummy_resource" == promise.resolve(context)
        
class Test_PromiseContextual:
    def test_construction(self):
        PromiseContextual("", Promise.Type.RESOURCE, context=None)

    def test_replace_signal(self):
        ''' resolve utilizing signals from project.resources (dummy)'''

        class _DummyProject():
            def __init__(self):
                self.resources = Collection(key_attr="")

        project = _DummyProject()
        context = Context(project = project)

        promise = PromiseContextual("key", Promise.Type.RESOURCE, context=context)

        cvar = ContextVar("")
        promise.replace.connect(lambda value: cvar.set((value)))

        ## Dummy signal call:
        project.resources.appended("key", "dummy_resource")

        assert cvar.get() == "dummy_resource"

    def test_elem_update(self):
        ''' utilizing a dummy project object, assert connection and disconnection from collection '''
        class _DummyProject():
            def __init__(self):
                self.resources = Collection(key_attr="")
        p1 = _DummyProject()
        p2 = _DummyProject()
        context = Context(project = p1)

        assert len(p1.resources.appended.subscribers) == 0
        assert len(p1.resources.renamed.subscribers) == 0

        promise = PromiseContextual("key", Promise.Type.RESOURCE, context=context)

        ## attaches to context,
        assert len(p1.resources.appended.subscribers) == 1
        assert len(p1.resources.renamed.subscribers) == 1

        context.project = p2

        ## detaches from old project, attaches to new project 
        assert len(p1.resources.appended.subscribers) == 0
        assert len(p1.resources.renamed.subscribers) == 0

        assert len(p2.resources.appended.subscribers) == 1
        assert len(p2.resources.renamed.subscribers) == 1

class Test_PromiseProperty:
    def test_construction(self):
        PromiseProperty("","",Promise.Type.RESOURCE)

    def test_extrensics(self):
        cvar = ContextVar("")
        class _Dummy():
            context : Context
            _value : Promise[Any]|Any
            value = PromiseProperty("_value","value_set",Promise.Type.RESOURCE)
            def __init__(self):
                self.context = Context()
            def value_set(self, old_value, value):
                cvar.set(value)
        d = _Dummy()

        d._value = None
        assert d.value == None

        d._value = "str"
        assert d.value == "str"

        d.value = "key"
        assert isinstance(d._value, PromiseContextual)
        assert len(d._value.replace.subscribers) == 1
        assert d._value.key == "key"

        d._value.replace("dummy_resource", *d._value._extra_args)
        assert d._value == "dummy_resource"
        assert d.value == "dummy_resource"

class Test_Properties:
    def test_construction(self):
        Properties()
        Properties({"data":"data"})
        Properties({"data":"data"}, context=Context())

    def test_overlay_basic(self):
        a = Properties({         "b":"b", "c":"c1"})
        b = Properties({"a":"a"         , "c":"c2"})
        b.set_overlay(a)
        assert b["a"] == "a"
        assert b["b"] == "b"
        assert b["c"] == "c2"

    def test_overlay_basic_signals(self):
        a = Properties({         "b":"b", "c":"c1"})
        b = Properties({"a":"a"         , "c":"c2"})

        updated = {}
        added = {}
        removed = {}
        b.updated.connect(lambda k,v0,v1: updated.__setitem__(k,(v0,v1)))
        b.added.connect(lambda k,v: added.__setitem__(k, v))
        b.removed.connect(lambda k,v: removed.__setitem__(k, v))

        ## ADDING ##
        b.set_overlay(a)
        assert len(b) == 3

        assert len(updated.keys()) == 0

        assert len(added.keys()) == 1
        assert added["b"] == "b"

        assert len(removed.keys()) == 0

        ## REMOVAL ##
        updated.clear()
        added.clear()
        removed.clear()

        b.set_overlay(None)
        assert len(b) == 2

        assert len(updated.keys()) == 0

        assert len(added.keys()) == 0

        assert len(removed.keys()) == 1
        assert removed["b"] == "b"

    def test_setitem_promise_failure(self):
        p = Properties({"ref": Promise("", Promise.Type.RESOURCE)})

        ## Tries and fails to find relevent in context, converts to a PromiseContextual
        assert isinstance(p["ref"], PromiseContextual)
        assert len(p["ref"].replace.subscribers) == 1

    def test_setitem_promise_success(self):
        ## Monkeypatch Promise object to ensure that resolve is being called, and is replacing item on property
        promise = Promise("", Promise.Type.RESOURCE)
        promise.resolve = lambda context, default: "value"

        ## "Finds" relevent in context via monkey patch, replaces.
        p = Properties({"ref":promise})
        assert p["ref"] == "value"

        ## Currently resolve only called on intial set and from signals, not on fetch!
        p.data["ref"] = promise
        assert isinstance(p["ref"], Promise)
        
    def test_localize_defered(self):
        ''' Behavior is to defer localization to object when a `localize` attribute exists '''

        class _object():
            def localize(self, context):
                return "Replacement"

        obj = _object()
        p0 = Properties({"ref":obj})
        p = Properties()
        p.set_overlay(p0)

        ## Localize is only called if object is sourced from an overlay
        assert p.get("ref", localize=True) == "Replacement"
        assert p.get("ref", localize=False) is obj

        assert p0.get("ref", localize=True) is obj
        assert p0.get("ref", localize=False) is obj




class Test_Project:
    def test_construction(self):
        Project()

class Test_File:
    def test_construction(self):
        File()

class Test_FileIO:
    def test_construction(self):
        FileIO()

class Test_Settings:
    def test_construction(self):
        Settings()

class Test_Category:
    def test_construction(self):
        Category()

class Test_Resource:
    def test_construction(self):
        Resource()

class Test_Node:
    def test_construction(self):
        Node()