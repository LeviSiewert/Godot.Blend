from .structure import Project, Resource, File, Properties
from contextvars import ContextVar

def make_project():
    return Project()

class Test_Properties_Signals():
    def test_add(self):
        properties = Properties(None)
        c = ContextVar("")
        properties.local_value_added.connect(lambda k,v: c.set((k,v)))
        properties["a"] = "a"
        assert c.get() == ("a","a")

    def test_rem(self):
        properties = Properties(None)
        c = ContextVar("")
        properties.local_value_removed.connect(lambda k,v: c.set((k,v)))
        properties["a"] = "a"
        del properties["a"]
        assert c.get() == ("a","a")

    def test_update(self):
        properties = Properties(None)
        c = ContextVar("")
        properties.local_value_updated.connect(lambda k,v: c.set((k,v)))
        properties["a"] = "a"
        properties["a"] = "b"
        assert c.get() == ("a","b")

class Test_Properties_ContextualAttachment():
    ''' test contextual-sticky attachment '''

    def test_resource_ordered(self):
        ''' r1.context is set, fetch immediatly '''
        project = make_project()
        r1 = Resource(id="r1", uid="r1")
        r2 = Resource(id="r2", uid="r2")

        project.resources.append(r1)
        r1.properties["reference"] = r2

        assert r2 in project.resources  
        assert project.resources["r2"]._proxy_obj is r2 
        assert r2.context._extends is project.context

    def test_resource_delayed(self):
        ''' r1.context is not set, fetch via signal '''
        project = make_project()
        r1 = Resource(id="r1", uid="r1")
        r2 = Resource(id="r2", uid="r2")

        r1.properties["reference"] = r2  
        project.resources.append(r1)

        assert r2 in project.resources  
        assert project.resources["r2"]._proxy_obj is r2 
        assert r2.context._extends is project.context

    def test_subresource_ordered(self):
        ''' r1.context is set, set immediatly '''
        r1 = Resource(id="r1", uid="r1")
        sr1 = Resource(id="sr1")
        sr2 = Resource(id="sr2")

        r1.properties["reference"] = sr1
        assert sr1 in r1.sub_resources
        assert sr1.context._extends is r1.context
        assert r1.sub_resources["sr1"]._proxy_obj is sr1

        sr1.properties["reference"] = sr2
        assert sr2 in r1.sub_resources
        assert sr2.context._extends is r1.context
        assert r1.sub_resources["sr2"]._proxy_obj is sr2 

    def test_subresource_inverse(self):
        ''' r1.context is not set yet, defered via signals '''
        r1 = Resource(id="r1", uid="r1")
        sr1 = Resource(id="sr1")
        sr2 = Resource(id="sr2")

        sr1.properties["reference"] = sr2

        assert not sr1 in r1.sub_resources
        assert not sr1.context._extends is r1.context
        assert not "sr2" in r1.sub_resources

        r1.properties["reference"] = sr1

        assert sr1 in r1.sub_resources
        assert sr1.context._extends is r1.context
        assert r1.sub_resources["sr1"]._proxy_obj is sr1

        assert sr2 in r1.sub_resources
        assert sr2.context._extends is r1.context
        assert r1.sub_resources["sr2"]._proxy_obj is sr2

    # def test_resource_conversion(self):
    #     raise NotImplementedError()\
from .structure import Properties, Promise, _StructuralPromise
from .core import _C_Proxy

class Test_Properties_Promises():
    def test_promise_base(self):

        props = Properties()
        promise = Promise()
        props["t"] = promise

        assert len(promise._promise_replace.subscribers) == 1
        
        promise._promise_replace("value")

        assert props["t"] == "value"
        assert len(promise._promise_replace.subscribers) == 0

    def test_promise_contextual_proxy_fullfilled(self):
        project = make_project()
        r1 = Resource(uid="r1")
        r2 = Resource(uid="r2")
        project.resources.append(r1)
        project.resources.append(r2)

        c = ContextVar("")
        promise = _StructuralPromise("project","resources","r2", "RID(r2)")
        promise._promise_replace.connect(lambda x: c.set(x))
        r1.properties["reference"] = promise

        assert c.get()._proxy_obj is r2
        assert isinstance(r1.properties["reference"], Resource)
        assert r1.properties["reference"]._proxy_obj is r2

    def test_promise_contextual_proxy_defered(self):
        project = make_project()
        r1 = Resource(uid="r1")
        r2 = Resource(uid="r2")
        project.resources.append(r1)

        c = ContextVar("")
        promise = _StructuralPromise("project","resources","r2", "RID(r2)")
        promise._promise_replace.connect(lambda x: c.set(x))
        r1.properties["reference"] = promise

        project.resources.append(r2)

        assert c.get()._proxy_obj is r2
        assert isinstance(r1.properties["reference"], Resource)
        assert r1.properties["reference"]._proxy_obj is r2

