from .core import BlToPy, BlToPyRuleset
from .core import PyToBl, PyToBlRuleset, PyToBlContext

# from ....GdPy.structure.values
from ....GdPy.structure.core.property_collection import PropertyCollection
from ..core.properties import BlProperty, BlPropertyCollection

class PyToBl_Properties(PyToBl):
    _keys = (PropertyCollection,)
    def transform(self, node:PropertyCollection, c:PyToBlContext, *args, **kwargs):
        """ This transform should be a side effect on resulting container's parent, 
        as target object's properylist already exists. 
        This will have to be a existing_object "thrown" by the parent into the context... somehow
        As with all other BlCollections, children are already attached
        """
        bl_props : BlPropertyCollection = c.existing_object.get()
        assert(not(bl_props is None))

        for k, v in node:
            p = bl_props.add()
            p.name = k
            t = c.existing_object.set(p)
            yield (v,) 
            ## Throwing child value to fullfill
            res = c.children.get(v)
            assert (res is p)
            c.existing_object.reset(t)

        return bl_props

class BlToPy_Properties(BlToPy):
    _keys = (BlPropertyCollection,)
    def transform(self, node:BlPropertyCollection, c, *args, **kwargs):

        yield res.values()
        ## Yield all children, let god sort them out

        di = c.children_map.get()

        res = PropertyCollection()
        for k,v in node.items():
            res[k] = di[v]

        return res

        

py_to_bl_rulset = BlToPyRuleset(
    BlToPy_Properties,
    )
bl_to_gd_rulset = PyToBlRuleset(
    BlToPy_Properties,
    )