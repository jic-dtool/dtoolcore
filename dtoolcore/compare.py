"""Module with helper functions for comparing datasets."""

def diff_identifiers(a, b):
    """Return tuple of sets containing identifiers not in other dataset.

    :param a: first :class:`dtoolcore.DataSet`
    :param b: second :class:`dtoolcore.DataSet`
    :returns: set(a not in b), set(b not in a)
    """
    a_ids = set(a.identifiers)
    b_ids = set(b.identifiers)
    return a_ids.difference(b_ids), b_ids.difference(a_ids)


def diff_sizes(a, b):
    """Return list of tuples (identifier, size in a, size in b).

    Assumes list of identifiers in a and b are identical.

    :param a: first :class:`dtoolcore.DataSet`
    :param b: second :class:`dtoolcore.DataSet`
    :returns: list of tuples for all items with different sizes
              (identifier, size in a, size in b)
    """
    difference = []

    for i in a.identifiers:
        a_size = a.item_properties(i)["size_in_bytes"]
        b_size = b.item_properties(i)["size_in_bytes"]
        if a_size != b_size:
            difference.append((i, a_size, b_size))

    return difference
