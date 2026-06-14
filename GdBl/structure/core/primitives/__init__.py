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