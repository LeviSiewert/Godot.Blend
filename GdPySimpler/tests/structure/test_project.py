from ...core.structure import (
    Project,
)

from ...core.subresources import (
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
        assert file_script.uid_file is file_script_uid
        assert file_script.get_uid() == "uid://abc"

        ## Collection key assertions
        assert prj.files["uid://abc"] is file_script
        assert prj.files["mem://test.gd"] is file_script
        assert prj.files["mem://test.gd.uid"] is file_script_uid
        
        ## assert defered file creation
        assert file_system.getfile("mem://test.gd")
        assert file_system.getfile("mem://test.gd.uid")
        assert file_system.readtext("mem://test.gd.uid") == "uid://abc"

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

        assert file_script.uid_file is file_script_uid

        assert prj.files["uid://abc"] is file_script