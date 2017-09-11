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
    """Return list of tuples where sizes differ.

    Tuple structure:
    (identifier, size in a, size in b)

    Assumes list of identifiers in a and b are identical.

    :param a: first :class:`dtoolcore.DataSet`
    :param b: second :class:`dtoolcore.DataSet`
    :returns: list of tuples for all items with different sizes
    """
    difference = []

    for i in a.identifiers:
        a_size = a.item_properties(i)["size_in_bytes"]
        b_size = b.item_properties(i)["size_in_bytes"]
        if a_size != b_size:
            difference.append((i, a_size, b_size))

    return difference


def diff_content(a, reference):
    """Return list of tuples where content differ.

    Tuple structure:
    (identifier, hash name, hash in a, hash in reference)

    Assumes list of identifiers in a and b are identical.

    Storage broker of reference used to generate hash for files in a.

    :param a: first :class:`dtoolcore.DataSet`
    :param b: second :class:`dtoolcore.DataSet`
    :returns: list of tuples for all items with different content
    """
    difference = []
    hasher_name = reference._storage_broker.hasher.name
    for i in a.identifiers:
        fpath = a.item_content_abspath(i)
        calc_hash = reference._storage_broker.hasher(fpath)
        ref_hash = reference.item_properties(i)["hash"]
        if calc_hash != ref_hash:
            info = (i, hasher_name, calc_hash, ref_hash)
            difference.append(info)
    return difference
