import bpy

from ._transformer import (
    PyToBlContext, 
    PyToBlRuleset, 
    PyToBlModule, 
    BlToPyContext, 
    BlToPyRuleset,
    BlToPyModule,
)

from ...core.structure import (
    ExtResource as BlExtResource,
    SubResource as BlSubResource,
    GdResource as BlGdResource,
)

from ....GdPy.core.resources import(
    ExtResource as PyExtResource,
    SubResource as PySubResource,
    ResourceTres as PyResourceTres,
)


class BlToPy_ExtResource(BlToPyModule):
    _keys = (BlExtResource,)
    def transform(self, c, node:BlExtResource):
        return PyExtResource(
            type=node.type, 
            uid=node.uid,
            path=node.path, 
            id=node.name, 
        )

class PyToBl_ExtResource(PyToBlModule):
    _keys = (PyExtResource,)
    def transform(self, c, node:PyExtResource):
        target = c.existing_object.get()
        target.name = node.id.addr
        target.uid = node.uid.addr
        target.path = node.path.addr
        target.type = node.type.addr
        
        #return Target
        # Mutated in place!


class BlToPy_SubResource(BlToPyModule):
    _keys = (BlSubResource,)
    def transform(self, c, node:BlSubResource):

        yield (node.properties,)
        props = c.children.get()[0]

        return PySubResource.construct(node.name,
            type = node.type,
            properties = props,
        )
    
class PyToBl_SubResource(PyToBlModule):
    _keys = (PySubResource,)
    def transform(self, c, node:PySubResource):
        target : BlSubResource = c.existing_object.get()
        target.name = node.id.addr
        target.type = node.type
        target.script_type = node.script_type

        t = c.existing_object.set(target.properties)
        yield (node.properties,)
        c.existing_object.reset(t)
        
        #return target
        # Mutated in place!



class BlToPy_ResourceTres(BlToPyModule):
    _keys = (BlGdResource,)

    def transform(self, c, node:BlGdResource):

        t = c.existing_object.set(node.properties)
        yield (node.properties,)
        c.existing_object.reset(t)
        props = c.children.get()[0]

        t = c.collection.set(node.ext_resources)
        yield tuple(node.ext_resources.values())
        c.collection.reset(t)
        ext_res = c.children.get()

        t = c.collection.set(node.sub_resources)
        yield tuple(node.sub_resources.values())
        c.collection.reset(t)
        sub_res = c.children.get()

        return PyResourceTres.construct(
            uid=node.uid,
            format=node.format,
            type=node.type,  
            file=node.file,
            script_class=node.script_class,
            properties=props,
            sub_resources=sub_res,
            ext_resources=ext_res,
        )
    

class PyToBl_ResourceTres(PyToBlModule):
    _keys = (PyResourceTres,)

    def transform(self, c, node:PyResourceTres):
        target : BlGdResource = c.existing_object.get()

        for v in node.sub_resources:
            _child = target.sub_resources.add()
            t = c.existing_object.set(_child)
            yield (v,)
            c.existing_object.reset(t)

        for v in node.ext_resources:
            _child = target.ext_resources.add()
            t = c.existing_object.set(_child)
            yield (v,)
            c.existing_object.reset(t)

        t = c.existing_object.set(target.properties)
        yield (node.properties,)
        c.existing_object.reset(t)

        target.uid = node.uid.addr
        target.format = node.format
        target.type = node.type
        target.file = node.file.cached_addr
        target.script_class = node.script_class

        


py_to_bl_ruleset = PyToBlRuleset("PropCol :: STD",(
    PyToBl_ExtResource,
    PyToBl_SubResource,
    PyToBl_ResourceTres,
))

bl_to_py_ruleset = BlToPyRuleset("PropCol :: STD",(
    BlToPy_ExtResource,
    BlToPy_SubResource,
    BlToPy_ResourceTres,
))