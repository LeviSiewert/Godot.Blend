import bpy 

class _BlReference(bpy.types.PropertyGroup):
    pass

class _BlSubResource(bpy.types.PropertyGroup):
    pass

class _BlSubResourceCollection(bpy.types.PropertyGroup):
    items : bpy.types.PropertyCollection

class _BlResource(bpy.types.PropertyGroup):
    filepath : bpy.props.StringProperty() #type:ignore
    uid : bpy.props.StringProperty() #type:ignore
    cached_dependencies : list[str]

class _BlResourceCollection(bpy.types.PropertyGroup):
    items : bpy.types.PropertyCollection

class _BlProject():
    name : bpy.props.StringProperty(name="Name") #type:ignore
    filepath : bpy.props.StringProperty(name="project_dir", subtype="DIR_PATH") #type:ignore