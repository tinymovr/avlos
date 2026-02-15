class DummyChannel:
    """
    Dummy channel class.

    Supports a single shared ``value`` (used by legacy tests that inspect
    ``channel.value`` directly) **and** per-endpoint storage so that
    multiple attributes can be written and read back independently.
    """

    def __init__(self, value=0):
        self.value = value
        self.write = False
        self._store = {}

    def send(self, data, ep_id):
        # data == [] is a read request (get_value); only store real writes
        if self.write and data != []:
            self.value = data
            self._store[ep_id] = data

    def recv(self, ep_id):
        if ep_id in self._store:
            return [self._store[ep_id]]
        return [self.value]

    def set_value(self, value):
        self.value = value
        self._store.clear()

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
