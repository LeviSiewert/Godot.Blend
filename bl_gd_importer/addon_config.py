from pathlib import Path

from contextvars import ContextVar

bl_info = {
    "name": "Godot IO",
    "author": "Levi Siewert",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

id_name = "bl_gd_importer"
addon_path = str(Path(__file__).parent.resolve())

flag_testing = ContextVar("flag_testing",default=False)
flag_debug = ContextVar("flag_debug",default=False)