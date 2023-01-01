import json
import pint
from avlos import get_registry


class AvlosEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, pint.Quantity):
            return str(o)
        else:
            return super().default(o)
