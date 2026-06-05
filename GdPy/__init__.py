""" 
Module for parsing generic Godot Tscn & Like (Modified TOML) files to a python data structure
As this is built for continious use rather than one-off use, Signals should be suppported as first class objects.

The transformer pipeline (via hooks) for use in blender is contained in a seperate lookup for env isolation.
"""

from .structure import *