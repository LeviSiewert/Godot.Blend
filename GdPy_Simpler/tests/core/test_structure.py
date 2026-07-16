import pytest

from fsspec import AbstractFileSystem

from ...core.structure import Project, File, Node, Resource, ResourceRef, FileRef
from fsspec.implementations.memory import MemoryFileSystem
from ...core.structure import FileSystemSignalProvider
from ...files import FileText

class Test_File():

    def test_construction(self):
        file = File.construct(
            "res://abc.txt",
            cached_uid="uid://abc",
            resource=None,
            properties={},
        )
        assert file.meta_properties.context.file == file

        assert file.filepath.key == "res://abc.txt"
        assert file.resource.key == "uid://abc"

# @pytest.mark.dependency(name="Test_Resource", depends=["test_signals.py::Test_Signals", "test_gdtype.py::Test_GdType"] )
class Test_Resource():
    
    def test_construction(self):
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
            },
        )

        # assert res.properties.context.resource == res
        assert res.properties.context.subresource == res

        assert res.uid.key == "uid://abc"
        assert res.file.key == "res://abc.txt"
        assert res.file.get() is None

        assert res.properties["a"] == "a"

    def test_subresource_tracking_construction(self):
        subres = Resource.construct(
            properties={
                "a":"a",
            },
        )
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a", 
            },
            subresources = [
                subres,
            ]
        )

        assert subres in res.subresources
        assert subres.id
        
        assert res.context.resource is res

        assert res.context in tuple(subres.context._iter_extends())

        assert subres.context.resource is res
        assert subres.context.subresource is subres

    
    def test_subresource_tracking_implicit(self):
        subres = Resource.construct(
            properties={
                "a":"a",
            },
        )
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
                "b": subres, 
            },
        )

        assert subres in res.subresources
        assert subres.id
    
    def test_overlay_clean(self):
        subres = Resource.construct(
            properties={
                "a":"a",
            },
        )
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
                "b": subres, 
            },
        )
        new_res = res.copy_overlay()
        assert new_res.overlay is res
        assert new_res.properties["b"].overlay is subres


    def test_overlay_dirty(self):
        ''' Matching ids and overlay is applied to existing, else create new overlay and place in existing cache. Final Tree shape should be maintained. 
        Delimited by file/abstaract references in properties, instance notation, ie anything not structural. '''
        
        origin_subres = Resource.construct(id="subres_id",)
        res = Resource.construct(
            properties={
                "b": origin_subres, 
            },
        )
        overlay_subres = Resource.construct(id="subres_id")

        new_res = res.copy_overlay(existing={overlay_subres.id.key : overlay_subres})
        assert overlay_subres.overlay is origin_subres

    def test_overlay_clone(self):
        ''' Clone should collapse all overlays into a new fully mutable instance w/out overlays, essentially an embedd. '''
        
        subres = Resource.construct(id="subres_id")
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
                "b": subres, 
            },
        )

        res_overlay = res.copy_overlay()
        new_clone = res_overlay.clone(deep=True)

        assert new_clone.overlay is None
        assert new_clone.origin() is res_overlay
        assert new_clone.properties["a"] == "a"
        assert not new_clone.properties["b"] is subres


    def test_clone(self):
        ''' Clone should collapse all overlays into a new fully mutable instance w/out overlays, essentially an embedd. '''
        
        subres = Resource.construct(id="subres_id")
        res = Resource.construct(
            uid="uid://abc",
            file="res://abc.txt",
            properties={
                "a":"a",
                "b": subres, 
            },
        )

        new_clone = res.clone(deep=True)

        assert not (new_clone is res)
        assert new_clone.overlay is None
        assert new_clone.origin() is res
        assert new_clone.properties["a"] == "a"
        assert not (new_clone.properties["b"] is subres)
        

    def test_construction_overlay_direct(self):
        overlay_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":"c",
            },
            overlay=overlay_res,
        )

        assert res.properties.overlay is overlay_res.properties

        assert overlay_res.properties["a"] == "a"
        assert overlay_res.properties["b"] == "b"

        assert res.properties["a"] == "a"
        assert res.properties["b"] == "c"
        assert res.properties["c"] == "c"


    def test_construction_instance_direct(self):
        ''' Test direct instance construction'''

        inst_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        inst_file = File.construct(
            "res://inst_src.txt",
            resource=inst_res,
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":"c",
            },
            instance=inst_file,
            _instance_direct=True,
        )

        assert res.overlay == inst_res

        assert inst_res.properties["a"] == "a"
        assert inst_res.properties["b"] == "b"

        assert res.properties["a"] == "a"
        assert res.properties["b"] == "c"
        assert res.properties["c"] == "c"

    def test_construction_instance_delayed(self,):
        ''' Construct resources, attach to project and fullfill at that time '''
        inst_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        inst_file = File.construct(
            "res://inst_src.txt",
            resource=inst_res,
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":"c",
            },
            instance=inst_file,
        )
        assert res.instance.key == inst_file.filepath.key
        assert res.instance.get() == None

        prj = Project.construct(
            file_system = None,
            file_types = [],
            files = [
                inst_file
            ],
            resources = [
                inst_res,
                res,
            ]

        )

        assert res.overlay == inst_res

        assert inst_res.properties["a"] == "a"
        assert inst_res.properties["b"] == "b"

        assert res.properties["a"] == "a"
        assert res.properties["b"] == "c"
        assert res.properties["c"] == "c"


