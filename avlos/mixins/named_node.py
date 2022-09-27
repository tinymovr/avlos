from functools import cached_property


class NamedNode:
    def __init__(self, name, include_base_name=False):
        self._parent = None
        self.name = name
        self.include_base_name = include_base_name

    # this kinda stinks, cause it is implemented elsewhere
    # @cached_property
    # def parent(self):
    #     return self._parent

    @cached_property
    def full_name(self):
        try:
            return "{}.{}".format(self._parent.full_name, self.name).strip(".")
        except AttributeError:
            if self.include_base_name:
                return self.name
            return ""
