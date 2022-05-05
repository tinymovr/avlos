from functools import cached_property

class CommNode:

    def __init__(self):
        self._parent = None
        self._channel = None

    @cached_property
    def parent(self):
        return self._parent

    @cached_property
    def channel(self):
        if None != self.parent:
            return self.parent.channel
        return self._channel