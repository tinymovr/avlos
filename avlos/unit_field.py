
from marshmallow import fields, ValidationError
import pint 
ureg = pint.UnitRegistry()


class UnitField(fields.Field):
    """Field that serializes to a string and deserializes
    to a Pint unit.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return ureg(value)
        except ValueError as error:
            raise ValidationError("Invalid Pint unit.") from error