#     def test_instance(self):
#         raise NotImplementedError()

#     def test_instance_editability(self):
#         raise NotImplementedError()

#     def test_overlay_editability(self):
#         raise NotImplementedError()

#     def test_overlay_thin_recognition(self):
#         raise NotImplementedError()
    
#     def test_gdtype_defaults(self):
#         raise NotImplementedError()

#     def test_gdtype_verification(self):
#         raise NotImplementedError()



class Test_Node():
    def test_construction_basic():
        Node.construct()
    
    def test_construction_tree():
        subres = Resource.construct()
        node_e = Node.construct(name="E",
            properties={
                "a":"a",
                "b":subres,
            }
        )
        node_d = Node.construct(name="D", 
            children=[
                node_e,
            ],
        )
        node_c = Node.construct(name="C")
        node_b = Node.construct(name="B")
        node_a = Node.construct(name="A",
            uid="uid:abc",
            children = [
                node_b,
                node_c,
                node_d,
            ],
        )
        assert len(node_a.children) == 3
        assert len(node_a.nodes) == 4
        assert len(node_a.subresources) == 1
        assert node_a.subresources[0] is subres

    def test_tree_nodepath(self):
        node_e = Node.construct(name="E")
        node_d = Node.construct(name="D", 
            children=[
                node_e,
            ],
        )
        node_c = Node.construct(name="C")
        node_b = Node.construct(name="B")
        node_a = Node.construct(name="A",
            uid="uid:abc",
            children = [
                node_b,
                node_c,
                node_d,
            ],
            properties={
                "c":"c"
            },
        )

        assert node_e["."] is node_e
        assert node_b[".."] is node_a
        assert node_d["E"] is node_e
        assert node_a["D/E"] is node_e
        assert node_e["../.."] is node_a
        
        assert node_e[".:a"] is "a"
        assert node_e["../..:c"] is "c"
        assert node_e[":owner"] is node_a

        assert node_e["/"] is None

    def test_tree_instances():
        ''' A(B,C) -> A(B,~C,+D)
        Where + means new
        where ~ means changed
        '''
        
        node_c1 = Node.construct(name="C")
        node_b1 = Node.construct(name="B")
        node_a1 = Node.construct(name="A",
            uid="uid:abc",
            children = [
                node_b1,
                node_c1,
            ],
            properties={
                "c":"c"
            },
        )

        node_d2 = Node.construct(name="D")
        node_c2 = Node.construct(name="C")
        # node_b2 = Node.construct(name="B")
        node_a2 = Node.construct(name="A2",
            instance = node_a1,
            children=[
                # node_b2 # Inherit !
                node_c2,  # Change !
                node_d2,  # New !
            ]
        )
        assert len(node_a2.children) == 2
        node_a2.construct_instance()
        assert len(node_a2.children) == 3
        assert node_c2.overlay is node_c1
        assert node_a2["B"].overlay is node_b1
        assert node_d2.overlay is None

