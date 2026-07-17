from .....core.structure import Resource
from .....files import FileScript, FileUid
from .....core.values import *

def make()->tuple[FileScript, Resource, str]:
    src = '''
class_name GlobalNodeName
extends Node

'''
    res = None
    file = FileScript.construct(
        uid="uid://4ixpsfd7ehyv",
        path="res://assets/script_global.gd",
    )
    return file, res, src

def make_uid()->tuple[FileScript, Resource, str]:
    src = '''uid://4ixpsfd7ehyv'''
    res = None
    file = FileUid.construct(
        path="res://assets/script_global.gd",
    )
    return file, res, src
    