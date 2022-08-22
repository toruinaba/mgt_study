from ast import Load
from distutils.version import StrictVersion

from collections import namedtuple

from utils import (
    grouping_values_by_discrete_index_flag,
    grouping_values_by_index
)
from mixins import ElementMixin
from fields import (
    Natural_number,
    Positive_integer,
    Stripped_str,
    Mgt_flag,
    Dof_flags,
    Id_list,
    Load_case_dict,
    Element_type,
    Direction_type,
    Material_type,
    Material_sub_type,
    Offset_type,
    Load_unit_type,
    Meter_unit_type,
    Load_case_type
)


class Dataset_Meta(type):
    def __new__(cls, name, bases, d):
        fields = d.get("fields", ())
        datatypes = d.get("datatypes", ())
        defaults = d.get("defaults", ())
        typed_defaults = tuple([cast(x) for x, cast in zip(defaults, datatypes)])
        dataset_class = namedtuple(name, fields)
        dataset_class.__new__.__defaults__ = typed_defaults
        d["dataset_class"] = dataset_class
        return type.__new__(cls, name, bases, d)


class Dataset_base(object):
    __metaclass__ = Dataset_Meta
    __slots__ = ("_dataset")
    dataset_class = None
    fields = ()
    datatypes = ()
    defaults = ()

    def __init__(self, *args, **kwargs):
        typed_args = self._apply_datatype(args)
        if kwargs:
            typed_kwargs = {k: self.field_dict[k](v) for k, v in kwargs.items()}
            self._dataset = self.dataset_class(*typed_args, **typed_kwargs)
        self._dataset = self.dataset_class(*typed_args)

    def __getattr__(self, name):
        return self._dataset.__getattribute__(name)

    def __repr__(self):
        return self._dataset.__repr__()

    def _apply_datatype(self, params):
        return tuple([cast(x) for x, cast in zip(params, self.datatypes)])

    @property
    def field_dict(self):
        return {f: d for f, d in zip(self.fields, self.datatypes)}

    def to_line(self):
        raise NotImplementedError

    @classmethod
    def from_line(cls):
        raise NotImplementedError


class Singleline_dataset(Dataset_base):
    def to_line(self):
        return ", ".join(map(str, self._dataset))

    @classmethod
    def from_line(cls, line):
        params = line.split(",")
        return cls(*params)


class Multiline_dataset(Dataset_base):
    lf_positions = ()

    def __init__(self, *args, **kwargs):
        if not self.lf_positions:
            raise NotImplementedError("This class don't have any lf_position.")
        super(Multiline_dataset, self).__init__(*args, **kwargs)

    def to_line(self):
        divided = grouping_values_by_discrete_index_flag(
            self._dataset,
            lambda x: x in self.lf_positions
        )
        stringed = [", ".join(map(str, x)) for x in divided]
        return "\n".join(stringed)

    @classmethod
    def from_line(cls, line):
        if len(line) - 1 != len(cls.lf_positions):
            raise ValueError("Not match line num.")
        splitted = [x.split(",") for x in line]
        params = sum(splitted, [])
        return cls(*params)


class Unit(Singleline_dataset):
    fields = ("force", "length", "heat", "temper")
    datatypes = (Load_unit_type, Meter_unit_type, Stripped_str, Stripped_str)
    defaults = ("KN", "M", "KJ", "C")


class Version(Singleline_dataset):
    fields = ("version",)
    datatypes = (StrictVersion,)
    defaults = ("8.8.1",)


class Node(Singleline_dataset):
    fields = ("id", "x", "y", "z")
    datatypes = (Natural_number, float, float, float)
    defaults = (1, 0.0, 0.0, 0.0)


class Line_element(Singleline_dataset, ElementMixin):
    fields = ("id", "type", "imat", "isect", "i", "j", "angle", "isb")
    datatypes = (
        Natural_number,
        Element_type,
        Natural_number,
        Natural_number,
        Natural_number,
        Natural_number,
        float,
        int
    )
    defaults = (1, 0, 1, 1, 1, 1, 0.0, 0)

    @property
    def node_ids(self):
        return self.i, self.j


