from functools import cached_property

class NamedNode:

    def __init__(self, name):
        self._parent = None
        self.name = name

    # this kinda stinks, cause it is implemented elsewhere
    # @cached_property
    # def parent(self):
    #     return self._parent

    @cached_property
    def full_name(self):
        try:
            return "{}.{}".format(self._parent.full_name, self.name)
        except AttributeError:
            return self.name