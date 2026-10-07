@tool
extends EditorScript

enum Mode{
    SCRIPT,
    INTERNAL,
}

@export var mode := Mode.SCRIPT
@export_file var path : String

func _run():
    # var custom_classes: Array = ProjectSettings.get_global_class_list() 
        # https://docs.godotengine.org/en/stable/classes/class_projectsettings.html#class-projectsettings-method-get-global-class-list
    # var engine_classes: PackedStringArray = ClassDB.get_class_list()
    # https://docs.godotengine.org/en/stable/classes/class_script.html
    # https://docs.godotengine.org/en/stable/classes/class_classdb.html

    # /ClayOfMan/bl_gd_importer/commit/a59c458305a098516ad3b379f29d3ae655207c4b#diff-fb56387dd4378fd007cd9f1a100e40d66bed7c2e

func _run_classes()->Dictionary:
    return

func _run_script()->Dictionary:
    var _filter_by := ClassDb.get_inheriters_from_class("Resource")
    _filter_by.append_array(ClassDB.get_inheriters_from_class("Node"))
    _filter_by.append("Node")
    _filter_by.append("Resource")

    var scripts = _load_all_scripts()
    
    # for k,v in scripts:


    ## ProjectSettings.get_global_class_list()

func produce_engine_type(name:String)->Dictionary:

    signals = []
    for x in ClassDb.class_get_signal_list(name):
        signals.append(produce_signal(x))
    
    properties = []
    for x in ClassDb.class_get_property_list(name):
        signals.append(produce_properties(x))

    return {
        "_type":"Class",
        "extends":null, #null|str
        "global_name":name,
        "signals":signals,
        "properties":properties,
    }
    
func produce_script_type(name:String)->Dictionary:
    signals = []
    properties = []

    return {
        "_type":"Script",
        "extends":null, #null|str
        "global_name":name,
        "uid":null,
        "path":null,
        "signals":signals,
        "properties":properties,
    }

func produce_properties(_property_def:Dictionary):
    return {
        "_type":"property",
    }

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