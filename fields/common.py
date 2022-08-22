ELEMENT_TYPE_TUPLE = ("BEAM", "TRUSS", "TENSTR", "COMPTR", "PLATE")
DIRECTION_TYPE_TUPLE = ("GX", "GY", "GZ", "LX", "LY", "LZ")
MATERIAL_TYPE_TUPLE = ("USER", "STEEL", "CONC")
MATERIAL_SUB_TYPE_TUPLE = (
    'SN400', 'SNR400', 'STKN400', 'SN490', 
    'STKN490', 'SS400', 'STK400', 'STKR400',
    'SSC400', 'SWH400', 'SS490', 'SS540',
    'SM400', 'SMA400', 'SM400-TMC', 'SM490',
    'SM490Y', 'SMA490', 'STKR490', 'STK490',
    'SM490-TMC', 'SM520', 'SM520-TMC', 'SM570',
    'SWPC7A', 'SWPC7B', 'BCR295', 'BCP235',
    'BCP325', 'Fc18', 'Fc21', 'Fc24',
    'Fc27', 'Fc30', 'Fc33', 'Fc36', 'Fc39',
    'Fc42', 'Fc45', 'Fc48', 'Fc51', 'Fc54',
    'Fc57', 'Fc60', 'Fc18(LT1)', 'Fc21(LT1)',
    'Fc24(LT1)', 'Fc27(LT1)', 'Fc30(LT1)',
    'Fc33(LT1)', 'Fc36(LT1)', 'Fc18(LT2)',
    'Fc24(LT2)', 'Fc27(LT2)'   
)
OFFSET_TYPE_TUPLE = ("LT", "CT", "RT", "LC", "CC", "RC", "LB", "CB", "RB")
LOAD_UNIT_TYPE_TUPLE = ("KN", "N")
METER_UNIT_TYPE_TUPLE = ("M", "MM")
LOAD_CASE_TYPE_TUPLE = (
    "USER", "D", "L", "LE", "LR",
    "W", "WA", "WT", "E", "EVT",
    "S", "SE", "R", "IP", "EP",
    "EH", "EV", "WP", "FP", "SF",
    "B", "CR", "SH", "T", "PS",
    "CS", "ER", "IL", "BK", "WL",
    "CF", "CO", "RS", "EX", "I", "EE"
)