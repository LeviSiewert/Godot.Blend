import bpy

from ._test_utils import TransformerDirect
from ....GdPy.core import structure as GdPy
from ...structure import NodeGd, SceneGd

def _make_empty(bl_obj:bpy.types.Object, *, type:str, name:str=None, gd_type:str=None, gd_script:str|dict=None, instance=None, instance_editable=None, children:tuple[bpy.types.Object]=tuple())->tuple[NodeGd,bpy.types.Object]:
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

    for x in children:
        x.parent = bl_obj

    def cleanup():
        bpy.data.objects.remove(bl_obj)
        for x in children:
            bpy.data.objects.remove(x)

    return bl_obj, cleanup

def _make_resource(_obj, uid:str, res:str, **kwargs):
    col = bpy.data.collections.new()
    col.gd.uid = uid 
    col.gd.path = res

    obj, obj_clean = _make_empty(_obj, **kwargs)
    col.gd.root = obj

    col.asset_mark()
    col.asset_data.tags.new("uid://"+uid)
    col.asset_data.tags.new("res://"+res)

    def cleanup():
        obj_clean()
        bpy.data.collections.remove(col)

    return col, cleanup
    
    

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

class _Mixin_CollectionCompare(_Mixin_ObjectCompare):
    def bl_bl_compare(self, source:bpy.types.Collection, target:bpy.types.Collection):
        assert source.__class__ == target.__class__
        
        assert source.gd.uid == target.gd.uid
        assert source.gd.path == target.gd.path
        assert source.gd.unclaimed_extres == target.gd.unclaimed_extres #  as empties w/ promise & data. Instances as allowed by env
        assert source.gd.unclaimed_subres == target.gd.unclaimed_subres #  as empties w/ fullpath, nanme and data

        assert source.asset_data.tags == target.asset_data.tags

        super().bl_bl_ccompare(source.gd.root, target.gd.root)


class SubResource(TransformerDirect, _Mixin_ObjectCompare):
    ''' SubResources simple, no properties, existing collection w/a 
    '''
    # No existing matching collection for extres referencing.
    def data(self):

        def empty()->bpy.types.Object:
            return bpy.data.objects.new("obj", None)

        ## BASIC CONSTRUCTION: 
        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE")
        gd_obj = GdPy.Resource()
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID")        
        gd_obj = GdPy.Resource(id="ID")
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_type="Resource")        
        gd_obj = GdPy.Resource(id="ID")
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_type="WorldSettings")        
        gd_obj = GdPy.Resource(id="ID", type="WorldSettings")
        yield bl_obj, gd_obj
        clean()


        ## PROMISE FIELD VARIATIONS

        #script local id 
        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_script="script_local_id")        
        gd_obj = GdPy.Resource(id="ID", script="script_local_id")
        yield bl_obj, gd_obj
        clean()

        #script promise
        _script_key = {"id":"_id","uid":"_uid","path":"_path"}
        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", gd_script=_script_key)        
        gd_obj = GdPy.Resource(id="ID", script=GdPy.Promise(key=_script_key, p_type=GdPy.promise.Type.EXTRESOURCE))
        yield bl_obj, gd_obj
        clean()

        #instance local id
        _instance_key = "local_inst_id"
        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", instance=_instance_key)        
        gd_obj = GdPy.Resource(id="ID", instance=_instance_key)
        yield bl_obj, gd_obj
        clean()

        #instance promise
        _instance_key = {"id":"_id","uid":"_uid","path":"_path"}
        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", instance=_instance_key)        
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key=_instance_key, p_type=GdPy.promise.Type.EXTRESOURCE))
        yield bl_obj, gd_obj
        clean()

        #instance promise editable
        _instance_key = {"id":"_id","uid":"_uid","path":"_path"}
        bl_obj, clean = _make_empty(empty(),type="SUBRESOURCE", name="ID", instance=_instance_key, instance_editable=True)        
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key=_instance_key, p_type=GdPy.promise.Type.EXTRESOURCE), instance_editable=True)
        yield bl_obj, gd_obj
        clean()


        ## Instance promise fullfilled locally, no overide
        _target_collection = bpy.data.collections.new()
        _target_collection.asset_mark()
        asset_data = _target_collection.asset_data
        asset_data.tags.new("uid://_uid")
        asset_data.tags.new("res://_path")

        bl_obj, clean = _make_empty(empty(),type="EXTRESOURCE", name="ID", instance=_target_collection)        
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key={"id":"_id","uid":"_uid","path":"_path"}, p_type=GdPy.promise.Type.EXTRESOURCE))

        yield bl_obj, gd_obj

        _target_collection.asset_clear()
        bpy.data.collections.remove(_target_collection)
        clean()

        ## Instance promise fullfilled nonlocally, with override
        # Utilizing res://path uid://uid tags in local/project asset collection.
        ## TODO SETUP LIBRARY
        _target_collection = bpy ##TODO 
        bl_obj, clean = _make_empty(empty(),type="EXTRESOURCE", name="ID", instance=_target_collection)
        gd_obj = GdPy.Resource(id="ID", instance=GdPy.Promise(key={"id":"_id","uid":"uid","path":"path"}, p_type=GdPy.promise.Type.EXTRESOURCE))
        yield bl_obj, gd_obj
        clean()

