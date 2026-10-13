import bpy

from ._test_utils import TransformerDirect
from ....GdPy.core import structure as GdPy
from ...datastruct import NodeGd, SceneGd

def _make_empty(bl_obj:bpy.types.Object, *, type:str, name:str=None, gd_type:str=None, gd_script:str|dict=None, instance=None, instance_editable=None)->tuple[NodeGd,bpy.types.Object]:
    # bl_obj = bpy.data.objects.new(type="EMPTY")
    gd = bl_obj.gd

    if not (name is None):
        gd.name = name
    if not (type is None):
        gd.type = type
    if not (gd_type is None):
        gd.gd_type = gd_type

    if not (instance_editable is None):
        gd.instance_editable = instance_editable

    ## Promise Types:

    if not (gd_script is None):
        if isinstance(gd_script,str):
            gd.script.id = gd_script
            gd.instance.type = "TYPE"
        elif isinstance(gd_script,dict): # Promise
            gd.instance.type = "EXTRES"
            gd.script.id = gd_script["id"]
            gd.script.uid = gd_script["uid"]
            gd.script.path = gd_script["path"]
        else:
            raise TypeError()

    if not (instance is None):
        if isinstance(str):
            gd.instance.type = "EXTRES_DIRECT"
            gd.instance.id = gd_script
            pass
        elif isinstance(dict):
            gd.instance.type = "EXTRES"
            gd.instance.id = instance["id"]
            gd.instance.uid = instance["uid"]
            gd.instance.path = instance["path"]
        elif isinstance(bpy.types.collection):
            bl_obj.instance = instance
        else:
            raise TypeError()

    def cleanup():
        bpy.data.objects.remove(bl_obj)

    return gd, bl_obj, cleanup

class _Mixin_ObjectCompare:
    def bl_bl_compare(self, source:bpy.types.Object, target:bpy.types.Object):
        assert source.__class__ == target.__class__
        
        assert source.gd.name == target.gd.name

        assert source.gd.gd_type == target.gd_type

        assert source.instance == target.instance
        assert source.instance_editable == target.instance_editable

        # If external library:
        if source.library:
            assert target.library
        if source.override_library:
            assert target.override_library
            assert source.override_library.properties == source.override_library.properties 
            
        assert source.gd.gd_script.id == target.gd_script.id
        assert source.gd.gd_script.uid == target.gd_script.uid
        assert source.gd.gd_script.path == target.gd_script.path
        
        assert source.gd.instance.id == target.gd.instance.id
        assert source.gd.instance.uid == target.gd.instance.uid
        assert source.gd.instance.path == target.gd.instance.path

        assert source.gd.properties == target.gd.properties

        # Stored under Collection:
        # unclaimed_extres as empties w/ promise & data. Instances as allowed by env
        # unclaimed_subres as empties w/ fullpath, nanme and data

    def gd_gd_compare(self, source, target):
        assert source == target


class SubResource(TransformerDirect, _Mixin_ObjectCompare):
    ''' SubResources simple, no properties, existing collection w/a 
    '''
    # No existing matching collection for extres referencing.
    def data(self):

        def empty()->bpy.types.Object:
            return bpy.data.objects.new("obj", None)

        ## BASIC CONSTRUCTION: 
        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE")
        gd_obj = GdPy.Resource()
        yield bl_obj, gd_obj
        clean()

        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID")        
        gd_obj = GdPy.Resource(id="ID")
        yield bl_obj, gd_obj
        clean()

        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_type="Resource")        
        gd_obj = GdPy.Resource(id="ID")
        yield bl_obj, gd_obj
        clean()

        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_type="WorldSettings")        
        gd_obj = GdPy.Resource(id="ID", type="WorldSettings")
        yield bl_obj, gd_obj
        clean()


        ## PROMISE FIELD VARIATIONS

        #script local id 
        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_script="script_local_id")        
        gd_obj = GdPy.Resource(id="ID", script="script_local_id")
        yield bl_obj, gd_obj
        clean()

        #script promise
        _script_key = {"id":"_id","uid":"_uid","path":"_path"}
        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_script=_script_key)        
        gd_obj = GdPy.Resource(id="ID", script=GdPy.Promise(key=_script_key, p_type=GdPy.promise.Type.EXTRESOURCE))
        yield bl_obj, gd_obj
        clean()

        #instance local id
        _instance_key = "local_inst_id"
        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", instance=_instance_key)        
        gd_obj = GdPy.Resource(id="ID", instance=_instance_key)
        yield bl_obj, gd_obj
        clean()

        #instance promise
        _instance_key = {"id":"_id","uid":"_uid","path":"_path"}
        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", instance=_instance_key)        
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key=_instance_key, p_type=GdPy.promise.Type.EXTRESOURCE))
        yield bl_obj, gd_obj
        clean()

        #instance promise editable
        _instance_key = {"id":"_id","uid":"_uid","path":"_path"}
        _, bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", instance=_instance_key, instance_editable=True)        
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key=_instance_key, p_type=GdPy.promise.Type.EXTRESOURCE), instance_editable=True)
        yield bl_obj, gd_obj
        clean()


        ## Instance promise fullfilled locally, no overide
        _target_collection = bpy.data.collections.new()
        _target_collection.asset_mark()
        asset_data = _target_collection.asset_data
        asset_data.tags.new("uid://_uid")
        asset_data.tags.new("res://_path")

        _, bl_obj, clean = _make_empty(empty(),type="EXTRESOURCE", name="ID", instance=_target_collection)        
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key={"id":"_id","uid":"_uid","path":"_path"}, p_type=GdPy.promise.Type.EXTRESOURCE))

        yield bl_obj, gd_obj

        _target_collection.asset_clear()
        bpy.data.collections.remove(_target_collection)
        clean()

        ## Instance promise fullfilled nonlocally, with override
        # Utilizing res://path uid://uid tags in local/project asset collection.
        ## TODO SETUP LIBRARY
        _target_collection = bpy ##TODO 
        _, bl_obj, clean = _make_empty(empty(),type="EXTRESOURCE", name="ID", instance=_target_collection)
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key={"id":"_id","uid":"uid","path":"path"}, p_type=GdPy.promise.Type.EXTRESOURCE))
        yield bl_obj, gd_obj
        clean()


# class Node():
#     def data(self):
#         pass

# class Resource():
#     def data(self):
#         pass


# class Scene():
#     def data(self):
#         pass
