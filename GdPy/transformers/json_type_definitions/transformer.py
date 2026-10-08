''' TODO: Transform json dump of types into structure. 
Tree is:


"meta": {...}
"info": [
		{
			"_type": "Script",
			"abstract": false,
			"extends_class": "Node",
			"extends_script": "<Object#null>",
			"global_name": "",
			"path": "res://GdPy/godot_utilities/extract_types.gd",
			"properties": [
				{
					"_type": "Property",
					"class_name": "",
					"default_value": null,
					"hint": 0,
					"hint_string": "res://GdPy/godot_utilities/extract_types.gd",
					"name": "extract_types.gd",
					"type": 0,
					"usage": 128
				}],
			"signals": [],
			"uid": "uid://d2ysfw8f0dasa"
		},
]

Don't worry about post-processing / incorperating extensions and the like. That will be done later.
Relationships will be done via "on-fetch" promises.

'''

from ...core.structure import DefType, DefProperty, DefSignal, DefValue, DefValueTyping, PropertyUsage, PropertyHint, PrimitiveType
from ...core.transformer import Session, Transformer, TransformerOptions, TransformerSet, TRANSFORM, TRANSFORM_CHILDREN, STEP

from contextvars import ContextVar
from typing import Type, Generator, Any, Iterable

class _Bases():
    class FrFile_Session(Session):
        pass

    class FrFile_Transformer(Transformer):
        memoized=False
        keys : tuple[str] = tuple()
        def match(self, session, node):
            if not isinstance(node, dict):
                return False
            return node.get("_type", None) in self.keys

class Options_FrFile(TransformerOptions):
    def __init__(self, session):
        self.get_hint = ContextVar("get_hint",default=None)
        self.get_type = ContextVar("get_type",default=None)
        self.get_usage = ContextVar("get_usage",default=None)
    get_hint : ContextVar[callable] = None
    get_type : ContextVar[callable] = None
    get_usage : ContextVar[callable] = None

from ...core.values import type_map as _type_map

class _Root():
    class FrFile(_Bases.FrFile_Transformer):
        def match(self, session, node:dict):
            return all([
                "engine" in node.keys(), 
                "classes" in node.keys(),
            ])
        def transform(self, session, node)->Generator[Any,Any,list[DefType]]:
            hint_map = dict({v:PropertyHint[k] for k,v in node["hint_map"].items()})
            def get_hint(i:int):
                return hint_map[i]

            type_map = dict({v:_type_map[PrimitiveType[k.upper()]] for k,v in node["type_map"].items()})
            def get_type(i:int):
                return type_map[i]
            
            usage_map = dict({v:PropertyUsage[k] for k,v in node["usage_map"].items()})
            def get_usage(i:int):
                return usage_map[i]

            t0 = session.options["lookup"].get_hint.set(get_hint)
            t1 = session.options["lookup"].get_type.set(get_type)
            t2 = session.options["lookup"].get_usage.set(get_usage)
            
            classes = yield TRANSFORM_CHILDREN(node["classes"]) 

            session.options["lookup"].get_hint.reset(t0)
            session.options["lookup"].get_type.reset(t1)
            session.options["lookup"].get_usage.reset(t2)

            return classes

class _DefType():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Type","T"]

class _DefProperty():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Property","P"]

class _DefSignal():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Signal","S"]

class _DefValueTyping():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Value","V"]

class Default(Transformer):
    memoized=False
    def match(self, session, node):
        return True
    def transform(self, session, node):
        return node

def make_fr_file(extras:Iterable[TransformerSet]=tuple())->_Bases.FrFile_Session:
    return _Bases.FrFile_Session(
        transformer_sets=[TransformerSet("base", [
            _DefType.FrFile,
            _DefProperty.FrFile,
            _DefSignal.FrFile,
            _DefValueTyping.FrFile,
            _Root.FrFile,
            Default,
        ], 
        options = {
            "lookup":Options_FrFile
        }
    ),
            *extras,
    ])
