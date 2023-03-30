import enum
from marshmallow import fields, ValidationError


class BitmaskField(fields.Field):
    """
    Marshmallow Field that serializes to a string
    and deserializes to a bitmask of flags.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return NotImplementedError

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            assert len(value) > 0
            return enum.IntFlag(attr, value)
        except ValueError as error:
            raise ValidationError("Invalid flags list.") from error
        except AssertionError as error:
            raise ValidationError("Empty flags list.") from error
