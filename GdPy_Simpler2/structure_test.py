from .structure import Project, Resource, File

def make_project():
    return Project()

class Test_Properties_ContextualAttachment():
    ''' test contextual-sticky attachment '''

    def test_resource_ordered():
        ''' r1.context is set, fetch immediatly '''
        project = make_project()
        r1 = Resource(id="r1", uid="r1")
        r2 = Resource(id="r2", uid="r2")

        project.resources.append(r1)
        r1.properties["reference"] = r2

        assert r2 in project.resources  
        assert project.resources[r2] == "r2"
        assert r2.context._extends is project.context

    def test_resource_delayed():
        ''' r1.context is not set, fetch via signal '''
        project = make_project()
        r1 = Resource(id="r1", uid="r1")
        r2 = Resource(id="r2", uid="r2")

        r1.properties["reference"] = r2  
        project.resources.append(r1)

        assert r2 in project.resources  
        assert project.resources[r2] == "r2"
        assert r2.context._extends is project.context

    def test_subresource_ordered():
        ''' r1.context is set, set immediatly '''
        r1 = Resource(id="r1", uid="r1")
        sr1 = Resource(id="sr1")
        sr2 = Resource(id="sr2")

        r1.properties["reference"] = sr1
        assert sr1 in r1.sub_resources
        assert sr1.context._extends is r1.context
        assert r1[sr1] == "sr1"

        sr1.properties["reference"] = sr2
        assert sr2 in r1.sub_resources
        assert sr2.context._extends is r1.context
        assert r1[sr2] == "sr2"

    def test_subresource_inverse():
        ''' r1.context is set, set immediatly '''
        r1 = Resource(id="r1", uid="r1")
        sr1 = Resource(id="sr1")
        sr2 = Resource(id="sr2")

        sr1.properties["reference"] = sr2

        assert not sr1 in r1.sub_resources
        assert not sr1.context._extends is r1.context
        assert not r1[sr2] == "sr2"

        r1.properties["reference"] = sr1

        assert sr1 in r1.sub_resources
        assert sr1.context._extends is r1.context
        assert r1[sr1] == "sr1"

        assert sr2 in r1.sub_resources
        assert sr2.context._extends is r1.context
        assert r1[sr2] == "sr2"

    def test_resource_conversion():
        raise NotImplementedError()