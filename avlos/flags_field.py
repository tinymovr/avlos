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
        print(value)
        try:
            return Flags(value)
        except ValueError as error:
            raise ValidationError("Invalid flags list.") from error


class Flags:

    def __init__(self, flags):
        self.flags = flags

    def match(self, value):
        matches = []
        for i in range(len(self.flags)):
            if bool((1 << i) & value):
                matches.append(self.flags[i])
        return matches

    def mask(self, flags_list):
        value = 0
        for i in range(len(self.flags)):
            if self.flags in flags_list:
                value |= (1 << i)
        return value
