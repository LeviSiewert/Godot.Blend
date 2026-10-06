''' TODO: Transform json dump of types into structure. 
Tree is:
[
    {
        "_type"      : "T"
        "extends"    : str|None,
        "properties" : [{"_type":"P", "name":str, value:{"_type":"V", typing={"_type":"VT"} default=...}}],
        "signals"    : [{"_type":"S", "name":str, value:{"_type":"V", typing={"_type":"VT"} default=...}}],
        "type"       : "INTERNAL"|"SCRIPT",
        "uid"        : str|None,
        "path"       : str|None,
        "class_name" : str|None,
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