# @pytest.mark.dependency(name="Test_Project", depends=["test_signals.py::Test_Signals", "test_context.py::Test_Context", "test_collection.py::Test_Collection", "Test_Resource", "Test_File"] )
class Test_Project():

    def test_construction(self):
        prj = Project.construct()

    def test_construction_mem_fs(self):
        prj = Project.construct(
            file_system=MemoryFileSystem(),
            signals=FileSystemSignalProvider(),
        )

    def test_construction_res_only(self):
        inst_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":"b"
            },
        )
        inst_file = File.construct(
            "res://inst_src.txt",
            resource=inst_res,
        )

        subres = Resource.construct(
            id="subres_id"
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":subres,
            },
            instance=inst_file,
        )
        res_file = File.construct(
            "res://abc.txt",
            resource=res,
        )

        prj = Project.construct(
            files = [
                inst_file,
                res_file,
            ], 
            resources=[
                inst_res,
                subres,     ## Subresources should be filtered out, as they do *not* have a UID.
                res,
            ],
        )

        assert len(prj.resources) == 2
        assert inst_res in prj.resources
        assert res in prj.resources
        
        assert res.file.get() is res_file
        assert inst_res.file.get() is inst_file
    
    def test_construction_search(self):
        fs = MemoryFileSystem()
        fs.write_text("abc.txt", "abc_contents")
        fs.write_text("subfolder/xyz.txt", "xyz_contents")
        
        prj = Project.construct(file_system=fs, file_types=[FileText], search=True)

        assert len(prj.files) == 2
        assert prj.files["abc.txt"]
        assert prj.files["subfolder/xyz.txt"]

    def test_construction_search_load(self):
        fs = MemoryFileSystem()
        fs.write_text("abc.txt", "abc_contents")
        fs.write_text("subfolder/xyz.txt", "xyz_contents")
        
        prj = Project.construct(file_system=fs, file_types=[FileText], search=True)

        file_abc = prj.files["abc.txt"]
        file_abc.load()
        assert file_abc.data == "abc_contents"
        
        file_xyz = prj.files["subfolder/xyz.txt"]
        file_xyz.load()
        assert file_xyz.data == "xyz_contents"

    def test_construction_instance_construction(self):
        ''' Desired structure is `res[b] is res[c] is subres` and  `subres.overlay is inst_subres` 
        Done through ref match + loading
        - inst_file
            - res.props:
                - subres
        - res_file
            - res.props:
                - subres
        '''

        inst_subres = Resource.construct(
            id="subres_id"
        )
        inst_res = Resource.construct(
            uid="uid://inst_src",
            properties={
                "a":"a",
                "b":inst_subres,
            },
        )
        inst_file = File.construct(
            "res://inst_src.txt",
            resource=inst_res,
        )

        subres = Resource.construct(
            id="subres_id"
        )
        res = Resource.construct(
            uid="uid://abc",
            properties={
                "b":"c",
                "c":subres,
            },
            instance="res://inst_src.txt", ## constructs defered reference, should be found
        )
        res_file = File.construct(
            "res://abc.txt",
            resource=res,
        )

        prj = Project.construct(
            files = [
                inst_file,
                res_file,
            ], 
            resources=[
                inst_res,
                subres,     ## Subresources should be filtered out, as they do *not* have a UID.
                res,
            ],
        )
        
        res.construct_instance()
        assert res.are_instances_constructed()
        assert res.overlay is inst_res
        assert subres.overlay is inst_subres
        assert (res["b"] is res["c"]) and res["b"] is subres 


#     def test_construction_file_resource_refs(self):
#         raise NotImplementedError()

#     def test_fs_root(self):
#         raise NotImplementedError()

#     def test_fs_search(self):
#         raise NotImplementedError()

#     def test_fs_search(self):
#         raise NotImplementedError()

#     def test_fs_search_match(self):
#         raise NotImplementedError()

#     def test_fs_events(self):
#         raise NotImplementedError()

#     def test_fs_dif_update(self):
#         raise NotImplementedError()
