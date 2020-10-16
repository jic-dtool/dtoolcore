"""Test the iter_datasets_in_base_uri function."""

from . import tmp_uri_fixture  # NOQA


def test_iter_datasets_in_base_uri(tmp_uri_fixture):  # NOQA

    from dtoolcore import (
        create_proto_dataset,
        DataSet,
        ProtoDataSet,
        iter_datasets_in_base_uri,
        iter_proto_datasets_in_base_uri,
    )

    # Create a proto dataset.
    proto_ds = create_proto_dataset("proto", tmp_uri_fixture)

    # Create a proto dataset.
    _frozen_ds = create_proto_dataset("frozen", tmp_uri_fixture)
    _frozen_ds.freeze()
    frozen_ds = DataSet.from_uri(_frozen_ds.uri)

    from_iter_datasets = list(iter_datasets_in_base_uri(tmp_uri_fixture))
    from_iter_proto_datasets = list(iter_proto_datasets_in_base_uri(tmp_uri_fixture))  # NOQA
    assert len(from_iter_datasets) == 1
    assert len(from_iter_datasets) == 1

    assert isinstance(from_iter_datasets[0], DataSet)
    assert isinstance(from_iter_proto_datasets[0], ProtoDataSet)

    assert proto_ds.uri == from_iter_proto_datasets[0].uri
    assert frozen_ds.uri == from_iter_datasets[0].uri
