from ._transformers import GdToBlTransformer, GdToBlTransformerSet, BlToGdTransformer, BlToGdTransformerSet, TransformerOptions

class OPTIONS():
    class GdToBl(TransformerOptions):
        pass
    class BlToGd(TransformerOptions):
        pass


class Resource():
    ''' Scene <-> Collection. Primary resource stored as "root" node.
    '''
    class GdToBl(GdToBlTransformer):
        pass
    class BlToGd(BlToGdTransformer):
        pass

class SubResource():
    ''' Generic Subresource, derivitives by type/script are in .subtypes && via modules #TODO '''
    class GdToBl(GdToBlTransformer):
        pass
    class BlToGd(BlToGdTransformer):
        pass


class Node():
    ''' Generic Subresource, derivitives by type/script are in .nodes && via modules #TODO '''
    class GdToBl(GdToBlTransformer):
        pass
    class BlToGd(BlToGdTransformer):
        pass

class Scene():
    ''' Scene <-> Collection
        - Collection marked as asset, tags include UID 
        - Extres as Instance fr env
            - Missing nodes have paths recorded, notation in name matching blender's missing paths?
        - Signals attached to node.gd.signals
            - References nodes OR relative paths if missing depending on construction.
        - Edits require seperate caching file if collection not already present
            - Collections matched via Assets Tags ( Uid -> Path factoring in some project remap notes?? )
        - Subresources are sorted based on users?
            - Single users are made children of referencer
            - Multiple users are stored under root? or sub collection. TODO: Decide 
            - Could also be flat, no parents & hidden
    '''
    class GdToBl(GdToBlTransformer):
        pass
    class BlToGd(BlToGdTransformer):
        pass


bl_to_gd = BlToGdTransformerSet(
    transformers=[
        Node.BlToGd,
        Scene.BlToGd,
        SubResource.BlToGd,
        Resource.BlToGd,
    ],
    options={
        "node":OPTIONS.BlToGd
    }
)

gd_to_bl = GdToBlTransformerSet(
    transformers=[
        Node.GdToBl,
        Scene.GdToBl,
        SubResource.GdToBl,
        Resource.GdToBl,
    ],
    options={
        "node":OPTIONS.GdToBl
    }
)