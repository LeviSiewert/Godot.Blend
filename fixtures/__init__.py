from pathlib import Path

cwd = Path.cwd()

def get_test_tscn_file()->Path:
    return (cwd / "test.tscn")
def get_test_tres_file()->Path:
    return (cwd / "exported_classes.tres")
def get_test_proj_file()->Path:
    return (cwd / "project.godot")
