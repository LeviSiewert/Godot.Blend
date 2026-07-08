@tool
extends Node

@export var path: String

@export var data : ClassDataDB
@export_tool_button("export") var _tool : Callable = run


# class SignalDataReturn extends Resource:
#     @export var cls_name : String
#     @export var hint : int
#     @export var hint_string : String 
#     @export var name : String
#     @export var type : String
#     @export var usage : String


func run():
    data = null
    var db := ClassDataDB.new()
    db.classes = []
    data = db
    # var _classes := []

    var _filter_by := ClassDB.get_inheriters_from_class("Resource")
    _filter_by.append_array(ClassDB.get_inheriters_from_class("Node"))
    _filter_by.append("Node")
    _filter_by.append("Resource")

    for cls in Array(ClassDB.get_class_list()).filter(func(x)->bool: return x in _filter_by):
        # ## Inbuilt classes
        if !(cls in _filter_by): continue
        
        var d := ClassData.new()
        db.classes.append(d)
        d.name = StringName(cls)
        d.c_extends = StringName(ClassDB.get_parent_class(cls))

        # d.properties
        for val : Dictionary in ClassDB.class_get_property_list(cls, true):
            var pd := PropertyData.new()
            d.properties[val["name"]] = pd

            pd.cls_name = val["class_name"]
            pd.type = val["type"]
            pd.hint_type = val["hint"]
            pd.hint_str = val["hint_string"]
            pd.usage = val["usage"]
            pd.default_value = ClassDB.class_get_property_default_value(cls, val["name"])

        # for val : Dictionary in ClassDB.class_get_signal_list(cls, false):
        #     var sd := SignalData.new()
        #     d.signals[val["name"]] = sd
        #     sd.args = val["args"]
        #     sd.default_args = val["default_args"]
        #     sd.flags = val["flags"]
        #     sd.id = val["id"]
        #     sd.name = val["name"]
        #     print(val)


    var scripts : Dictionary[String, Script] = _load_all_scripts()
    for script_path in scripts.keys() :
        var script = scripts[script_path]
        if !(script.get_instance_base_type() in _filter_by): continue
        var d := ClassData.new()
        db.classes.append(d)

        d.path = script_path
        d.name = script.get_global_name()
        d.is_abstract = script.is_abstract()
        var _base_script = scripts.find_key(script.get_base_script())
         
        if _base_script == null:
            d.c_extends = script.get_instance_base_type()
        else:
            d.c_extends = _base_script

        # print("PROPERTY LIST:", script.get_property_list())  
        for val in script.get_property_list():
            var pd := PropertyData.new()
            d.properties[val["name"]] = pd

            pd.cls_name = val["class_name"]
            pd.hint_type = val["hint"]
            pd.hint_type = val["type"]
            pd.hint_str = val["hint_string"]
            pd.usage = val["usage"]
            pd.default_value = script.get_property_default_value(val["name"])

        # for val : Dictionary in ClassDB.get_signal_list():
        #     var sd := SignalData.new()
        #     d.signals[val["name"]] = sd
        #     sd.args = val["args"]
        #     sd.default_args = val["default_args"]
        #     sd.flags = val["flags"]
        #     sd.id = val["id"]
        #     sd.name = val["name"]
        #     print(val)

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
    