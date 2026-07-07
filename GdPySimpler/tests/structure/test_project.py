from ...core.structure import Project, FileLocal, FileForeign
import fs
class Test_Project():
    def test_construction(self,):
        prj = Project.construct(
            file_system = fs("mem://"),
            file_types = (FileLocal, FileScript, FileForeign),
            resources = [],
            _inload_files = True,
        )
        
        raise NotImplementedError() 
    
    def test_references(self,):
        raise NotImplementedError() 
    
    