class Plate_element(Singleline_dataset, ElementMixin):
    fields = (
        "id",
        "type",
        "imat",
        "isect",
        "n1",
        "n2",
        "n3",
        "n4",
        "isb",
        "iwid",
        "lcaxis"
    )
    datatypes = (
        Natural_number,
        Element_type,
        Natural_number,
        Natural_number,
        Natural_number,
        Natural_number,
        Natural_number,
        Positive_integer,
        Natural_number,
        Positive_integer,
        Stripped_str
    )
    defaults = (
        1,
        4,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        ""
    )

    @property
    def node_ids(self):
        if self.n4:
            return self.n1, self.n2, self.n3, self.n4
        return self.n1, self.n2, self.n3


class Constraint(Singleline_dataset):
    fields = ("id_list", "condition", "group")
    datatypes = (Id_list, Dof_flags, Stripped_str)
    defaults = (1, "111111", "")


class Frame_rls(Multiline_dataset):
    fields = (
        "id_list",
        "b_value",
        "i_flag",
        "fxi",
        "fyi",
        "fzi",
        "mxi",
        "myi",
        "mzi",
        "j_flag",
        "fxj",
        "fyj",
        "fzj",
        "mxj",
        "myj",
        "mzj",
    )
    datatypes = (
        Id_list,
        Mgt_flag,
        Dof_flags,
        float,
        float,
        float,
        float,
        float,
        float,
        Dof_flags,
        float,
        float,
        float,
        float,
        float,
        float
    )
    defaults = (
        1,
        False,
        "000111",
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        "000111",
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    )
    lf_positions = (8,)


class DB_material(Singleline_dataset):
    fields = (
        "id",
        "type",
        "name",
        "spheat",
        "heatco",
        "plast",
        "tunit",
        "b_mass",
        "damp_ratio",
        "num",
        "db_name",
        "standard",
        "code",
        "use_elast",
        "elast"
    )
    datatypes = (
        Natural_number,
        Material_type,
        Material_sub_type,
        float,
        float,
        Stripped_str,
        Stripped_str, # tunit
        Mgt_flag,
        float,
        Natural_number,
        Stripped_str,
        Stripped_str,
        Material_sub_type,
        Mgt_flag,
        float
    )
    defaults = (
        1,
        1,
        0,
        0,
        0,
        "",
        "C",
        False,
        0.0,
        1,
        "",
        "",
        0,
        False,
        0
    )


class Isotropic_material(Singleline_dataset):
    fields = (
        "id",
        "type",
        "name",
        "spheat",
        "heatco",
        "plast",
        "tunit",
        "b_mass",
        "damp_ratio",
        "num",
        "elastic",
        "poisson",
        "thermal",
        "density",
        "mass"
    )
    datatypes = (
        Natural_number,
        Material_type,
        Stripped_str,
        float,
        float,
        Stripped_str,
        Stripped_str,
        Mgt_flag,
        float,
        Natural_number,
        float,
        float,
        float,
        float,
        Positive_integer
    )
    defaults = (
        1,
        0,
        "Material",
        0.0,
        0.0,
        "",
        "C",
        False,
        0.0,
        2,
        205.0,
        0.3,
        0.000012,
        0.0,
        0
    )

class Orthotropic_material(Singleline_dataset):
    fields = (
        "id",
        "type",
        "name",
        "spheat",
        "heatco",
        "plast",
        "tunit",
        "b_mass",
        "damp_ratio",
        "num",
        "ex",
        "ey",
        "ez",
        "tx",
        "ty",
        "tz",
        "sxy",
        "sxz",
        "syz",
        "pxy",
        "pxz",
        "pyz",
        "density"
    )
    datatypes = (
        Natural_number,
        Material_type,
        Stripped_str,
        float,
        float,
        Stripped_str,
        Stripped_str,
        Mgt_flag,
        float,
        Natural_number,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float
    )
    defaults = (
        1,
        0,
        "Material",
        0.0,
        0.0,
        "",
        "C",
        False,
        0.0,
        2,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    )


class DB_section(Singleline_dataset):
    fields = (
        "id",
        "type",
        "name",
        "offset",
        "icent",
        "iref",
        "ihorz",
        "huser",
        "ivert",
        "vuser",
        "b_sd",
        "b_we",
        "shape",
        "num",
        "dbname",
        "sname"
    )
    datatypes = (
        Natural_number,
        Stripped_str,
        Stripped_str,
        Offset_type,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Mgt_flag,
        Mgt_flag,
        Stripped_str,
        Positive_integer,
        Stripped_str,
        Stripped_str
    )
    defaults = (
        1,
        "DBUSER",
        "H 800x300x14/26",
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        True,
        False,
        "H",
        1,
        "JIS",
        "H 800x300x14/26"
    )


