from functools import cached_property


class BaseChannel:
    """
    Base Channel class to be implemented by
    the client.
    """

    def send(self, data, ep_id):
        raise NotImplementedError

    def recv(self, ep_id, timeout=0.1):
        raise NotImplementedError

    @cached_property
    def serializer(self):
        raise NotImplementedError
