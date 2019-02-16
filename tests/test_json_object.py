from json_object import JsonObject


class JsonObjectSubClass(JsonObject):
    pass


class TestJsonObject(object):
    def test_subclass_read(self):
        foo = JsonObjectSubClass(
            {"a": 0, "b": {"bb": 1}, "c": [{"cc": 2}, {"dd": {"ddd": 3}}]}
        )

        assert foo["a"] == 0
        assert foo.a == 0
        assert foo.b.bb == 1
        assert foo.c[0].cc == 2
        assert foo.c[1].dd.ddd == 3
        assert foo.c[0].get("dd") is None

    def test_subclass_iterate(self):
        bar = JsonObjectSubClass([{"a": 1, "b": 1}, {"a": 2, "b": 2}, {"a": 3, "b": 3}])

        for x in bar:
            assert x.a == x.b

        baz = bar[0:2]

        for i in range(len(baz)):
            assert baz[i].a == i + 1

        baz_sorted = sorted(baz, key=lambda e: (e["a"], e["b"]), reverse=True)
        assert baz_sorted[0].a == 2
        assert baz_sorted[1].b == 1

    def test_subclass_write(self):
        foobar = JsonObjectSubClass({})

        foobar.a = 1
        foobar.b = 2
        foobar["c"] = 3

        assert foobar.a == 1
        assert foobar.b == 2
        assert foobar.c == 3
