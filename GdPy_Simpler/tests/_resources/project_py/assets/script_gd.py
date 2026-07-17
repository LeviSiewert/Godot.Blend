from .....core.structure import Resource
from .....files import FileScript, FileUid
from .....core.values import *

def make()->tuple[FileScript, Resource, str]:
    src = '''
extends Node

@export var resource : Resource
@export var noderef : Node
'''
    res = None
    file = FileScript.construct(
        uid="uid://cr1tpol7u62kd",
        path="res://assets/script.gd",
    )
    return file, res, src

def make_uid()->tuple[FileScript, Resource, str]:
    src = '''uid://cr1tpol7u62kd'''
    res = None
    file = FileUid.construct(
        path="res://assets/script.gd",
    )
    return file, res, src
    