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
        Project(fs=None)

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

    def test_normalization(self):
        ''' fix ownership of structural elements, clean subresources, prep for tree construction '''

        sr = Resource()
        r = Resource(uid="uid", properties = {"ref":sr})

        assert not (sr in r.sub_resources)
        assert (r in sr.users)

        r.normalize(duplicate=False)

        assert (sr in r.sub_resources)
        assert (r in sr.users)

class Test_Node:
    def test_construction(self):
        Node()

    def test_normalization_simple(self):
        ''' fix ownership of structural elements, clean subresources, prep for tree construction 
        Normalization is not required for write to disc, as context flags should swap rendering of objects.
        '''

        r = Node(uid="uid")
        sr = Node(name = "ChildNode")

        r0 = Node(name="root", uid="uid", children=[sr], properties={"val":r, "ref":sr})
        r1 = Node(name="root", uid="uid", children=[sr], properties={"val":r, "ref":sr})

        assert (r0 in sr.users)
        assert (r1 in sr.users)
        assert not (sr.context.resource is r0) ## NON-NORMALIZED due to multiple references
        assert (sr.context.resource is r1)

        r0.normalize(fork=True, refs_to_paths=True)
        r1.normalize(fork=True, refs_to_paths=True)

        sr0 = r0.properties["ref"]
        sr1 = r1.properties["ref"]

        assert isinstance(sr0, Node)
        assert isinstance(sr1, Node)
        assert not (sr0 is sr1)
        assert sr0 == sr1

        assert r0.properties["val"] is r ## Rendered to text as "packed_scene", not split
        assert r1.properties["val"] is r

        assert r0.properties["ref"] == NodePath("./ChildNode") ## nromalize flag refs_to_paths=True
        assert r1.properties["ref"] == NodePath("./ChildNode")

    def test_normalization_childtooverlay():
        ''' When normalizing, direct instances are turned to overlayed nodes.
        
        '''

        r = Node(uid="uid", name = "Child")

        r0 = Node(name="root", uid="uid", children=[r], properties={"ref":r})
        r1 = Node(name="root", uid="uid", children=[r], properties={"ref":r})

        r0.normalize(scene_children_as_instances=True, scene_children_refs_to_paths=False)
        r1.normalize(scene_children_as_instances=True, scene_children_refs_to_paths=True)

        sr0 : Node = r0.children["Child"]  
        sr1 : Node = r1.children["Child"]

        assert not (sr0 is r)
        assert not (sr1 is r)
        
        assert sr0.instance is r
        assert sr1.instance is r 

        assert sr0 == sr1

        assert sr0 == r
        assert sr1 == r

        assert r0.properties["ref"] is r
        assert r0.properties["ref"] == NodePath("./Child")

    def test_instance_construction_simple_noneditable(self):
        sr0_a = Node(name="a") 
        sr0_b = Node(name="b") ## Overlayed or shifted
        # sr0_c = Node(name="c") ## Introduced
        r0 = Node(uid="uid", name="Scene_0", children=[sr0_a, sr0_b])

        # sr1_a = Node(name="a") 
        sr1_b = Node(name="b") ## if instance isnt editable, shifted 
        sr1_c = Node(name="c") ## Introduced
        r1 = Node(uid="uid", name="Scene_0", children=[sr1_b, sr1_c], instance=r0, instance_editable=False)

        r1.construct_and_load(shift_matchiing_non_editable=True)

        assert r1.overlay is r0

        ## ## if instance isnt editable, names are shifted
        assert len(r1.children) == 4
        assert sr1_b.overaly is None
        assert not (sr1_b.name == "b")

        ## Non-editable, so children are not overlayed
        assert r1.children["a"] is sr0_a
        assert r1.children["b"] is sr0_b
        assert r1.children["c"] is sr1_c
    
    def test_instance_construction_simple_editable(self):
        sr0_a = Node(name="a") 
        sr0_b = Node(name="b") ## Overlayed or shifted
        # sr0_c = Node(name="c") ## Introduced
        r0 = Node(uid="uid", name="Scene_0", children=[sr0_a, sr0_b])

        # sr1_a = Node(name="a") 
        sr1_b = Node(name="b") ## if instance isnt editable, shifted 
        sr1_c = Node(name="c") ## Introduced
        r1 = Node(uid="uid", name="Scene_0", children=[sr1_b, sr1_c], instance=r0, instance_editable=True)

        r1.construct_and_load(shift_matchiing_non_editable=True)

        assert r1.overlay is r0

        ## if instance isnt editable, names are shifted
        assert len(r1.children) == 3
        assert sr1_b.overaly is sr0_b 
        assert (sr1_b.name == "b")

        ## Instance editable, so all children are overlayed
        assert r1.children["a"].overlay is sr0_a
        assert r1.children["b"].overlay is sr0_b
        assert r1.children["c"] is sr1_c
    

    def test_instance_construction_nested(self):
        sr0_a = Node(name="a") ## Appended
        sr0_b = Node(name="b") ## Overlayed
        r0 = Node(uid="uid", name="Scene_0", children = [sr0_a, sr0_b])

        sr1_b = Node(name="b") ## Overlayed
        sr1_c = Node(name="c") ## Introduced

        sr1_0 = Node(instance=r0, instance_editable=False)
        sr1_1 = Node(instance=r0, instance_editable=True, children = [sr1_b, sr1_c],)
        r1 = Node(uid="uid", children=[sr1_0,sr1_1])

        r1.construct_and_load()

        assert len(sr1_0.children) == 2
        assert len(sr1_1.children) == 3

        ## Considering; do I overlay non-editable children or not?
        ## Matched:
        assert sr1_0.instance is r0
        assert sr1_0.overaly is r0

        assert sr1_0.children["a"] is sr0_a
        assert sr1_0.children["b"] is sr0_b

        ## Overlay construction:
        ## Matched:
        assert sr1_1.instance is r0
        assert sr1_1.overaly is r0

        assert sr1_1.children["a"].overaly is sr0_a
        assert sr1_1.children["b"].overaly is sr0_b
        assert sr1_1.children["c"].overaly is None