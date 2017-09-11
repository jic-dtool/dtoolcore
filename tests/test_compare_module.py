"""Test the compare module."""

import os

from . import tmp_dir_fixture  # NOQA


def create_test_files(directory):
    fpaths = dict()
    for word in ["he", "she", "cat"]:
        fpath = os.path.join(directory, word + ".txt")
        with open(fpath, "w") as fh:
            fh.write(word)
        fpaths[word] = fpath
    return fpaths


def test_diff_identifiers(tmp_dir_fixture):  # NOQA

    from dtoolcore import (
        DataSet,
        generate_admin_metadata,
        generate_proto_dataset,
    )
    from dtoolcore.utils import generate_identifier
    from dtoolcore.compare import diff_identifiers

    fpaths = create_test_files(tmp_dir_fixture)

    proto_ds_a = generate_proto_dataset(
        admin_metadata=generate_admin_metadata("test_compare_1"),
        prefix=tmp_dir_fixture,
        storage="file")
    proto_ds_a.create()
    proto_ds_a.put_item(fpaths["cat"], "a.txt")
    proto_ds_a.freeze()

    proto_ds_b = generate_proto_dataset(
        admin_metadata=generate_admin_metadata("test_compare_2"),
        prefix=tmp_dir_fixture,
        storage="file")
    proto_ds_b.create()
    proto_ds_b.put_item(fpaths["cat"], "b.txt")
    proto_ds_b.freeze()

    ds_a = DataSet.from_uri(proto_ds_a.uri)
    ds_b = DataSet.from_uri(proto_ds_b.uri)

    assert diff_identifiers(ds_a, ds_a) == (set(), set())

    expected = (
        set([generate_identifier("a.txt")]),
        set([generate_identifier("b.txt")])
    )
    assert diff_identifiers(ds_a, ds_b) == expected


def test_diff_sizes(tmp_dir_fixture):  # NOQA

    from dtoolcore import (
        DataSet,
        generate_admin_metadata,
        generate_proto_dataset,
    )
    from dtoolcore.utils import generate_identifier
    from dtoolcore.compare import diff_sizes

    fpaths = create_test_files(tmp_dir_fixture)

    proto_ds_a = generate_proto_dataset(
        admin_metadata=generate_admin_metadata("test_compare_1"),
        prefix=tmp_dir_fixture,
        storage="file")
    proto_ds_a.create()
    proto_ds_a.put_item(fpaths["he"], "file.txt")
    proto_ds_a.freeze()

    proto_ds_b = generate_proto_dataset(
        admin_metadata=generate_admin_metadata("test_compare_2"),
        prefix=tmp_dir_fixture,
        storage="file")
    proto_ds_b.create()
    proto_ds_b.put_item(fpaths["she"], "file.txt")
    proto_ds_b.freeze()

    ds_a = DataSet.from_uri(proto_ds_a.uri)
    ds_b = DataSet.from_uri(proto_ds_b.uri)

    assert diff_sizes(ds_a, ds_a) == []

    expected = [
        (generate_identifier("file.txt"), 2, 3 ),
    ]
    assert diff_sizes(ds_a, ds_b) == expected
