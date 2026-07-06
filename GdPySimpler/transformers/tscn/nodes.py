from ._transformer import GdToPyRuleset, GdToPyModule, PyToGdRuleset, PyToGdModule

from ...core.nodes import (
    ResourceScene, 
    Node,
    EditFlag,
    SignalNotation,
)

from ...core.structure import (
    ExtResourceRef,
    )


class GdToPy_ResourceScene(GdToPyModule):
    _keys = ("file_tscn",)
    # def transform(self, c, node):
    #     header_props, ext_resources, sub_resources, node_resources, signals, edit_flags = node.children
        
    #     yield header_props

    #     res = ResourceScene(**c.children.get())
    #     t0 = c.resource.set(res)

    #     yield {
    #         # "properties":properties,
    #         "ext_resources" : ext_resources,
    #         "edit_flags" : edit_flags,
    #     }
        

    #     apply(res,
    #         edit_flags = c.children.get()["edit_flags"],
    #         ext_resources = c.children.get()["ext_resources"],
    #     )

    #     yield {
    #         "sub_resources":sub_resources,
    #         "node_resources":node_resources,
    #         "signals":signals
    #         # "ResourceScene":ResourceScene,
    #     }
    #     contents = c.children.get()
    #     apply(res,
    #         sub_resources = contents["sub_resources"],
    #         node_resources = contents["node_resources"],
    #     )

    #     ## Nodes load deps as required, construction will load all instances of ext scenes, but textures and similar will not be loaded until req
    #     res.construct_node_tree()
    #     res.apply_signals(contents["signals"])

    #     c.resource.reset(t0)
    
    #     return res
    
class PyToGd_ResourceScene(PyToGdModule):
    _keys = (ResourceScene,)



class GdToPy_Node(GdToPyModule):
    _keys = ("node_resource",)
    def transform(self, c, node):
        header_props, _properties = node.children

        yield header_props.children
        header = dict(c.children.get())
        
        instance = None
        if inst_id := header.get("instance",None):
            instance = ExtResourceRef(inst_id)

        res = Node.construct(
            name=header["name"],
            type=header["type"],
            unique_id=header["unique_id"],
            instance=instance,
            #Defered to hooks on collection (better for signal timing, ect.):
            _defered_parent = header.get("parent", None),
            _defered_apply_owner = True,
        )

        t0 = c.sub_resource.set(res)

        yield (_properties,)
        res.properties.update(dict(c.children.get()[0]))

        c.sub_resource.reset(t0)

        return res

class PyToGd_Node(PyToGdModule):
    _keys = (Node,)
    
    def transform(self, c, node:Node):
        yield dict(node.properties)
        _properties : dict[str,str] = c.children.get()
        properties = "\n".join(f"{k} = {v}" for k,v in _properties.items())
        
        _header_props = {
            "type": node.type,
            "name": node.name,
            "parent": node.get_nodepath_local(), 
            "unique_id": node.unique_id.addr,
        }
        if node.instance:
            _header_props["instance"] = node.instance.addr

        _header_props : dict = c.children.get()
        header_props = " ".join(f"{k}={v}" for k,v in _properties.items()) 

        return f"[node {header_props}]" + properties


class GdToPy_EditFlag(GdToPyModule):
    _keys = ("edit_flag",)
    def transform(self, c, node):
        yield node.children
        properties = c.children.get()[0]
        return EditFlag(**properties)

class PyToGd_EditFlag(PyToGdModule):
    _keys = (EditFlag,)
    def transform(self, c, node:EditFlag):
        yield (node.path,)
        path = c.children.get()[0]
        return f'[editable path={path}]'
    

class GdToPy_SignalNotation(GdToPyModule):
    _keys = ("signal",)
    def transform(self, c, node):
        yield node.children
        properties = c.children.get()[0]
        return SignalNotation(
            signal = properties["signal"],
            method = properties["method"],
            fr = properties["from"],
            to = properties["to"]
        )
class PyToGd_SignalNotation(PyToGdModule):
    _keys = (SignalNotation,)
    def transform(self, c, node):
        yield {
            "signal" : node.signal,
            "fr" : node.fr.addr,
            "to" : node.to.addr,
            "method" : node.method,
        }
        d = c.children.get()
        return f"[connection signal={d["signal"]} from={d["fr"]} to={d["to"]} method={d["method"]}]"

gd_to_py_ruleset = GdToPyRuleset("STD_Nodes", [
    GdToPy_ResourceScene,
    GdToPy_Node,
    GdToPy_EditFlag,
    GdToPy_SignalNotation,
])

py_to_gd_ruleset = PyToGdRuleset("STD_Nodes", [
    PyToGd_ResourceScene,
    PyToGd_Node,
    PyToGd_EditFlag,
    PyToGd_SignalNotation,
])