class Shaped_section(Singleline_dataset):
    fields = (
        "id",
        "type",
        "name",
        "offset",
        "icent",
        "iref",
        "ihorz",
        "huser",
        "ivert",
        "vuser",
        "b_sd",
        "b_we",
        "shape",
        "num",
        "d1",
        "d2",
        "d3",
        "d4",
        "d5",
        "d6",
        "d7",
        "d8",
        "d9",
        "d10"
    )
    datatypes = (
        Natural_number,
        Stripped_str,
        Stripped_str,
        Offset_type,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Positive_integer,
        Mgt_flag,
        Mgt_flag,
        Stripped_str,
        Positive_integer,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float
    )
    defaults = (
        1,
        "DBUSER",
        "P 318.5x12.7",
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        True,
        False,
        "P",
        2,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    )


class Thickness(Singleline_dataset):
    fields = (
        "id",
        "type",
        "b_same",
        "thick_in",
        "thick_out",
        "b_offset",
        "offtype",
        "value"
    )
    datatypes = (
        Natural_number,
        Stripped_str,
        Mgt_flag,
        float,
        float,
        Mgt_flag,
        Positive_integer,
        float
    )
    defaults = (
        1,
        "VALUE",
        False,
        0.0,
        0.0,
        False,
        0,
        0
    )


class Static_load_case(Singleline_dataset):
    fields = ("name", "type", "description")
    datatypes = (Stripped_str, Load_case_type, Stripped_str)
    defaults = ("DL", 1, "Deadload")


class Load_to_mass(Multiline_dataset):
    fields = ("dir", "b_nodal", "b_beam", "b_floor", "b_pres", "gravity", "load_case_factor")
    datatypes = (Stripped_str, Mgt_flag, Mgt_flag, Mgt_flag, Mgt_flag, float, Load_case_dict)
    defaults = ("XY", True, True, True, True, 9.806, {"DL": 1.0, "LL": 1.0})
    lf_positions = (6,)

    @classmethod
    def from_line(cls, line):
        splitted = [x.split(",") for x in line]
        params = splitted[0]
        lc = splitted[1]
        return cls(*params, load_case_factor=lc)


class Selfweight(Singleline_dataset):
    fields = ("x", "y", "z", "group")
    datatypes = (float, float, float, Stripped_str)
    defaults = (0.0, 0.0, 1.0, "")


class Concentrated_load(Singleline_dataset):
    fields = (
        "id_list",
        "fx",
        "fy",
        "fz",
        "mx",
        "my",
        "mz",
        "group"
    )
    datatypes = (
        Id_list,
        float,
        float,
        float,
        float,
        float,
        float,
        Stripped_str
    )
    defaults = (
        1,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        ""
    )


class Beam_load(Singleline_dataset):
    fields = (
        "id_list",
        "cmd",
        "type",
        "diretion",
        "b_proj",
        "b_ecc",
        "ecc_dir",
        "i_end",
        "j_end",
        "b_j_end",
        "d1",
        "p1",
        "d2",
        "p2",
        "d3",
        "p3",
        "d4",
        "p4",
        "group",
        "b_additional",
        "additional_i_end",
        "additional_j_end",
        "b_additional_j_end"
    )
    datatypes = (
        Id_list,
        Stripped_str,
        Stripped_str,
        Direction_type,
        Mgt_flag,
        Mgt_flag,
        Stripped_str,
        Stripped_str,
        Stripped_str,
        Stripped_str,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        Stripped_str,
        Mgt_flag,
        float,
        float,
        Mgt_flag
    )
    defaults = (
        1,
        "TYPICAL",
        "UNILOAD",
        0,
        False,
        False,
        "aDir[1]",
        "",
        "",
        "",
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        "",
        False,
        0,
        0,
        False,
    )


class Pressure(Singleline_dataset):
    fields = (
        "id_list",
        "cmd",
        "e_type",
        "l_type",
        "direction",
        "vx",
        "vy",
        "vz",
        "b_proj",
        "value",
        "p1",
        "p2",
        "p3",
        "p4",
        "group"
    )
    datatypes = (
        Id_list,
        Stripped_str,
        Stripped_str,
        Stripped_str,
        Stripped_str,
        float,
        float,
        float,
        Mgt_flag,
        float,
        float,
        float,
        float,
        float,
        Stripped_str
    )
    defaults = (
        1,
        "PRES",
        "PLATE",
        "FACE",
        "GZ",
        0.0,
        0.0,
        0.0,
        False,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        ""
    )


