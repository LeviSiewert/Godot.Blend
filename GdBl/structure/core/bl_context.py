from contextvars import ContextVar

class BlContext():
    gd_project : ContextVar
    gd_file : ContextVar
    gd_resource : ContextVar
    gd_subresource : ContextVar
    
    bl_project : ContextVar
    bl_file : ContextVar
    bl_resource : ContextVar
    bl_subresource : ContextVar

    bl_collection : ContextVar

    meta_tree : ContextVar[tuple]

    def __init__(self):
        self.gd_project = ContextVar(str(id(self))+"gd_project")
        self.gd_file = ContextVar(str(id(self))+"gd_file")
        self.gd_resource = ContextVar(str(id(self))+"gd_resource")
        self.gd_subresource = ContextVar(str(id(self))+"gd_subresource")
        self.bl_project = ContextVar(str(id(self))+"bl_project")
        self.bl_file = ContextVar(str(id(self))+"bl_file")
        self.bl_resource = ContextVar(str(id(self))+"bl_resource")
        self.bl_subresource = ContextVar(str(id(self))+"bl_subresource")
        self.bl_collection = ContextVar(str(id(self))+"bl_collection")
        self.meta_tree = ContextVar(str(id(self))+"meta_tree")