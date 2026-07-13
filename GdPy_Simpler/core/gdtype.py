from __future__ import annotations

class GdType():
    ''' Abstract class, represents any type allowable in this system '''


class GdTypePrimitive():
    ''' Represents a primitive value type, use standard instances '''

class SignalDef():
    pass

class PropertyDef():
    pass

class GdTypeClass():
    ''' Represents a class '''
    extends : GdType

    uid : str
    filepath : str
    class_name : str

    properties : dict[str, PropertyDef]
    signals : dict[str, SignalDef]


class GdTypeDb():
    pass
