from utils import grouping_values_by_index
from fields import Keyword
from datasets import (
    Unit,
    Version,
    Node,
    Line_element,
    Plate_element,
    Constraint,
    Frame_rls,
    DB_material,
    Isotropic_material,
    Orthotropic_material,
    DB_section,
    Shaped_section,
    Thickness,
    Static_load_case,
    Load_to_mass,
    Selfweight,
    Concentrated_load,
    Beam_load,
    Pressure,
    Nodal_temperature,
    Element_temperature,
    Nodal_body_force,
    Load_combination
)
from fields import Element_type, Positive_integer

class Block_base(object):
    item_type = None
    key = ""

    def __init__(self, items):
        self.items = self._constructor(items)

    def __repr__(self):
        return "<{}:{}items>".format(self.key, len(self.items))

    def __str__(self):
        return "\n".join(self.to_lines())

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.items + other.items)
        raise ValueError("Not match class.")

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def _constructor(self, items):
        raise NotImplementedError

    @property
    def header(self):
        return ["*" + self.key]

    def to_lines(self):
        return self.header + [x.to_line() for x in self.items]

    @classmethod
    def from_lines(cls, lines):
        NotImplementedError


class Fixed_length_block(Block_base):
    line_num = 1

    def _constructor(self, items):
        return items

    @classmethod
    def from_lines(cls, lines):
        if cls.line_num == 1:
            items = [cls.item_type.from_line(x) for x in lines]
            return cls(items)
        elif cls.line_num >= 2:
            grouped = grouping_values_by_index(lines, lambda x: x // cls.line_num)
            items = [cls.item_type.from_line(x) for x in grouped]
            return cls(items)
        raise ValueError


class Singleline_block(Fixed_length_block):
    def _constructor(self, items):
        if isinstance(items, self.item_type):
            return [items]
        if len(items) >= 2:
            raise ValueError("This block can have only 1 dataset.")
        return items


class Mapping_block(Block_base):
    def _constructor(self, items):
        return {x.id: x for x in items}

    def to_lines(self):
        return self.header + [x.to_line() for x in self.items.values()]

    @classmethod
    def from_lines(cls, lines):
        items = [cls.item_type.from_line(x) for x in lines]
        return cls(items)


class Multitype_block(Block_base):
    item_type = None
    key_index = None
    key_type = None

    @classmethod
    def from_lines(cls, lines):
        items = [
            cls.create_instance_by_key(
                cls.key_type(cls.extract_key(x)), x
            ) for x in lines
        ]
        return cls(items)

    @classmethod
    def extract_key(cls, line):
        return line.split(",")[cls.key_index]

    @staticmethod
    def create_instance_by_key(key, line):
        raise NotImplementedError


class Multitype_mapping_block(Multitype_block):
    def _constructor(self, items):
        return {x.id: x for x in items}

    def to_lines(self):
        return self.header + [x.to_line() for x in self.items.values()]


class Block_in_block(Block_base):
    item_type = None
    key_index = 0
    key_type = Keyword

    def to_lines(self):
        return self.header + sum([x.to_lines() for x in self.items], [])

#     @classmethod
#     def from_lines(self):



class bUnit(Singleline_block):
    item_type = Unit
    key = "UNIT"


class bVersion(Singleline_block):
    item_type = Version
    key = "VERSION"


class Nodes(Mapping_block):
    item_type = Node
    key = "NODE"


class Elements(Multitype_mapping_block):
    key = "ELEMENT"
    key_index = 1
    key_type = Element_type

    @staticmethod
    def create_instance_by_key(key, line):
        if int(key) < 2:
            return Line_element.from_line(line)
        elif int(key) == 4:
            return Plate_element.from_line(line)
        raise TypeError("{} is not supported type".format(key))


class Constraints(Fixed_length_block):
    item_type = Constraint
    line_num = 1
    key = "CONSTRAINT"


class Frame_rlses(Fixed_length_block):
    item_type = Frame_rls
    line_num = 2
    key = "FRAME-RLS"


class Materials(Multitype_mapping_block):
    key = "MATERIAL"
    key_index = 9
    key_type = Positive_integer

    @staticmethod
    def create_instance_by_key(key, line):
        if int(key) == 1:
            return DB_material.from_line(line)
        elif int(key) == 2:
            return Isotropic_material.from_line(line)
        elif int(key) == 3:
            return Orthotropic_material.from_line(line)


class Sections(Multitype_mapping_block):
    key = "SECTION"
    key_index = 13
    key_type = Positive_integer

    @staticmethod
    def create_instance_by_key(key, line):
        if int(key) == 1:
            return DB_section.from_line(line)
        elif int(key) == 2:
            return Shaped_section.from_line(line)
        raise TypeError("This line cannot convert mgt object.")


class Thicknesses(Fixed_length_block):
    item_type = Thickness
    line_num = 1
    key = "THICKNESS"


class bStatic_load_case(Singleline_block):
    item_type = Static_load_case
    line_num = 1
    key = "STLDCASE"


class bLoad_to_mass(Singleline_block):
    item_type = Load_to_mass
    line_num = 1
    key = "LOADTOMASS"

    @classmethod
    def from_lines(cls, lines):
        if len(lines) == 2:
            item = cls.item_type.from_line(lines)
            return cls(item)
        raise ValueError("Not convert loat to mass class. line num don't match.")


class bSelfweight(Singleline_block):
    item_type = Selfweight
    line_num = 1
    key = "SELFWEIGHT"


class Concentrated_loads(Fixed_length_block):
    item_type = Concentrated_load
    line_num = 1
    key = "CONLOAD"


class Beam_loads(Fixed_length_block):
    item_type = Beam_load
    line_num = 1
    key = "BEAMLOAD"


class Pressures(Fixed_length_block):
    item_type = Pressure
    line_num = 1
    key = "PRESSURE"


class Nodal_temperatures(Fixed_length_block):
    item_type = Nodal_temperature
    line_num = 1
    key = "NDTEMPER"


class Element_temepratures(Fixed_length_block):
    item_type = Element_temperature
    line_num = 1
    key = "ELTEMPER"


class Nodal_body_forces(Fixed_length_block):
    item_type = Nodal_body_force
    line_num = 1
    key = "NBODYFORCE"


class Load_combinations(Fixed_length_block):
    item_type = Load_combination
    line_num = 2
    key = "LOADCOMB"


if __name__ == "__main__":
    unit = bUnit(Unit())
    print(unit.to_lines())
    version = bVersion(Version())
    print(version.to_lines())
    nodes = Nodes.from_lines(["1, 1.0, 2.0, 3.0", "2, 4.0, 5.0, 6.0"])
    print(nodes.to_lines())

    elements = Elements.from_lines(
        [
            "2, BEAM, 1, 1, 2, 166, 0, 0",
            "1586, PLATE, 17, 1, 1114, 1108, 1005, 0, 1, 0"
        ]
    )
    print(elements.to_lines())

    constraints = Constraints.from_lines(
        [
            "35 38 40 88to97by3 103 107 110 133 146 164 168 190 193 194 201 216 , 111000, ",
            "254 268 272 273 276 353to355 357 360 361 364 556to559 562 601, 111000, " 
        ]
    )
    print(constraints.to_lines())

    frame_rlses = Frame_rlses.from_lines(
        [
            "19,  NO, 000011, 0, 0, 0, 0, 0, 0",
            "000000, 0, 0, 0, 0, 0, 0,",
            "27,  NO, 000011, 0, 0, 0, 0, 0, 0",
            "000000, 0, 0, 0, 0, 0, 0, "
        ]
    )
    print(frame_rlses.to_lines())

    materials = Materials.from_lines(
        [
            "1,  STEEL, STKN490,0,0,,C,NO,0.02,1,JIS(S),,STKN490, NO,205",
             " 17, USER , hoge, 0, 0, , C, NO, 0, 2, 2.0500e+002,   0.3, 1.2000e-005,     0,     0",
             "2, USER , hoge, 0, 0, , C, NO, 0, 3, 100, 200, 300, 0.1, 0.2, 0.3, 50, 100, 150, 0.1, 0.2, 0.3, 0.001"
        ]
    )
    print(materials.to_lines())

    sections = Sections.from_lines(
        [
            "1, DBUSER, P 318.5x12.7, CC, 0, 0, 0, 0, 0, 0, YES, NO, P, 2, 318.5, 12.7, 0, 0, 0, 0, 0, 0, 0, 0",
            "2, DBUSER, P 318.5x9, CC, 0, 0, 0, 0, 0, 0, YES, NO, P  , 1, JIS, P 318.5x9",
            "3, DBUSER, H 800x300x14/26, CC, 0, 0, 0, 0, 0, 0, YES, NO, H, 1, JIS, H 800x300x14/26"
        ]
    )
    print(sections.to_lines())

    ltm = bLoad_to_mass.from_lines(
        [
            "XY, YES, YES, YES, YES, 9.806",
            "DL, 1, LL(forE), 1, SL(forE), 1"
        ]
    )
    print(ltm.to_lines())

    key = Keyword("*TEST")
    test = {"TEST": 1}
    print(test[key])