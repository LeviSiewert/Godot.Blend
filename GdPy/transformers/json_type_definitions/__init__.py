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

    class ToFile_Transformer(Transformer):
        memoized=False
        types : tuple[Type] = tuple()
        def match(self, session, node):
            return isinstance(node, self.types)

class _GdDefType():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Type","T"]
    class ToFile(_Bases.ToFile_Transformer):
        types = [GdDefType]

class _GdDefProperty():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Property","P"]
    class ToFile(_Bases.ToFile_Transformer):
        types = [GdDefProperty]

class _GdDefSignal():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Signal","S"]
    class ToFile(_Bases.ToFile_Transformer):
        types = [GdDefSignal]

class _GdDefValue():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["Value","V"]
    class ToFile(_Bases.ToFile_Transformer):
        types = [GdDefValue]

class _GdDefValueTyping():
    class FrFile(_Bases.FrFile_Transformer):
        keys = ["ValueTyping","VT"]
    class ToFile(_Bases.ToFile_Transformer):
        types = [GdDefValueTyping]

class Default(Transformer):
    memoized=False
    def match(self, session, node):
        return True
    def transform(self, session, node):
        return node

fr_file = _Bases.FrFile_Session(
    transformer_sets=[TransformerSet("base", [
        _GdDefType.FrFile,
        _GdDefProperty.FrFile,
        _GdDefSignal.FrFile,
        _GdDefValue.FrFile,
        _GdDefValueTyping.FrFile,  
        Default,
])])

to_file = _Bases.ToFile_Session(
    transformer_sets=[TransformerSet("base", [
        _GdDefType.ToFile,
        _GdDefProperty.ToFile,
        _GdDefSignal.ToFile,
        _GdDefValue.ToFile,
        _GdDefValueTyping.ToFile,  
        Default,
])]) 
