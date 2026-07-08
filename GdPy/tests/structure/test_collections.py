from __future__ import annotations
from ...core.collections import Collection, Reference, Item, CollectionKey, StructContext

def test():
    class ItemExample(Item):
        # context : StructContext
        def __colkeys__(self,)->tuple[Key]:
            return (self.key_a, self.key_b, self.key_c)

        key_a : ForeignCollectionKey[str, ItemExample] #UNIQuE
        key_b : ForeignCollectionKey[str, ItemExample] #UNIQuE

        key_c : ForeignCollectionKey[str, ItemExample] #SHARED

        def __setup__(self):
            # self.context = StructContext()
            self.key_a = CollectionKey(self, "key_a", None)
            self.key_b = CollectionKey(self, "key_b", None)
            self.key_c = CollectionKey(self, "key_c", None)

        def __init__(self, id:str, a:str, b:str):
            self.__setup__()
            self.identifier = id
            self.key_a.set(a)
            self.key_b.set(b)
            self.key_c.set("key_c://c")
        
        def __repr__(self):
            return f"Item({self.identifier})"

    class CollectionExample(Collection):
        unique_keys = ("key_a","key_b")
        shared_keys = ("key_c",)

    # col = CollectionExample(context = StructContext())
    col = CollectionExample()

    item_a = ItemExample("item_a", "key_a://a", "key_b://a")
    item_b = ItemExample("item_b", "key_a://b", "key_b://b")
    item_c = ItemExample("item_c", "key_a://c", "key_b://c")

    for item in (item_a, item_b, item_c):
        col.append(item)

        key_a = item.key_a.addr
        key_b = item.key_b.addr
        key_c = item.key_c.addr

        assert (col.get(key_a) is item)
        assert (col.get(key_b) is item)
        assert (item in col.get(key_c)) 

        for key_id,key in {
            "key_a" : key_a,
            "key_b" : key_b,
            # "key_c" : key_c, #!!! Pool-References are not yet supported !
        }.items():
            ref_0 = Reference(key_id = key_id, address=key, cached_value=item)
            assert(not ref_0.is_valid())
            col.append_reference(ref_0)
            assert(ref_0.is_valid())
            assert(ref_0.cached_value()==item)

            ref_1 = Reference(key_id = key_id, address=key)
            col.append_reference(ref_1)
            assert(ref_1.is_valid())
            assert(ref_1.cached_value()==item)

            ref_2 = Reference(key_id = key_id, cached_value=item)
            col.append_reference(ref_2)
            assert(ref_2.is_valid())
            assert(ref_2.cached_value()==item)
            assert(ref_2.cached_addr==key)

        assert(item in col.get("key_c://c", "key_c"))
