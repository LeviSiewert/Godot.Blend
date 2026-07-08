import bpy

def get_file_collection(ensure=True):
    """ Ensure & get file collection that retains all referenced external files 
    Due to lack of a singleton in blender for addons, this is the next best thing ;/
    """
    if res := bpy.data.texts.get("_GODOT",None):
        return res.gd
    
    if ensure:
        res = bpy.data.texts.new(name="_GODOT")
        res.write("""
    !! This file is a container for all 'thin' External/Referenced GODOT files !!

    If you are deleting this, make sure to have all external tres/resource edits saved to disk!
    This file will regenerate __every__ time that referenced (.tres, .import, .godot) files are needed to be edited.
    """)
        return res.gd
    
    return None