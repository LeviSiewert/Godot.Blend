from .structure import Project, Resource, File
from contextvars import ContextVar

def make_project():
    return Project()

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
