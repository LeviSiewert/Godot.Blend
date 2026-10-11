from contextvars import ContextVar

from ._transformer import (
    GdToBl_Transformer, 
    GdToBl_TransformerSet, 
    GdToBl_TransformerOptions, 
    BlToGd_Transformer, 
    BlToGd_TransformerSet, 
    BlToGd_TransformerOptions, 
    TRANSFORM_CHILDREN,
    TRANSFORM,
)

from ....GdPy.core.structure import (
    Properties as PyProperties,
    Promise as PyPromise,
    Node as PyNode,
    Resource as PyResource,
    File as PyFile,
)

from ....GdPy.core.values import (
    NodePath as PyNodePath,
    StringName as PyStringName,
    Object as PyObject,
    Dictionary as PyDictionary,
    Array as PyArray,
    Vector2i as PyVector2i,
    Vector3i as PyVector3i,
    Vector4i as PyVector4i,
    Rect2i as PyRect2i,
    Vector2 as PyVector2,
    Vector3 as PyVector3,
    Vector4 as PyVector4,
    Rect2 as PyRect2,
    Plane as PyPlane,
    Color as PyColor,
    AABB as PyAABB,
    Quaternion as PyQuaternion,
    Transform2D as PyTransform2D,
    Transform3D as PyTransform3D,
    Basis as PyBasis,
    PackedInt32Array as PyPackedInt32Array,
    PackedInt64Array as PyPackedInt64Array,
    PackedFloat32Array as PyPackedFloat32Array,
    PackedFloat64Array as PyPackedFloat64Array,
    PackedStringArray as PyPackedStringArray,
    PackedVector2Array as PyPackedVector2Array,
    PackedVector3Array as PyPackedVector3Array,
    PackedVector4Array as PyPackedVector4Array,
    PackedColorArray as PyPackedColorArray,
    PackedByteArray as PyPackedByteArray,
)

from ...core.property_collection import (
    GdDictionary as BlGdDictionary,
    GdArray as BlGdArray,
    GdPrimitive as BlGdPrimitive,
    GdVector as BlGdVector,
    GdReference as BlGdReference,
    GdPropertyCollection as BlGdPropertyCollection,
)

from ...core.primitives.pointer_collection import (
    BlPointerDictionaryWrapper as BlDictionaryWrapper,
    BlPointerArrayWrapper as BlArrayWrapper,
    BlPointerDictionaryItemWrapper as BlDictionaryItemWrapper,
    BlPointerArrayItemWrapper as BlArrayItemWrapper,
    BlPointerArrayItem as BlArrayItem,
)




## TYPES ## 

### SIMPLE ### 
class GdToBl_Primitive(GdToBl_Transformer):
    _keys = (PyNodePath, PyStringName, str, int, float, bool, None)
    contextual = False
    memoized = False
    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()
        obj, ptr = propcol.store_value(val=node, bin_id="bin_primitive")
        return ptr
    
class BlToGd_Primitive(BlToGd_Transformer):
    _keys = (BlGdPrimitive,)
    _subtype_map = {"NodePath": PyNodePath, "StringName" : PyStringName}
    contextual = False
    memoized = False
    def transform(self, c, node:BlGdPrimitive):
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value)
        return node.value

class GdToBl_Vector(GdToBl_Transformer):
    _keys = (PyVector2, PyVector3, PyVector4, PyRect2, PyPlane, PyColor, PyAABB, PyQuaternion, PyBasis, PyTransform2D, PyTransform3D, PyVector2i, PyVector3i,PyVector4i, PyRect2i)
    contextual = False
    memoized = False
    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()
        obj, ptr = propcol.store_value(val=node, bin_id="bin_vector")
        return ptr

class BlToGd_Vector(BlToGd_Transformer):
    _keys = (BlGdVector,)
    _subtype_map = {x.__class__.__name__:x for x in GdToBl_Vector._keys}
    contextual = False
    memoized = False
    def transform(self, session, node):
        if cls := self._subtype_map.get(node.subtype, None):
            return cls(node.value)
        return node.value

## COMPLEX ## 

class Macros:
    @staticmethod
    def transform_kv_generator(gen):
        res = {}
        for k,v in gen:
            _k,_v = yield TRANSFORM_CHILDREN([k,v]) 
            res[_k] = v
        return res

