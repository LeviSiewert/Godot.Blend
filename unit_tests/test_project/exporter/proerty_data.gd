extends Resource
class_name PropertyData

@export var default_value : Variant 

## Typing:
@export var cls_name  : StringName  ## If typed to a class, ie (var a : PropertyData) 
@export var type : int              ## Mapping of types, See Variant.Type
## Hinting/Display:    
@export var hint_type : int         ## See PROPERTY_HINT_...
@export var hint_str  : String      ## Input variable for PROPERTY_HINT_...
@export var usage       : int       ## See PROPERTY_USAGE_...