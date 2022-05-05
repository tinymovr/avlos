class DummyChannel:
    """
    Dummy channel class
    """
    def send(self, data, ep_id):
        pass

    def recv(self, ep_id):
        return [0]

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
        return [0]