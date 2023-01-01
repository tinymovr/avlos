from functools import cached_property


class CommNode:
    def __init__(self):
        self._parent = None
        self._channel = None

    @cached_property
    def parent(self):
        return self._parent

    @cached_property
    def root(self):
        return self._parent.root

    @cached_property
    def channel(self):
        try:
            return self.parent.channel
        except AttributeError:
            return self._channel

    def set_channel(self, channel):
        self._channel = channel
