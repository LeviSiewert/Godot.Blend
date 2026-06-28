import bpy 

# class _BlReference(bpy.types.PropertyGroup):
#     pass

class _BlSubResource(bpy.types.PropertyGroup): 
    pass

class _BlSubResourceCollection(bpy.types.PropertyGroup):
    data : bpy.types.PropertyCollection

class _BlResource(bpy.types.PropertyGroup):
    ''' Place on all objects that require a unique disc representation (Tscn, Gltf, ~Textures) 
    required standard is object.gd
    in cases where an object represents multiple files, use .gd.{filetype}
    '''
    is_enabled : bpy.props.BoolProperty() #type:ignore
    filepath : bpy.props.StringProperty() #type:ignore
    uid : bpy.props.StringProperty() #type:ignore

class _BlResourceSettings(bpy.types.PropertyGroup):
    ''' Settings container, utilize for all _BlResources subtypes that have import/export settings that should be stored on the local object (Tscn, Gltf, Textures, Ect.) 
    required standard is .gd_settings
    in cases where an object represents multiple files, use .gd_settings.{filetype}
    '''

class _BlResourceCollection(bpy.types.PropertyGroup):
    ''' Utilize when clumping specific types of _BlResources '''
    data : bpy.types.PropertyCollection

class _BlProjectData(bpy.types.PropertyGroup):
    ''' Project data accessor, utilize to point to other shit'''
    pass

class _BlProject(bpy.types.PropertyGroup):
    ''' Preferences project representation '''
    name : bpy.props.StringProperty(name="Name") #type:ignore
    filepath : bpy.props.StringProperty(name="project_dir", subtype="DIR_PATH") #type:ignore