class GdToBl_Dictionary(GdToBl_Transformer):
    _keys = (dict, PyDictionary, PyObject,)
    contextual = False
    memoized = False

    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()

        obj, ptr = propcol.store_value(bin_id="bin_dict", wrap=True)
        obj : BlDictionaryWrapper
        children = yield from Macros.transform_kv_generator(node.items())
        ## All GdToBl_Properties::Transformers return pointers to the local value

        for k,v in children.items():
            e = obj.items.new()
            e.val_ptr = k
            e.key_ptr = v

        if isinstance(obj, PyObject):
            obj.objtype = node.type
        else:             
            obj.typing = yield TRANSFORM(node.typing)
            
        return ptr

class BlToGd_Dictionary(BlToGd_Transformer):
    _keys = (BlDictionaryWrapper)
    contextual = False
    memoized = False

    def transform(self, session, node:BlDictionaryWrapper):
        src : BlGdDictionary = node.data
        items = yield from Macros.transform_kv_generator(node.items())

        if not (src.objtype == ""):
            return PyObject(src.objtype, **items)
        
        typing = yield TRANSFORM(src.typing)
        return PyDictionary(items, typing=typing)

    
class GdToBl_Array(GdToBl_Transformer):
    _keys = (PyArray, PyPackedInt32Array, PyPackedInt64Array, PyPackedFloat32Array, PyPackedFloat64Array, PyPackedStringArray, PyPackedVector2Array, PyPackedVector3Array, PyPackedVector4Array, PyPackedColorArray, PyPackedByteArray, )
    contextual = False
    memoized = False

    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()

        obj, ptr = propcol.store_value(bin_id="bin_array", wrap=True)
        obj : BlArrayWrapper

        children = TRANSFORM_CHILDREN(node.__iter__(), as_generator=True)
        for v in children:
            e = obj.items.new()
            e: BlArrayItem
            e.ptr = v

        obj.src.typing = typing
        typing = yield TRANSFORM(node.typing)
            
        return ptr


class BlToGd_Array(BlToGd_Transformer):
    _keys = (BlArrayWrapper, )
    contextual = False
    memoized = False

    def transform(self, session, node:BlArrayWrapper):
        src = node.data
        typing = yield TRANSFORM(src.typing)

        children = yield TRANSFORM_CHILDREN(node.values())
        return PyArray(*children, typing=typing)


## OBJECT REFS ##

class GdToBl_Reference(GdToBl_Transformer):
    _keys = (PyPromise, PyResource, PyNode, PyFile)
    contextual = False
    memoized = False

    def match(self, session, node):
        return any([
            isinstance(node, PyPromise),
            isinstance(node, PyResource),
            isinstance(node, PyFile),
        ])

    def transform(self, session, node):
        propcol : BlGdPropertyCollection = session.options["properties"].bl_property_structure.get()

        if isinstance(node, PyPromise):
            res = yield from self.transform_PyPromise(session, node, propcol)
            return res
        elif isinstance(node, PyResource):
            res = yield from self.transform_PyResource(session, node, propcol)
            return res
        elif isinstance(node, PyFile):
            res = yield from self.transform_PyFile(session, node, propcol)
            return res
        raise TypeError(node)

    def transform_PyPromise(self, session, node:PyPromise, propcol:BlGdPropertyCollection):
        ''' Convert object rep to str promise, *or* reference w/a '''

        session.promises.declare(node)

        obj, ptr = propcol.store_value("",bin_id="bin_reference")
        obj : BlGdReference
        obj.ptr_type = node.p_type

        match node.p_type:
            case PyPromise.Type.FILE:
                obj.addr_filepath = node.key 
            case _:
                obj.addr_resource = node.key 


        def callback():
            ''' Callback for formatting the reference with additional information and references w/a '''
            match node.p_type:
                case PyPromise.Type.EXT_RESOURCE:
                    raise NotImplementedError()
                case PyPromise.Type.SUB_RESOURCE:
                    raise NotImplementedError()
                case PyPromise.Type.RESOURCE:
                    raise NotImplementedError()
                case PyPromise.Type.FILE:
                    raise NotImplementedError()
                case PyPromise.Type.EXT_RESOURCE_DIRECT:
                    raise NotImplementedError()

        session.reference_callbacks.append(callback)

        return ptr

    def transform_PyResource(self, session, node:PyResource, propcol:BlGdPropertyCollection):
        ''' Convert object rep to str promise, *or* reference w/a '''
        # assert node.uid or node.file

        if node.uid or node.file:
            obj, ptr = propcol.store_value("",bin_id="bin_reference")
            
            _target = yield TRANSFORM(node)

            obj : BlGdReference

            obj.ptr_type = "EXT_RESOURCE"
            if node.uid:
                obj.addr_resource = node.uid
            if node.file:
                obj.addr_filepath = node.file

            if isinstance(node,PyNode):
                obj.gdtype = "Scene"
            else:
                obj.gdtype = "Resource"
            return ptr

        elif isinstance(node,PyNode):
            _target = yield TRANSFORM(node) ## Memoized, OOPs should mean that we have an actual object

            obj, ptr = propcol.store_value("", bin_id="bin_primitive")
            obj : BlGdPrimitive
            obj.subtype = "NodePath"
            obj.val_nodepath = session.options["structure"].node.get().get_path(node.name)
            return ptr

        elif isinstance(node,PyResource):
            _target = yield TRANSFORM(node) ## Memoized

            obj, ptr = propcol.store_value("",bin_id="bin_reference")
            obj.ptr_type = "SUB_RESOUCE"
            obj.addr_resource  = node.name
            return ptr

        raise Exception()


    def transform_PyFile(self, session, node:PyFile, propcol:BlGdPropertyCollection):
        ''' Convert object rep to str promise, *or* reference w/a '''

        _target = yield TRANSFORM(node) 
        ## Memoized, may or may not be localize?
        ## consider macro for implimenting central incorperation options?

        obj, ptr = propcol.store_value("",bin_id="bin_reference")
        obj.ptr_type = "FILE"
        obj.addr_filepath = node.path

        return ptr

        
