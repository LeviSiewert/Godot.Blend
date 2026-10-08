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

from ...core.defininitions import GdDefType, GdDefProperty, GdDefSignal, GdDefValue, GdDefValueTyping
from ...core.transformer import Session, Transformer, TransformerOptions, TransformerSet, TRANSFORM, TRANSFORM_CHILDREN, STEP

from typing import Type

class _Bases():
    class FrFile_Session(Session):
        pass

    class ToFile_Session(Session):
        pass

    class FrFile_Transformer(Transformer):
        memoized=False
        keys : tuple[str] = tuple()
        def match(self, session, node):
            if not isinstance(node, dict):
                return False
            return node["_type"] in self.keys

class _Root():
    class FrFile(_Bases.FrFile_Transformer):
        def match(self, session, node:dict):
            return all([
                "engine" in node.keys(), 
                "classes" in node.keys(), 
                "type_map" in node.keys(), 
                "hint_map" in node.keys(), 
            ])

class _GdDefType():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Type","T"]

class _GdDefProperty():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Property","P"]

class _GdDefSignal():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Signal","S"]

class _GdDefValueTyping():
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
            _GdDefType.FrFile,
            _GdDefProperty.FrFile,
            _GdDefSignal.FrFile,
            _GdDefValueTyping.FrFile,
            _Root.FrFile,
            Default,
    ]),
            *extras,
    ])
