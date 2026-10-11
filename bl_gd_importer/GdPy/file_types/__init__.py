''' Implimentation of `File` generic implimentation  '''

from typing import Type
import re

from ..core.structure import File
from ..transformers import gd_to_py
from ..transformers.gd_to_py.lark_tools import make_parser


class File_GodotAscii(File):
    ''' All Godot's ascii Files [tres, tscn, godot, import]
    Implimentation of `GdPy.transformers.gd_to_py` && `.gd_to_py.lark_tools`
    '''

    @classmethod
    def matches_file(cls, context, fs, fp):
        return fp.rsplit(".") in ["tres","tscn","godot","import"]

    def prefetch_uid(self):
        if res:=self.resource:
            return res.uid
        with self.context.project.fs.open(self.path) as f:
            return re.search('uid="uid://(.+)"',f.readline()).group(1)

    def read(self, data):
        parser = make_parser()
        s = gd_to_py.make_gd_to_py()
        return s.transform(parser(data))

    def write(self, res):
        s = gd_to_py.make_py_to_gd()
        return s.transform(res)

generic : list[Type[File]] = [
    File_GodotAscii,
]