@tool
extends Node

enum Mode{
	SCRIPT,
	INTERNAL,
}

@export var mode := Mode.SCRIPT
@export_file var path : String = "res://extraction.json"
@export_tool_button("run") var run = _run

#GENERAL NOTES:
# https://github.com/godotengine/godot/issues/76407
# Hint map and type map 

func _run():
	var hint_map := get_hint_map()
	var type_map := get_type_map()
	var usage_map:= get_property_usage_map()

	if mode == Mode.SCRIPT:
		var result := {
			"engine":Engine.get_version_info(),
			"hint_map":hint_map,
			"type_map":type_map,
			"usage_map":usage_map,
			"classes":_run_script(),
		}
		var r = JSON.stringify(result, "\t")
		FileAccess.open(path, FileAccess.WRITE).store_string(r)
	else:
		var result := {
			"engine":Engine.get_version_info(),
			"hint_map":hint_map,
			"type_map":type_map,
			"usage_map":usage_map,
			"classes":_run_classes(),
		}
		var r = JSON.stringify(result, "\t")
		FileAccess.open(path, FileAccess.WRITE).store_string(r)

func get_type_map()->Dictionary:
	var type_map := {}
	for i in TYPE_MAX:
		type_map[i] = type_string(i)
	return type_map

func get_hint_map()->Dictionary:
	## Can't get keys from builtin PropertyHint enum, 
	## Map fr https://docs.godotengine.org/en/stable/classes/class_@globalscope.html
	## FUTURE: Different versions of this per engine version?
	return {
		"PROPERTY_HINT_NONE":0,
		"PROPERTY_HINT_RANGE":1,
		"PROPERTY_HINT_ENUM":2,
		"PROPERTY_HINT_ENUM_SUGGESTION":3,
		"PROPERTY_HINT_EXP_EASING":4,
		"PROPERTY_HINT_LINK":5,
		"PROPERTY_HINT_FLAGS":6,
		"PROPERTY_HINT_LAYERS_2D_RENDER":7,
		"PROPERTY_HINT_LAYERS_2D_PHYSICS":8,
		"PROPERTY_HINT_LAYERS_2D_NAVIGATION":9,
		"PROPERTY_HINT_LAYERS_3D_RENDER":10,
		"PROPERTY_HINT_LAYERS_3D_PHYSICS":11,
		"PROPERTY_HINT_LAYERS_3D_NAVIGATION":12,
		"PROPERTY_HINT_LAYERS_AVOIDANCE":37,
		"PROPERTY_HINT_FILE":13,
		"PROPERTY_HINT_DIR":14,
		"PROPERTY_HINT_GLOBAL_FILE":15,
		"PROPERTY_HINT_GLOBAL_DIR":16,
		"PROPERTY_HINT_RESOURCE_TYPE":17,
		"PROPERTY_HINT_MULTILINE_TEXT":18,
		"PROPERTY_HINT_EXPRESSION":19,
		"PROPERTY_HINT_PLACEHOLDER_TEXT":20,
		"PROPERTY_HINT_COLOR_NO_ALPHA":21,
		"PROPERTY_HINT_OBJECT_ID":22,
		"PROPERTY_HINT_TYPE_STRING":23,
		"PROPERTY_HINT_NODE_PATH_TO_EDITED_NODE":24,
		"PROPERTY_HINT_OBJECT_TOO_BIG":25,
		"PROPERTY_HINT_NODE_PATH_VALID_TYPES":26,
		"PROPERTY_HINT_SAVE_FILE":27,
		"PROPERTY_HINT_GLOBAL_SAVE_FILE":28,
		"PROPERTY_HINT_INT_IS_OBJECTID":29,
		"PROPERTY_HINT_INT_IS_POINTER":30,
		"PROPERTY_HINT_ARRAY_TYPE":31,
		"PROPERTY_HINT_DICTIONARY_TYPE":38,
		"PROPERTY_HINT_LOCALE_ID":32,
		"PROPERTY_HINT_LOCALIZABLE_STRING":33,
		"PROPERTY_HINT_NODE_TYPE":34,
		"PROPERTY_HINT_HIDE_QUATERNION_EDIT":35,
		"PROPERTY_HINT_PASSWORD":36,
		"PROPERTY_HINT_TOOL_BUTTON":39,
		"PROPERTY_HINT_ONESHOT":40,
		"PROPERTY_HINT_GROUP_ENABLE":42,
		"PROPERTY_HINT_INPUT_NAME":43,
		"PROPERTY_HINT_FILE_PATH":44,
		"PROPERTY_HINT_MAX":45,
	}

