extends Resource
class_name ClassData
 
@export var name       : StringName
@export var c_extends  : StringName

@export var properties : Dictionary[String, PropertyData]
@export var signals    : Dictionary[String, SignalData]

@export var is_abstract: bool
@export var language   : StringName
@export var path       : String

func init()->void:
    properties = {}
    signals    = {}