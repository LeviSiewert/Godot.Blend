import bpy
from .primitives.pointer_collection import PointerCollection

class BlPropertyCollection(PointerCollection):
    ''' 
    Implementation for Gd of multi-object pointer collection, which was seperated for future use w/ generic File, Res, SubRes
    Considering using a TransformerV2 for store_value, as Dict, Array, are basically already doing so with a limited scope.
    ''' 

    _bins = ("bin_array","bin_dict",)
    
    def _bin_val_to_key_matcher(self, val):
        if isinstance(val,dict):
            return "bin_dict"
        elif isinstance(val,list):
            return "bin_array"        
        return "bin_"+val.__class__.__name__

_all = (
    BlPropertyCollection
)