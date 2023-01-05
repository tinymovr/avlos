from enum import Enum
from marshmallow import fields, ValidationError


class DataType(Enum):
    """
    Enum that represents a datatype. Includes
    various convenience functions
    """

    VOID = 0
    BOOL = 1
    UINT8 = 2
    INT8 = 3
    UINT16 = 4
    INT16 = 5
    UINT32 = 6
    INT32 = 7
    UINT64 = 8
    INT64 = 9
    FLOAT = 10
    DOUBLE = 11
    STR = 12

    @property
    def nickname(self):
        return self.name.lower()

    @property
    def c_name(self):
        return c_type_map[self]

    @property
    def size(self):
        return datatype_sizes[self]

    @property
    def is_void(self):
        return DataType.VOID == self

    def from_string(self, str_value):
        if self == DataType.VOID:
            return None
        else:
            return py_type_map[self](str_value)


c_type_map = {
    DataType.VOID: "void",
    DataType.BOOL: "bool",
    DataType.INT8: "int8_t",
    DataType.UINT8: "uint8_t",
    DataType.INT16: "int16_t",
    DataType.UINT16: "uint16_t",
    DataType.INT32: "int32_t",
    DataType.UINT32: "uint32_t",
    DataType.FLOAT: "float",
    DataType.DOUBLE: "double",
    DataType.STR: "char[]",
}

py_type_map = {
    DataType.VOID: None,
    DataType.BOOL: bool,
    DataType.INT8: int,
    DataType.UINT8: int,
    DataType.INT16: int,
    DataType.UINT16: int,
    DataType.INT32: int,
    DataType.UINT32: int,
    DataType.FLOAT: float,
    DataType.DOUBLE: float,
    DataType.STR: str,
}

datatype_sizes = {
    DataType.VOID: 0,
    DataType.BOOL: 1,
    DataType.INT8: 1,
    DataType.UINT8: 1,
    DataType.INT16: 2,
    DataType.UINT16: 2,
    DataType.INT32: 4,
    DataType.UINT32: 4,
    DataType.FLOAT: 4,
    DataType.DOUBLE: 8,
    DataType.STR: -1,
}


datatype_names = {
    "void": DataType.VOID,
    "bool": DataType.BOOL,
    "int8": DataType.INT8,
    "uint8": DataType.UINT8,
    "int16": DataType.INT16,
    "uint16": DataType.UINT16,
    "int32": DataType.INT32,
    "uint32": DataType.UINT32,
    "float": DataType.FLOAT,
    "double": DataType.DOUBLE,
    "string": DataType.STR,
}


class DataTypeField(fields.Field):
    """
    Marshmallow Field that serializes to a string and
    deserializes to a member of the DataType enum.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        for k, v in datatype_names.iteritems():
            if v == value:
                return k

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return datatype_names[value]
        except KeyError as error:
            raise ValidationError("Invalid DataType.") from error