class BlToGd_Reference(BlToGd_Transformer):
    _keys = (BlGdReference,)
    _subtype_map = {x.__class__.__name__:x for x in GdToBl_Reference._keys}
    contextual = False
    memoized = False
    def transform(self, session, node:BlGdReference):
        '''For simplicity, all but references are promises going outwards. Structure will accomidate at earliest if/a via signals.'''

        match node.ptr_type:
            case PyPromise.Type.SUB_RESOURCE:
                return PyPromise(node.addr_resource, p_type=node.ptr_type)
            case PyPromise.Type.RESOURCE:
                return PyPromise(node.addr_resource, p_type=node.ptr_type)
            case PyPromise.Type.FILE:
                return PyPromise(node.addr_filepath, p_type=node.ptr_type)
            case PyPromise.Type.EXT_RESOURCE:
                return PyPromise({"path":node.addr_filepath, "uid":node.addr_resource}, p_type=node.ptr_type)
            case PyPromise.Type.EXT_RESOURCE_DIRECT:
                return PyPromise(node.addr_resource, p_type=node.ptr_type)

PROPCOL_gd_to_bl = GdToBl_TransformerSet("Properties::SUBMODE", [
    GdToBl_Primitive,
    GdToBl_Vector,
    GdToBl_Reference,
    GdToBl_Dictionary,
    GdToBl_Array,
    # GdToBl_PropertyCollection,
])
PROPCOL_bl_to_gd = BlToGd_TransformerSet("Properties::SUBMODE", [
    BlToGd_Primitive,
    BlToGd_Vector,
    BlToGd_Reference,
    BlToGd_Dictionary,
    BlToGd_Array,
    # BlToGd_PropertyCollection,
])



## OPTIONS ##

class GdToBl_Options(GdToBl_TransformerOptions):
    bl_property_structure : ContextVar[BlGdPropertyCollection]
    def __init__(self, session):
        self.bl_property_structure = ContextVar("")

class BlToGd_Options(BlToGd_TransformerOptions):
    bl_property_structure : ContextVar[BlGdPropertyCollection] = False
    def __init__(self, session):
        self.bl_property_structure = ContextVar("")

## CORE ## 

class GdToBl_PropertyCollection(GdToBl_Transformer):
    _keys = (PyProperties,)
    contextual = True
    memoized = False
    def transform(self, session, node:PyProperties):
        assert session.options["properties"].gd_property_collection.get()

        t = session.options["properties"].original_transformer_sets.set(session.transformer_sets)
        t1 = session.transformer_sets.set(PROPCOL_bl_to_gd)

        res = yield from Macros.transform_kv_generator(node.items())

        t = session.options["properties"].original_transformer_sets.reset(t)
        session.transformer_sets.reset(t1)

        return session.options["properties"].gd_property_collection.get()

class BlToGd_PropertyCollection(BlToGd_Transformer):
    _keys = (BlGdPropertyCollection,)
    contextual = True
    memoized = False
    def transform(self, session, node:BlGdPropertyCollection):
        res = yield from Macros.transform_kv_generator(node.items())
        return PyProperties(res)


## GROUPINGS ##
PROPCOL_gd_to_bl = GdToBl_TransformerSet("Properties", [
    GdToBl_PropertyCollection
],
options={
    "properties":GdToBl_Options,
})

PROPCOL_bl_to_gd = BlToGd_TransformerSet("Properties", [
    BlToGd_PropertyCollection
],
options={
    "properties":BlToGd_Options,
})
