import json


class JsonObject(object):
    """enable JavaScript/JSON style dict attribute dot access"""

    __slots__ = ["obj"]

    def __init__(self, obj=None):
        # note: cannot use self.obj = obj
        # because __setattr__ will call __getattr__ as infinite recursion
        # https://stackoverflow.com/questions/16237659
        if obj is None:
            obj = []
        super(JsonObject, self).__setattr__("obj", obj)

    def __len__(self):
        return len(self.obj)

    def __contains__(self, item):
        return item in self.obj

    # note: cannot use __getslice__ since it had been deprecated
    # see https://portingguide.readthedocs.io/en/latest/core-obj-misc.html
    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.step not in (1, None):
                raise ValueError("only step=1 supported")
            ret = self.obj[item.start: item.stop]
        else:
            ret = self.obj.__getitem__(item)

        return self.wrap(ret)

    def __setitem__(self, item, value):
        if isinstance(item, slice):
            if item.step not in (1, None):
                raise ValueError("only step=1 supported")
            self.obj[item.start: item.stop] = value
        else:
            self.obj[item] = value

    def __getattr__(self, item):
        if isinstance(self.obj, dict):
            try:
                v = self.obj[item]
            except KeyError:
                v = self.obj.__getattribute__(item)
        else:
            v = self.obj.__getattribute__(item)

        return self.wrap(v)

    def __setattr__(self, key, value):
        self.obj[key] = value

    def wrap(self, v):
        if isinstance(v, (dict, list)):
            return self.__class__(v)
        else:
            return v

    def __str__(self):
        """convert dict to pretty print string for debug"""
        return json.dumps(self.obj, indent=2, sort_keys=True, default=str)
