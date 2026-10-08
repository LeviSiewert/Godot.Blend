@tool
extends Node

enum Mode{
	SCRIPT,
	INTERNAL,
}

@export var mode := Mode.SCRIPT
@export_file var path : String = "res://extraction.json"

func _run():
	# var custom_classes: Array = ProjectSettings.get_global_class_list() 
		# https://docs.godotengine.org/en/stable/classes/class_projectsettings.html#class-projectsettings-method-get-global-class-list
	# var engine_classes: PackedStringArray = ClassDB.get_class_list()
	# https://docs.godotengine.org/en/stable/classes/class_script.html
	# https://docs.godotengine.org/en/stable/classes/class_classdB.html

	# /ClayOfMan/bl_gd_importer/commit/a59c458305a098516ad3b379f29d3ae655207c4b#diff-fb56387dd4378fd007cd9f1a100e40d66bed7c2e
	if mode == Mode.SCRIPT:
		var result := {
			"Meta":Engine.get_version_info(),
			"info":_run_script(),
		}
		var r = JSON.stringify(result, "\t")
		FileAccess.open(path, FileAccess.WRITE).store_string(r)
	else:
		var result := {
			"Meta"=Engine.get_version_info(),
			"info"=_run_classes(),
		}
		var r = JSON.stringify(result, "\t")
		FileAccess.open(path, FileAccess.WRITE).store_string(r)


@export_tool_button("run") var run = _run


func _run_classes()->Array:
	# TODO: export all engine classes in order for load effeciency 
	var engine_classes: PackedStringArray = ClassDB.get_class_list()
	var res := []
	for x in engine_classes:
		res.append(produce_engine_type(x))
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

	## ProjectSettings.get_global_class_list()

func produce_engine_type(name:String)->Dictionary:

	var signals:Array[Dictionary] = []
	for x in ClassDB.class_get_signal_list(name):
		signals.append(produce_signal(x))
	
	var properties = []
	for x in ClassDB.class_get_property_list(name, true):
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
	return _signal_def

func produce_value(_value_def:Dictionary)->Dictionary:
	return {
		"_type":"Value",
		"default":null,
		"typing":null, # list[ValueType] | ValueType | null
	}

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
