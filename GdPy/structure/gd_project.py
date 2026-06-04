from __future__ import annotations
from typing import Any
from .gd_definitions import ClassDb
from ..primitives import Collection
from ..primitives import SignalContainer

class File():
    uuid : str
    path : str
    data : Any

class FileDb(Collection):
    pass

class GdProject(SignalContainer):
    files : FileDb
    class_db : ClassDb

    def __init__(self):
        self.files = FileDb()
        self.class_db = ClassDb()
        super().__init__()