class Resource(TransformerDirect, _Mixin_CollectionCompare):
    def data(self):
        def make(**kwargs):
            return _make_resource(bpy.data.objects.new("",None), "RESOURCE", res="_res", uid="_uid", **kwargs)

        ## Basic structure

        bl_obj, clean = make()
        gd_obj = GdPy.Resource(uid="_uid", file="_res")
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = make(type="SUBRESOURCE")
        gd_obj = GdPy.Resource(uid="_uid", file="_res")
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = make(name="ID")
        gd_obj = GdPy.Resource(uid="_uid", file="_res", id="ID")
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = make(gd_type="WorldSettings")
        gd_obj = GdPy.Resource(uid="_uid", file="_res", type="WorldSettings")
        yield bl_obj, gd_obj
        clean()

        bl_obj, clean = make(gd_script="_script_uid")
        gd_obj = GdPy.Resource(uid="_uid", file="_res", script="_script_uid")
        yield bl_obj, gd_obj
        clean()

        ## Promise vs instance test cases handled by SubResource tests.
        
        ## STRUCTURE:

        # Depth 1:
        bl_obj, clean = make(gd_script="_script_uid")
        bl_subres = _make_empty(bpy.types.Object(), name="subres")
        bl_obj.objects.link(bl_subres)
        bl_obj.properties["ref"] = bl_subres

        gd_obj = GdPy.Resource(uid="_uid", file="_res", script="_script_uid", 
            properties={
                "ref" : GdPy.Resource(id="subres"), 
        })
        
        yield bl_obj, gd_obj

        bpy.data.objects.remove(bl_subres)
        clean()

        # Depth 2:
        bl_obj, clean = make(gd_script="_script_uid")

        bl_subres_a = _make_empty(bpy.types.Object(), name="subres_a")
        bl_obj.objects.link(bl_subres_a)
        bl_obj.gd.root.properties["ref"] = bl_subres_a

        bl_subres_b = _make_empty(bpy.types.Object(), name="subres_b")
        bl_obj.objects.link(bl_subres_b)
        bl_subres_b.properties["ref"] = bl_subres_b

        gd_obj = GdPy.Resource(uid="_uid", file="_res", script="_script_uid", 
            properties={
                "ref":GdPy.Resource(id="subres_a", properties = {
                    "ref":GdPy.Resource(id="subres_b")
                }), 
        })
        
        yield bl_obj, gd_obj

        bpy.data.objects.remove(bl_subres)
        clean()


        ## unused subres
        bl_obj, clean = make(gd_script="_script_uid")
        bl_subres = _make_empty(id="id")
        bl_obj.objects.link(bl_subres)
        _e = bl_obj.gd.unclaimed_subres.new()
        _e.node = bl_subres

        gd_obj = GdPy.Resource(uid="_uid", file="_res", script="_script_uid", 
            unclaimed_subres=[
                GdPy.Resource(id="id")
            ], 
        )

        yield bl_obj, gd_obj
        bpy.data.objects.remove(bl_subres)
        clean()

        ## unused extres
        bl_obj, clean = make(gd_script="_script_uid")
        bl_subres = _make_empty(id="id")
        bl_obj.objects.link(bl_subres)
        _e = bl_obj.gd.unclaimed_extres.new()
        _e.type = "EXTRESOURCE"
        _e.id = "_id"
        _e.uid = "_uid"
        _e.res = "_res"
       
        gd_obj = GdPy.Resource(uid="_uid", file="_res", script="_script_uid", 
            unclaimed_extres=[
                GdPy.Promise(key={"uid":"_uid", "id":"_id", "path":"_res"}, p_type=GdPy.Promise.Type.EXTRESOURCE),
            ], 
        )

        yield bl_obj, gd_obj
        bpy.data.objects.remove(bl_subres)
        clean()


# class Node():
#     def data(self):
#         pass


class Scene():
    def data(self):

        def node(**kwargs)->bpy.types.Object:
            bl_obj, _ = _make_empty(bpy.data.objects.new("obj", None), type="NODE", gd_type="Node", **kwargs)
            return bl_obj

        def make_scene(**kwargs):
            return _make_resource(bpy.data.objects.new("",None), "SCENE" , res="_res", uid="_uid", **kwargs)

        

        bl_obj, clean = make_scene(
            name = "Root",
            children = [
                node(name="Node")
            ]
        )

        gd_obj = GdPy.Node(uid="_uid", file="_res", 
            children = [
                GdPy.Node(name="Node")
            ]
        )

        yield bl_obj, gd_obj 
        clean()


        ## TODO: MORE!!!
        # - depth 2 structure
        # - Instance
        # - Instance Override



