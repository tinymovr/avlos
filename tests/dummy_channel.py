class DummyChannel:
    """
    Dummy channel class
    """

    def __init__(self, value=0):
        self.value = value

    def send(self, data, ep_id):
        pass

    def recv(self, ep_id):
        return [self.value]

    def set_value(self, value):
        self.value = value

    @property
    def serializer(self):
        return DummyCodec()


class DummyCodec:
    """
    Dummy CODEC class
    """

    def serialize(self, values, *args):
        pass

    def deserialize(self, data, *args):
        return data
