from . import preferences, datastruct,operators,panels

def register():
    datastruct.register()
    preferences.register()
    operators.register()
    panels.register()

def unregister():
    preferences.unregister()
    datastruct.unregister()
    operators.unregister()
    panels.unregister()