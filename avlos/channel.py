from functools import cached_property


class BaseChannel:
    """
    Base Channel class to be implemented by
    the client.
    """

    def send(self, data, ep_id):
        """
        Send data to endpoint ep_id. Implement this to
        send data contained in the data byte array, to
        the endpoint with id ep_id
        """
        raise NotImplementedError

    def recv(self, ep_id, timeout=0.1):
        """
        Receive data from endpoint ep_id. Implement this
        to receive data from endpoint with id ep_id. The
        implementation should timeout after a period equal
        to timeout has elapsed.
        """
        raise NotImplementedError

    @cached_property
    def max_ep_id(self):
        """
        Max value that the endpoint can get for this channel.
        """
        raise NotImplementedError

    @cached_property
    def serializer(self):
        """
        Return a data codec appropriate for the channel.
        """
        raise NotImplementedError
