from pathlib import Path

thisdir = Path(__file__).parent.resolve()

def get_test_tscn_file()->Path:
    return (thisdir / "test.tscn")
def get_test_tres_file()->Path:
    return (thisdir / "exported_classes.tres")
def get_test_proj_file()->Path:
    return (thisdir / "project.godot")
