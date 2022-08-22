from itertools import count, groupby


def calc_diff_counter(n, c=count()):
        return n - next(c)


def count_bool(b, c=count()):
    if b:
        return next(c)
    else:
        return int(str(c).lstrip("count(").rstrip(")")) - 1


def grouping_values(values, f_bool):
    bools = [f_bool(x) for x in values]
    key_func = lambda x: x[1]
    grouped = [
        [
            x[0] for x in list(g)
        ] for _, g in groupby(
            zip(values, bools),
            key=key_func
        )
    ]
    return grouped    


def grouping_values_by_index(values, f_bool):
    bools = [f_bool(x) for x in range(len(values))]
    key_func = lambda x: x[1]
    grouped = [
        [
            x[0] for x in list(g)
        ] for _, g in groupby(
            zip(values, bools),
            key=key_func
        )
    ]
    return grouped


def grouping_values_by_discrete_flag(values, f_bool):
    bools = [f_bool(x) for x in values]
    counted = [count_bool(x) for x in bools]
    key_func = lambda x: x[1]
    grouped = [
        [
            x[0] for x in list(g)
        ] for _, g in groupby(
            zip(values, counted),
            key=key_func
        )
    ]
    return grouped


def grouping_values_by_discrete_index_flag(values, f_bool):
    bools = [f_bool(x) for x in range(len(values))]
    counted = [count_bool(x) for x in bools]
    key_func = lambda x: x[1]
    grouped = [
        [
            x[0] for x in list(g)
        ] for _, g in groupby(
            zip(values, counted),
            key=key_func
        )
    ]
    return grouped


def grouping_continuous_int(values):
        sorted_values = sorted(values)
        counted = [calc_diff_counter(x) for x in sorted_values]
        key_func = lambda x: x[1]
        grouped = [
            [
                x[0] for x in list(g)
            ] for _, g in groupby(
                zip(sorted_values, counted),
                key=key_func
            )
        ]
        return grouped
