from .collection_overlayable import Collection, CollectionKey, CollectionOverlayMode

from typing import Self

class _Item():
    key : CollectionKey[str]
    value : int = 0
    overlay : Self|None=None

    def overlay_copy(self,)->Self:
        r = _Item(self.key)
        r.set_overlay(self)
        return r

    def overlay_local_is_thin(self)->bool:
        if self.overlay is None: 
            return False
        return self.overlay.value != self.value

    def set_overlay(self, item:Self|None)->None:
        self.overlay=item

    def __init__(self, key:str, value:int=0):
        self.key = CollectionKey(self, key)

class Test_Collection():
    ''' test overlay version of collection, desired behavior is match by id and copy-overlay OR passthrough '''

    def test_construction(self):
        C0 = Collection("key", iterable=[], )
        pass

    def test_overlay_copy(self):
        I0 = _Item("string")
        C0 = Collection("key", iterable=[I0],  )

        C1 = Collection("key", mode=CollectionOverlayMode.SUBITEM_OVERLAY_COPY)
        dif = C1.set_overlay(C0)

        assert len(C1) == 1
        assert C1.overlay is C0
        assert not (C1[0] is I0)
        assert (C1["string"].overlay is I0)
        assert dif == {"add":(C1["string"]), "removed":tuple(), "update":tuple()}

    def test_overlay_copy_integrate(self):
        I0 =_Item("string")
        C0 = Collection("key", iterable=[I0], )

        I1 =_Item("string", value=1)
        C1 = Collection("key", iterable=[I1], mode=CollectionOverlayMode.SUBITEM_OVERLAY_COPY)
        dif = C1.set_overlay(C0)

        assert not (C1["string"] is I0)
        assert (C1["string"] is I1)
        assert I1.overlay is I0
        assert dif == {"add":tuple(), "removed":tuple(), "update":tuple()}

    def test_overlay_copy_disintegrate(self):
        I0 =_Item("string")
        C0 = Collection("key", iterable=[I0], )

        I1 =_Item("string", value=1)
        C1 = Collection("key", iterable=[I1], mode=CollectionOverlayMode.SUBITEM_OVERLAY_COPY)
        C1.set_overlay(C0)

        assert I1.overlay is I0
        dif = C1.set_overlay(None)

        assert I1.overlay is None
        
    def test_overlay_passtrough_integrate(self):
        I0 =_Item("string")
        C0 = Collection("key", iterable=[I0], )

        I1 =_Item("string")
        C1 = Collection("key", iterable=[I1], mode=CollectionOverlayMode.SUBITEM_PASSTHROUGH)
        dif = C1.set_overlay(C0)

        assert not (C1["string"] is I0)
        assert (C1["string"] is I1)
        assert I1.overlay is None
        assert dif == {"add":tuple(), "removed":tuple(), "update":tuple()}

    def test_overlay_passtrough_disintegrate(self):
        I0 =_Item("string")
        C0 = Collection("key", iterable=[I0])
        C1 = Collection("key", mode=CollectionOverlayMode.SUBITEM_PASSTHROUGH)
        dif = C1.set_overlay(C0)
        assert dif == {"add":[I0], "removed":tuple(), "update":tuple()}