class Nodal_temperature(Singleline_dataset):
    fields = ("id_list", "value", "group")
    datatypes = (Id_list, float, Stripped_str)
    defaults = (1, 0.0, "")


class Element_temperature(Singleline_dataset):
    fields = ("id_list", "value", "group")
    datatypes = (Id_list, float, Stripped_str)
    defaults = (1, 0.0, "")


class Nodal_body_force(Singleline_dataset):
    fields = (
        "b_usegroup",
        "id_list",
        "b_nmass",
        "b_lmass",
        "b_smass",
        "b_gmass",
        "x",
        "y",
        "z"
    )
    datatypes = (
        Mgt_flag,
        Id_list,
        Mgt_flag,
        Mgt_flag,
        Mgt_flag,
        Mgt_flag,
        float,
        float,
        float
    )
    defaults = (
        False,
        1,
        True,
        True,
        True,
        False,
        0.0,
        0.0,
        0.0
    )


class Load_combination(Multiline_dataset):
    fields = (
        "name",
        "kind",
        "active",
        "bes",
        "itype",
        "desc",
        "iserv_type",
        "nlcomtype",
        "load_case_factor"
    )
    datatypes = (
        Stripped_str,
        Stripped_str,
        Stripped_str,
        Positive_integer,
        Positive_integer,
        Stripped_str,
        Positive_integer,
        Positive_integer,
        Load_case_dict
    )
    defaults = (
        "CB1",
        "GEN",
        "ACTIVE",
        0,
        0,
        "",
        0,
        0,
        {"DL": 1.0, "LL": 1.0}
    )
    lf_positions = (8,)

    def to_line(self):
        name = self._dataset[0].to_str_with_key("NAME")
        params = [name] + list(map(str, self._dataset[1:-1]))
        param_line = ", ".join(params)
        lc_line = self._dataset[-1].to_str_with_key("ST")
        return param_line + "\n" + lc_line

    @classmethod
    def from_line(cls, line):
        splitted = [x.split(",") for x in line]
        params = [splitted[0][0].lstrip("NAME=")] + splitted[0][1:]
        grouped = grouping_values_by_index(splitted[1], lambda x: x // 3)
        lc = sum([[x[1], x[2]] for x in grouped], [])
        return cls(*params, load_case_factor=lc)


if __name__ == "__main__":
    unit1 = Unit()
    print(unit1)

    version1 = Version()
    print(version1)

    node1 = Node()
    print(node1)

    line_elem1 = Line_element()
    print(line_elem1)

    plate_elem1 = Plate_element()
    print(plate_elem1)

    constraint1 = Constraint()
    print(constraint1)

    frame_rls1 = Frame_rls()
    print(frame_rls1)

    db_mat1 = DB_material()
    print(db_mat1)

    iso_mat1 = Isotropic_material()
    print(iso_mat1)

    ort_mat1 = Orthotropic_material()
    print(ort_mat1)

    db_sec1 = DB_section()
    print(db_sec1)

    shaped_sec1 = Shaped_section()
    print(shaped_sec1)

    thickness1 = Thickness()
    print(thickness1)

    stld1 = Static_load_case()
    print(stld1)

    ltm1 = Load_to_mass()
    print(ltm1)
    ltm2 = Load_to_mass.from_line(["XY, YES, YES, YES, YES, 9.806", "DL, 1.0, LL, 1.0"])
    print(ltm2)

    sw1 = Selfweight()
    print(sw1)

    con_load1 = Concentrated_load()
    print(con_load1)

    beam_load1 = Beam_load()
    print(beam_load1)

    ntemp1 = Nodal_temperature()
    print(ntemp1)

    eltemp1 = Element_temperature()
    print(eltemp1)

    nbodyf1 = Nodal_body_force()
    print(nbodyf1)

    load_comb1 = Load_combination()
    print(load_comb1)
    print(load_comb1.to_line())
    load_comb2 = Load_combination.from_line(["NAME=CB1, GEN, ACTIVE, 0, 0, , 0, 0", "ST, DL, 1.0, ST, LL, 1.0"])
    print(load_comb2)
