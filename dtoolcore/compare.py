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
