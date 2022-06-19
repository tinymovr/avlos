from marshmallow import fields, ValidationError
import pint

_registry = None


def get_registry():
    """
    Get or create a Pint unit registry with custom units
    """
    global _registry
    if not _registry:
        _registry = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
        _registry.define("tick = turn / 8192")
    return _registry


class UnitField(fields.Field):
    """
    Marshmallow Field that serializes to a string
    and deserializes to a Pint unit.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return get_registry().Unit(value)
        except ValueError as error:
            raise ValidationError("Invalid Pint unit.") from error
