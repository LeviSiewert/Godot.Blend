from . import structure 
from . import operators

def register():
    structure.register()
    operators.register()

def unregister():
    operators.unregister()
    structure.unregister()