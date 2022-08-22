from utils import grouping_continuous_int
from common import *

class Field_factory(object):
    def __init__(self, value):
        self.value = self._constructor(value)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

    def to_str(self):
        return self.__str__()

    def _constructor(self):
        raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, Field_factory):
            return self.__class__(self.value + other.value)
        return self.__class__(self.value + other)

    def __mul__(self, other):
        if isinstance(other, Field_factory):
            return self.__class__(self.value * other.value)
        return self.__class__(self.value * other)


class Stripped_str(Field_factory):
    def __str__(self):
        return self.value

    def to_str_with_key(self, key):
        return "{}={}".format(key, self.value)

    def _constructor(self, value):
        return value.strip()


class Natural_number(Field_factory):
    limit = 0
    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def _constructor(self, value):
        if int(value) > self.limit:
            return int(value)
        raise ValueError("This field can define only natural number")


class Positive_integer(Natural_number):
    limit = -1


class Mgt_flag(Field_factory):
    ref_dict = {
        "YES": True,
        "NO": False
    }

    def __str__(self):
        return "YES" if self.value else "NO"

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return self.value

    def __and__(self, other):
        if isinstance(other, Field_factory):
            return self.value & other.value
        return self.value & other

    def __xor__(self, other):
        if isinstance(other, Field_factory):
            return self.value ^  other.value
        return self.value ^ other

    def __or__(self, other):
        if isinstance(other, Field_factory):
            return self.value | other.value
        return self.value | other

    def _constructor(self, value):
        if isinstance(value, str):
            return self.ref_dict[value.strip()]
        elif isinstance(value, int):
            return bool(value)
        elif isinstance(value, bool):
            return value
        raise ValueError("{} not match this Field".format(value))


class Dof_flags(Field_factory):
    def __str__(self):
        return "".join(str(int(x)) for x in self.value)

    def __repr__(self):
        return "Flag[{}]".format(self.__str__())

    def __iter__(self):
        return iter(self.value)

    def _constructor(self, value):
        if isinstance(value, str):
            return self._sequence_to_flags(value.strip())
        return self._sequence_to_flags(value)

    @staticmethod
    def _sequence_to_flags(seq):
        if len(seq) == 6:
            return tuple(bool(x) for x in seq)
        if len(seq) < 6:
            return tuple(True if (x + 1 in seq) else False for x in range(6))
        raise ValueError("{} not match  DoF flag".format(seq))


class Id_list(Field_factory):
    @property
    def grouped_ids(self):
        return grouping_continuous_int(self.value)

    def __str__(self):
        return " ".join([self._list_to_num_expression(x) for x in self.grouped_ids])

    def __repr__(self):
        return "ID[{}]".format(self.__str__())

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, idx):
        return self.value[idx]

    def _constructor(self, value):
        if isinstance(value, int):
            return [value]
        elif isinstance(value, str):
            return self._list_expression_to_ids(value)
        elif hasattr(value, "__iter__"):
            return [int(x) for x in value]
        else:
            raise ValueError("Cannot convert id list.")

    @staticmethod
    def __num_expression_to_ids(text):
        split_by_to = text.split("to")
        start = int(split_by_to[0])
        if split_by_to[1].isdigit():
            end = int(split_by_to[1])
            step = 1
        else:
            split_by_by = split_by_to[1].split("by")
            end = int(split_by_by[0])
            step = int(split_by_by[1])
        return list(range(start, end + 1, step))

    @staticmethod
    def __text_to_ids(text):
        if text.isdigit():
            return [int(text)]
        else:
            return Id_list.__num_expression_to_ids(text)

    @staticmethod
    def _list_expression_to_ids(text):
        splitted = text.split()
        ids = [Id_list.__text_to_ids(x) for x in splitted]
        return sum(ids, [])

    @staticmethod
    def _list_to_num_expression(values):
        if values:
            if len(values) == 1:
                return str(values[0])
            elif len(values) == 2:
                return " ".join(map(str, values))
            else:
                return "{}to{}".format(values[0], values[-1])
        raise ValueError("Not included value.")


class Load_case_dict(Field_factory):
    def __str__(self):
        return ", ".join(["{}, {}".format(k, v) for k, v in self.value.items()])

    def to_str_with_key(self, key):
        return ", ".join(["{}, {}, {}".format(key, k, v) for k, v in self.value.items()])

    def __repr__(self):
        return "LC[{}]".format(
            " ".join(["{}{}".format(k, v) for k, v in self.value.items()])
        )

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, idx):
        return self.value[idx]

    def _constructor(self, value):
        if isinstance(value, dict):
            return value
        elif hasattr(value, "__iter__"):
            names = [x for x in range(0, len(value), 2)]
            factors = [float(x) for x in range(1, len(value), 2)]
            return {k: v for k, v in zip(names, factors)}
        raise ValueError("")


class Index_with_tuple(Field_factory):
    ref_tuple = ()

    def __str__(self):
        return self.ref_tuple[self.value]

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def _constructor(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return self.ref_tuple.index(value.strip())
        raise KeyError("There is not {} in reference.".format(value))


class Element_type(Index_with_tuple):
    ref_tuple = ELEMENT_TYPE_TUPLE


class Direction_type(Index_with_tuple):
    ref_tuple = DIRECTION_TYPE_TUPLE


class Material_type(Index_with_tuple):
    ref_tuple = MATERIAL_TYPE_TUPLE


class Material_sub_type(Index_with_tuple):
    ref_tuple = MATERIAL_SUB_TYPE_TUPLE


class Offset_type(Index_with_tuple):
    ref_tuple = OFFSET_TYPE_TUPLE


class Load_unit_type(Index_with_tuple):
    ref_tuple = LOAD_UNIT_TYPE_TUPLE


class Meter_unit_type(Index_with_tuple):
    ref_tuple = METER_UNIT_TYPE_TUPLE


class Load_case_type(Index_with_tuple):
    ref_tuple = LOAD_CASE_TYPE_TUPLE
