from ...core.collections import Collection, StructContext, CollectionReferenceUnique, CollectionKey


def test():
    class ItemExample():
        context : StructContext

        key_a : CollectionKey[str] #UNIQuE
        key_b : CollectionKey[str] #UNIQuE

        key_c : CollectionKey[str] #SHARED

        def __setup__(self):
            self.context = StructContext()
            self.key_a = CollectionKey(self, "key_a", None)
            self.key_b = CollectionKey(self, "key_b", None)
            self.key_c = CollectionKey(self, "key_c", None)

        def __init__(self, a:str, b:str):
            self.__setup__()
            self.key_a.set(a)
            self.key_b.set(b)
            self.key_c.set("key_c://c")

    class CollectionExample(Collection):
        unique_keys = ("key_a","key_b")
        shared_keys = ("key_c",)

    col = CollectionExample(context = StructContext())

    item_a = ItemExample("key_a://a", "key_b://a")
    item_b = ItemExample("key_a://b", "key_b://b")
    item_c = ItemExample("key_a://c", "key_b://c")

    for item in (item_a,item_b,item_c):
        col.append(item)

        key_a = item.key_a.local_data
        key_b = item.key_b.local_data
        key_c = item.key_c.local_data

        assert (col.get(key_a) is item)
        assert (col.get(key_b) is item)
        assert (item in col.get(key_c)) 

        for key_id,key in {
            "key_a" : key_a,
            "key_b" : key_b,
            "key_c" : key_c,
        }.items():
            ref_0 = CollectionReferenceUnique(key_id = key_id, address=key, cached_value=item)
            assert(not ref_0.is_valid())
            col.append_reference(ref_0)
            assert(ref_0.is_valid())
            assert(ref_0.cached_value()==item)

            ref_1 = CollectionReferenceUnique(key_id = key_id, address=key)
            col.append_reference(ref_1)
            assert(ref_1.is_valid())
            assert(ref_1.cached_value()==item)

            ref_2 = CollectionReferenceUnique(key_id = key_id, cached_value=item)
            col.append_reference(ref_2)
            assert(ref_2.is_valid())
            assert(ref_2.cached_value()==item)
            assert(ref_2.cached_address==key)

        assert(item in col.get("c", key_id="key_c"))