func get_property_usage_map()->Dictionary:
	return {
		"PROPERTY_USAGE_NONE":0,#|PROPERTY_USAGE_NO_EDITOR
		"PROPERTY_USAGE_STORAGE":2,
		"PROPERTY_USAGE_EDITOR":4,
		"PROPERTY_USAGE_DEFAULT":6,
		"PROPERTY_USAGE_INTERNAL":8,
		"PROPERTY_USAGE_CHECKABLE":16,
		"PROPERTY_USAGE_CHECKED":32,
		"PROPERTY_USAGE_GROUP":64,
		"PROPERTY_USAGE_CATEGORY":128,
		"PROPERTY_USAGE_SUBGROUP":256,
		"PROPERTY_USAGE_CLASS_IS_BITFIELD":512,
		"PROPERTY_USAGE_NO_INSTANCE_STATE":1024,
		"PROPERTY_USAGE_RESTART_IF_CHANGED":2048,
		"PROPERTY_USAGE_SCRIPT_VARIABLE":4096,
		"PROPERTY_USAGE_STORE_IF_NULL":8192,
		"PROPERTY_USAGE_UPDATE_ALL_IF_MODIFIED":16384,
		"PROPERTY_USAGE_SCRIPT_DEFAULT_VALUE":32768,
		"PROPERTY_USAGE_CLASS_IS_ENUM":65536,
		"PROPERTY_USAGE_NIL_IS_VARIANT":131072,
		"PROPERTY_USAGE_ARRAY":262144,
		"PROPERTY_USAGE_ALWAYS_DUPLICATE":524288,
		"PROPERTY_USAGE_NEVER_DUPLICATE":1048576,
		"PROPERTY_USAGE_HIGH_END_GFX":2097152,
		"PROPERTY_USAGE_NODE_PATH_FROM_SCENE_ROOT":4194304,
		"PROPERTY_USAGE_RESOURCE_NOT_PERSISTENT":8388608,
		"PROPERTY_USAGE_KEYING_INCREMENTS":16777216,
		"PROPERTY_USAGE_DEFERRED_SET_RESOURCE":33554432,
		"PROPERTY_USAGE_EDITOR_INSTANTIATE_OBJECT":67108864,
		"PROPERTY_USAGE_EDITOR_BASIC_SETTING":134217728,
		"PROPERTY_USAGE_READ_ONLY":268435456,
		"PROPERTY_USAGE_SECRET":536870912,
	}

func _run_classes()->Array:
	# TODO: export all engine classes in order for load effeciency 
	var engine_classes: PackedStringArray = ClassDB.get_class_list()
	var res := []
	var _filter_by := ClassDB.get_inheriters_from_class("Resource")
	_filter_by.append_array(ClassDB.get_inheriters_from_class("Node"))
	
	res.append(produce_engine_type("Resource", false))
	res.append(produce_engine_type("Node", false))
	for x in engine_classes:
		if !(x in _filter_by): 
			continue
		res.append(produce_engine_type(x, true))
	
	return res

func _run_script()->Array:
	# TODO: export all engine classes in order for load effeciency  

	var _filter_by := ClassDB.get_inheriters_from_class("Resource")
	_filter_by.append_array(ClassDB.get_inheriters_from_class("Node"))
	_filter_by.append("Node")
	_filter_by.append("Resource")

	var scripts = _load_all_scripts()

	var res := []
	
	for script_path in scripts.keys() :
		var script : Script = scripts[script_path]
		if !(script.get_instance_base_type() in _filter_by): continue
		res.append(produce_script_type(script_path,script))
	
	return res


func produce_engine_type(name:String, limit=true)->Dictionary:

	var signals:Array[Dictionary] = []
	for x in ClassDB.class_get_signal_list(name, limit):
		signals.append(produce_signal(x))
	
	var properties = []
	for x in ClassDB.class_get_property_list(name, limit):
		properties.append(produce_class_properties(name, x))

	return {
		"_type":"Class",
		"extends":ClassDB.get_parent_class(name),
		"global_name":name,
		"signals":signals,
		"properties":properties,
		"abstract":ClassDB.can_instantiate(name),
	}


func produce_class_properties(cls, prop_data:Dictionary)->Dictionary:
	prop_data["default_value"] = ClassDB.class_get_property_default_value(cls, prop_data["name"])
	prop_data["_type"] = "Property"
	return prop_data


func produce_script_type(script_path:String, script:Script)->Dictionary:
	var signals = []
	var properties = []

	for x in script.get_script_property_list():
		properties.append(produce_properties(script, x))

	for x in script.get_script_signal_list():
		signals.append(produce_signal(x))

	return {
		"_type":"Script",
		"extends_script":script.get_base_script(), #null|str
		"extends_class":script.get_instance_base_type(), #null|str
		"global_name":script.get_global_name() ,
		"uid":ResourceUID.path_to_uid(script_path), #incorrect, 
		"abstract": script.is_abstract(),
		"path":script_path,
		"signals":signals,
		"properties":properties,
	}


func produce_properties(script:Script, property_def:Dictionary):
	var res := property_def
	res["_type"] = "Property"
	res["default_value"] = script.get_property_default_value(property_def["name"])
	return res


func produce_signal(_signal_def:Dictionary)->Dictionary:
	# args, default_args, flags, id, name, return: (class_name, hint, hint_string, name, type, usage).
	_signal_def["_type"] = "Signal"
	for x in _signal_def["args"]:
		x["_type"] = "Value"
	for x in _signal_def["default_args"]:
		x["_type"] = "Value"
	var ret = _signal_def.get("return", null)
	if not (ret == null):
		ret["_type"] = "Value"
	return _signal_def

func _load_all_scripts(iter:String = "res://")->Dictionary[String,Script]:
	var dir = DirAccess.open(iter)
	if !dir: return {}
	var res : Dictionary[String,Script] = {}
	dir.get_files()
	for x in dir.get_files():
		if x.begins_with("."): continue
		if x.ends_with(".gd"):
			res[iter+x]=load(iter+x)
	for x in dir.get_directories():
		if x.begins_with("."): continue
		res.merge(_load_all_scripts(iter+x+"/"))
	return res
