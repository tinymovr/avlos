from sys import flags
from marshmallow import fields, ValidationError


class FlagsField(fields.Field):
    """
    Marshmallow Field that serializes to a string
    and deserializes to a bitmask of flags.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return " ".join(value.flag_list)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            assert(len(value) > 0)
            return Flags(value)
        except ValueError as error:
            raise ValidationError("Invalid flags list.") from error
        except AssertionError as error:
            raise ValidationError("Empty flags list.") from error


class Flags:

    def __init__(self, flags, default="NONE"):
        self.flags = flags
        self.default = default

    def match(self, value):
        matches = []
        for i in range(len(self.flags)):
            if bool((1 << i) & value):
                matches.append(self.flags[i])
        if 0 == len(matches) and None != self.default:
            return [self.default]
        return matches

    def mask(self, flags_list):
        value = 0
        for i in range(len(self.flags)):
            if self.flags[i] in flags_list:
                value |= (1 << i)
        return value

    def __iter__(self):
        return self.flags.__iter__()
