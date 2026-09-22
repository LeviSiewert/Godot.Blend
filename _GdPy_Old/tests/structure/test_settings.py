
from ...core.settings import (
    ResourceSettings,
    Category,
)

class Test_Category():
    def test_construction(self):
        res = Category.construct(
            name = "catname",
            properties = {
                "A":"A"
            },
        )

        assert res.name == "catname"
        assert res.properties["A"] == "A"


class Test_ResourceSettings():    
    def test_construction(self):
        cat = Category.construct(
            name = "catname",
            properties = {
                "A":"A"
            },
        ),
        res = ResourceSettings.construct(
            cat_resources = [
                cat,
            ],
            properties = {
                "B":"B"
            },
        )
        
        assert res.properties["B"] == "B"
        assert len(res.cat_resources) == 1
        assert res.cat_resources["catname"] is cat
        assert cat.context.resource is res