class Test_Properties_Overlay():
    def test_basic(self):
        c = ContextVar("")
        p0 = Properties(None, {"a":"A", "b":"B", "c":"C"})
        p1 = Properties(None, {"a":"A1"})
        p1.overlay_updated.connect(lambda overlay: c.set(overlay))

        assert p0["a"] == "A"
        assert p0["b"] == "B"
        assert p0["c"] == "C"

        assert p1["a"] == "A1"
        assert not ("b" in p1)
        assert not ("c" in p1)

        p1.set_overlay(p0)
        assert c.get() is p0

        assert p1["a"] == "A1"
        assert p1["b"] == "B"
        assert p1["c"] == "C"

        p1.set_overlay(None)
        assert c.get() is None
        
    def test_signals(self):
        c = ContextVar("")
        added = {}
        removed = {}
        updated = {}

        p = Properties()
        p0 = Properties(None, {"a":"A", "b":"B", "c":"C"}, overlay=p)
        p1 = Properties(None, {"a":"A1"})

        p1.overlay_updated.connect(lambda overlay: c.set(overlay))

        p1.overlay_value_added.connect(lambda k,v: added.__setitem__(k,v))
        p1.overlay_value_removed.connect(lambda k,v: removed.__setitem__(k,v))
        p1.overlay_value_updated.connect(lambda k,v: updated.__setitem__(k,v))
            
        p1.set_overlay(p0, supress_dif = False)

        assert c.get() is p0

        assert added["b"] == "B" 
        assert added["c"] == "C" 
        assert not ("a" in added.keys()) ### Supressed update since it's 

        del p0["b"]
        assert removed["b"] == "B"

        p0["c"] = "C1"
        assert updated["c"] == "C1"

        ## Forwarded signals:
        p["d"] = "D"
        assert added["d"] == "D"

        p["d"] = "D1"
        assert updated["d"] == "D1"

        del p["d"]
        assert removed["d"] == "D1"

# class Test_Properties_Localize():
#     ''' Localization is returning the (scope[id] equivilent) or a promise to the (scope[id] equivilent), within the context given '''

#     def test_limited(self):
#         r0 = Resource(uid="r0")
#         sr0 = Resource(id="sr")
#         r0.properties["a"] = sr0

#         r1 = Resource(uid="r1")
#         sr1 = Resource(id="sr")
#         # r1.properties["a"] = sr1  

#         r1.properties.set_overlay(r0.properties)

#         ## Expectation; returns Proxy(Promise-like) of r1.context.resource.sub_resources["sr"]
#         assert isinstance(r1.properties["a"], _C_Proxy)
#         assert not isinstance(r1.properties["a"], Resource)
#         assert r1.properties["a"]._proxy_obj is None

#         ## Proxy is fullfilled via appending
#         r1.sub_resources.append(sr1)

#         assert isinstance(r1["a"], Resource)
#         assert r1.properties["a"]._proxy_obj is sr1

#         ## Second pass, add to r0.properties and fetch local again
#         r0.properties["b"] = sr0
#         assert r1.properties["b"]._proxy_obj is sr1

# from .core import ViewStruct

# class Test_Viewstructs():
#     ''' Viewstructs are a way to allow object localization && prevent incorrect context editing '''
#     def test(self):
#         raise NotImplementedError() 

# class Test_Properties_ViewStruct():
#     def test_limited(self):
#         p0 = Properties(None, {"a":{"b":[]}, })
#         p1 = Properties(overlay=p0)

#         r = p1["a"]
#         assert isinstance(r, ViewStruct)
#         assert r._src is p0["a"]
#         assert isinstance(r["b"], ViewStruct)
#         assert r["b"]._src is p0["a"]["b"]

#     def test_promise_c_unset(self):
#         ''' unset context is an odd edge case, but it's unknown how to do this otherwise ... 
#         '''
#         r0 = Resource(id="")
#         p0 = Properties(None, {"a":, })
#         p1 = Properties(overlay=p0)

#         res = p1["a"]["b"]
#         assert isinstance(res, j)
#             # Defered promise w/ ref to original (as context is unset)

#     def test_promise(self):
#         r0 = Resource(uid="r0")
#         sr0 = Resource(id="sr")
#         r0.properties["a"] = {"b":sr0}

#         r1 = Resource(uid="r1")
#         sr1 = Resource(id="sr")
#         # r1.properties["a"] = sr1  

#         r1.properties.set_overlay(r0.properties)

#         assert isinstance(r1["a"], ViewStruct)
#         assert isinstance(r1["a"]["b"], _C_Proxy)
#         assert r1["a"]["b"]._proxy_obj is None

#         r1.sub_resources.append(sr1)

#         assert isinstance(r1["a"]["b"], )
#         assert isinstance(r1["a"]["b"], _C_Proxy)
#         assert r1["a"]["b"]._proxy_obj is sr1

# class Test_Properties_ExtResource():
#     ''' Desired behavior: 
#     - all resources that are accessed through properties must be routed through a local ext_resource 
#     - these ext_resources are not included in the overlay system
#     - Unfullfilled promises from another collection must transfer/merge (uid, path)
#     '''

#     def test_assign_wrap_no_context(self):
#         pass

#     def test_assign_wrap(self):
#         ''' test assign a resource that is not a subresource ''' 
#         raise NotImplementedError()

    # def test_declare_assign_wrap(self):
    #     ''' test assign a resource that is not a subresource '''
    #     raise NotImplementedError()
    
    # def test_assign_convert(self):
    #     ''' test assign a resource that is a subresource, then convert '''
    #     raise NotImplementedError()


    # def test_assign_foreign_filled(self):
    #     ''' test assign a ext_resource that is from another resource, unwrap and localize. Return '''
    #     raise NotImplementedError()

    # def test_assign_foreign_empty(self):
    #     ''' test assign a ext_resource that is from another resource and isnt fullfilled. Return new _C_Proxy '''
    #     raise NotImplementedError()


    # def test_embedd_resources_one(self):
    #     ''' Asign resource, then localize 1 instance (not all) '''
    #     raise NotImplementedError()

    # def test_embedd_resources_all(self):
    #     ''' Asign resource, then localize all refs '''
    #     raise NotImplementedError()


    # def test_embedd_nodes_one(self):
    #     ''' Asign resource, then localize 1 instance '''
    #     raise NotImplementedError()

    # def test_embedd_nodes_all(self):
    #     ''' Asign resource, then localize all instances '''
    #     raise NotImplementedError()

