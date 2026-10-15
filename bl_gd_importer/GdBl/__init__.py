from . import properties, preferences, structure, operators,panels

def register():
    properties.register()
    structure.register()
    # preferences.register()
    # operators.register()
    # panels.register()

def unregister():
    # panels.unregister()
    # operators.unregister()
    # preferences.unregister()
    structure.unregister()
    properties.unregister()