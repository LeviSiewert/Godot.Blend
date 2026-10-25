from . import properties, preferences, structure, operators,panels, promise

def register():
    promise.register()
    properties.register()
    # structure.register()
    # preferences.register()
    # operators.register()
    # panels.register()

def unregister():
    # panels.unregister()
    # operators.unregister()
    # preferences.unregister()
    # structure.unregister()
    properties.unregister()
    promise.unregister()