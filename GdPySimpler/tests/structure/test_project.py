from ...core.structure import (
    Project,
)

from ...core.resources import (
    ResourceTres,
)

from ...file_types import (
    FileTxt, 
    FileScript,
    _all as file_types
)

# from fs.memoryfs import MemoryFS
from fsspec.implementations.memory import MemoryFileSystem

class Test_Project_Fs():

    def test_defered_write_import():
        file_system = MemoryFileSystem()
        
        file_script_uid = FileTxt.construct(
            "mem://test.gd.uid",
            _defered_write=True,
            _defered_write_data="uid://abc",
            _defered_import=True,
        )

        prj = Project.construct(
            files = [
                file_script_uid,
            ]
        )


        ## Test collection attachment:
        assert prj["mem://test.gd.uid"] is file_script_uid

        ## Test _defered_write:
        assert file_system.read_text("mem://test.gd.uid") == "uid://abc"
        
        ## Test _defered_import:
        assert file_script_uid.data == "uid://abc"


    def test_defered_export():
        pass

    def test_defered_write_uid_discovery():
        pass

    def test_discovered_relations(self,):
        file_system = MemoryFileSystem()

        file_script = FileScript.construct(
            "mem://test.gd",
        )
        ## Test that this discovers file_script_uid 

        file_script_uid = FileTxt.construct(
            "mem://test.gd.uid",
            data="uid://abc",
        )
        ## Test that this is discovered by file_script 

        res_script = ResourceTres.construct(
            uid="uid://abc"
        )
        ## Test that res_script is asc with file_script 

        prj = Project.construct(
            discover = False,
            file_system = None,
            files = [
                file_script,
                file_script_uid,
            ],
            resources = [
                res_script,
            ],
        )

        assert file_script.uid_file.get() is file_script_uid
        assert file_script.get_uid() == "uid://abc"
        ## On update of uid_file: data.store_key(get_uid())

        assert file_script.data.cached_addr == "uid://abc"
        assert file_script.data.get() is res_script


    def test_construction_defered_mem(self,):
        file_system = MemoryFileSystem()

        file_script = FileScript.construct(
            "mem://test.gd",
            _defer_create=True,
            _defer_create_contents="",
        )

        file_script_uid = FileTxt.construct(
            "mem://test.gd.uid",
            _defer_create=True,
            _defer_create_contents="uid://abc",
        )

        res_script = ResourceTres.construct(
            uid="uid://abc"
        )

        prj = Project.construct(
            file_system = file_system,
            file_types = (FileTxt, FileTxt),
            files = [
                file_script,
                file_script_uid,
            ],
            resources = [
                res_script,
            ],
        )

        ## Collection exists assertions
        assert file_script in prj.files
        assert file_script_uid in prj.files
        
        ## Context assertions
        assert file_script.context.project is prj
        assert file_script_uid.context.project is prj
        
        ## Structural assertions
        assert file_script.uid_file.get() is file_script_uid
        assert file_script.get_uid() == "uid://abc"

        ## Collection key assertions
        assert prj.files.get_cached_uid("uid://abc") is file_script
        assert prj.files["mem://test.gd"] is file_script
        assert prj.files["mem://test.gd.uid"] is file_script_uid
        
        ## assert defered file creation
        assert file_system.read_text("mem://test.gd")
        assert file_system.read_text("mem://test.gd.uid") == "uid://abc"

        ## assert resource attachment:
        assert file_script.data.get() is res_script


    def test_construction_discovered(self,):
        file_system = MemoryFileSystem()

        file_system.write_text(
            "test.gd",
            "",
        )
        file_system.write_text(
            "test.gd.uid",
            "uid://abc",
        )

        prj = Project.construct(
            file_system = file_system,
            file_types = (FileTxt, FileScript),
        )

        assert prj.files["mem://test.gd"]
        file_script = prj.files["mem://test.gd"]
        assert isinstance(file_script, FileScript) 
        
        assert prj.files["mem://test.gd.uid"]
        file_script_uid = prj.files["mem://test.gd.uid"]
        assert isinstance(file_script, FileTxt)

        assert file_script.uid_file.get() is file_script_uid

        assert prj.files.get_cached_uid("uid://abc") is file_script