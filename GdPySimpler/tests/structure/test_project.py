from ...core.structure import (
    FileScript,
    FileUid,
    Project,
)
from ...core.subresources import (
    ResourceTres,
    SubResource,
)
from ...file_io import (
    FileIoTxt,
)

from fs.memoryfs import MemoryFS

class Test_Project_Fs():
    def test_construction_defered_mem(self,):
        file_system = MemoryFS()

        file_script = FileScript.construct(
            "test.gd",
            _defer_create=True,
            _defer_create_contents="",
        )

        file_script_uid = FileUid.construct(
            "test.gd.uid",
            _defer_create=True,
            _defer_create_contents="uid://abc",
        )

        prj = Project.construct(
            # _discover_files = False,
            file_system = file_system,
            file_types = (FileUid,),
            file_io = (FileIoTxt,),
            files = [
                file_script,
                file_script_uid,
            ],
            resources = [],
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
        
        ## File IO Attachment 
        assert isinstance(file_script.get_io_handler(), FileIoTxt)
        assert isinstance(file_script_uid.get_io_handler(), FileIoTxt)

        ## assert defered file creation
        assert file_system.getfile("mem://test.gd")
        assert file_system.getfile("mem://test.gd.uid")
        assert file_system.readtext("mem://test.gd.uid") == "uid://abc"


    def test_construction_discovered(self,):
        file_system = MemoryFS()

        file_system.writetext(
            "test.gd",
            "",
        )
        file_system.writetext(
            "test.gd.uid",
            "uid://abc",
        )

        prj = Project.construct(
            file_system = file_system,
            file_types = (FileUid,),
            file_io = (FileIoTxt,),
        )

        assert prj.files["mem://test.gd"]
        file_script = prj.files["mem://test.gd"]
        assert isinstance(file_script, FileScript) 
        
        assert prj.files["mem://test.gd.uid"]
        file_script_uid = prj.files["mem://test.gd.uid"]
        assert isinstance(file_script, FileUid)

        assert file_script.uid_file is file_script_uid

        assert prj.files["uid://abc"] is file_script

        ## File IO Attachment 
        assert isinstance(file_script.get_io_handler(), FileIoTxt)
        assert isinstance(file_script_uid.get_io_handler(), FileIoTxt)