"""Module with helper functions for comparing datasets."""


def diff_identifiers(a, b):
    """Return list of tuples where identifiers in datasets differ.

    Tuple structure:
    (identifier, present in a, present in b)

    :param a: first :class:`dtoolcore.DataSet`
    :param b: second :class:`dtoolcore.DataSet`
    :returns: list of tuples where identifiers in datasets differ
    """

    a_ids = set(a.identifiers)
    b_ids = set(b.identifiers)

    difference = []

    for i in a_ids.difference(b_ids):
        difference.append((i, True, False))
    for i in b_ids.difference(a_ids):
        difference.append((i, False, True))

    return difference


def diff_sizes(a, b, progressbar=None):
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
        if progressbar:
            progressbar.update(1)

    return difference


def diff_content(a, reference, progressbar=None):
    """Return list of tuples where content differ.

    Tuple structure:
    (identifier, hash in a, hash in reference)

    Assumes list of identifiers in a and b are identical.

    Storage broker of reference used to generate hash for files in a.

    :param a: first :class:`dtoolcore.DataSet`
    :param b: second :class:`dtoolcore.DataSet`
    :returns: list of tuples for all items with different content
    """
    difference = []

    for i in a.identifiers:
        fpath = a.item_content_abspath(i)
        calc_hash = reference._storage_broker.hasher(fpath)
        ref_hash = reference.item_properties(i)["hash"]
        if calc_hash != ref_hash:
            info = (i, calc_hash, ref_hash)
            difference.append(info)
        if progressbar:
            progressbar.update(1)

    return difference
