import enum
from marshmallow import fields, ValidationError


class EnumField(fields.Field):
    """
    Marshmallow Field that serializes to a string
    and deserializes to an enum.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return NotImplementedError

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            assert len(value) > 0
            return enum.IntEnum(attr, value, start=0)
        except ValueError as error:
            raise ValidationError("Invalid enum list.") from error
        except AssertionError as error:
            raise ValidationError("Empty enum list.") from error
