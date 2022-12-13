class DummyChannel:
    """
    Dummy channel class
    """

    def __init__(self, value=0):
        self.value = value
        self.write = False

    def send(self, data, ep_id):
        if self.write:
            self.value = data

    def recv(self, ep_id):
        return [self.value]

    def set_value(self, value):
        self.value = value

    def write_on(self):
        self.write = True

    def write_off(self):
        self.write = False

    @property
    def serializer(self):
        return DummyCodec()


class DummyCodec:
    """
    Dummy CODEC class
    """

    def serialize(self, values, *args):
        return values[0]

    def deserialize(self, data, *args):
        return data
