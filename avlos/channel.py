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
        Arguments:
            data: a bytearray containing the data to
                  be sent
            ep_id: an integer representing the endpoint
                   ID to send to
        """
        raise NotImplementedError

    def recv(self, ep_id, timeout=0.1):
        """
        Receive data from endpoint ep_id. Implement this
        to receive data from endpoint with id ep_id. The
        implementation should timeout after a period equal
        to timeout has elapsed.
        Arguments:
            ep_id: an integer representing the endpoint ID
                   to listen to for data
            timeout: an integer indicating a timeout for
                     receiving any data
        Returns:
            A bytearray containing the received data
        """
        raise NotImplementedError

    @cached_property
    def max_ep_id(self):
        """
        Get the max value that the endpoint can get for
        this channel.
        Returns:
            An integer representing the max endpoint ID
            value
        """
        raise NotImplementedError

    @cached_property
    def max_packet_size(self):
        """
        Get the max size in bytes of the packet that this
        channel can transmit/receive.
        Returns:
            An integer representing the max packet size
        """
        raise NotImplementedError

    @cached_property
    def serializer(self):
        """
        Return a data codec appropriate for this channel.
        Returns:
            The data codec instance
        """
        raise NotImplementedError
