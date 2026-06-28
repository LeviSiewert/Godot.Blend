from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, CollectionProperty
from .resource import _BlResource, BlTres, BlTscn, BlSettings

class _BlFile(PropertyGroup):
    filepath : StringProperty() #type:ignore
    data : _BlResource

class BlFileTscn(_BlFile):    
    data : PointerProperty(type=BlTscn) #type:ignore    

class BlFileTres(_BlFile):
    data : PointerProperty(type=BlTres) #type:ignore    

class BlFileSettings(_BlFile):
    data : PointerProperty(type=BlSettings) #type:ignore

class BlFileCollection(PropertyGroup):
    ''' Utilized for "thin" imported files, ie ones that have no 3d structure '''
    tres_files : CollectionProperty(type = BlFileTres) #type:ignore
    import_files : CollectionProperty(type = BlFileSettings) #type:ignore
    tscn_files : CollectionProperty(type = BlTscn) #type:ignore

    project_file : PointerProperty(type = BlFileSettings) #type:ignore


_all=(
    BlFileTscn,
    BlFileTres,
    BlFileSettings,
    BlFileCollection,
)