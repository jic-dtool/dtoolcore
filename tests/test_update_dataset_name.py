"""Test the dtoolcore.ProtoDataset.update_name method."""

import pytest

from . import tmp_uri_fixture  # NOQA


def test_update_name(tmp_uri_fixture):  # NOQA

    import dtoolcore

    admin_metadata = dtoolcore.generate_admin_metadata("test_name")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=tmp_uri_fixture
    )

    assert proto_dataset.name == "test_name"

    proto_dataset.update_name("test_new_name")

    assert proto_dataset.name == "test_new_name"

    proto_dataset.create()

    proto_dataset.update_name("test_another_new_name")

    assert proto_dataset.name == "test_another_new_name"

    read_proto_dataset = dtoolcore.ProtoDataSet.from_uri(proto_dataset.uri)

    assert read_proto_dataset.name == "test_another_new_name"


def test_update_name_raises_DtoolCoreInvalidName(tmp_uri_fixture):  # NOQA

    import dtoolcore
    from dtoolcore import DtoolCoreInvalidNameError

    admin_metadata = dtoolcore.generate_admin_metadata("test_name")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=tmp_uri_fixture
    )

    assert proto_dataset.name == "test_name"

    proto_dataset.update_name("test_new_name")

    assert proto_dataset.name == "test_new_name"

    proto_dataset.create()

    with pytest.raises(DtoolCoreInvalidNameError):
        proto_dataset.update_name("test_another:new_name")


def test_update_name_of_frozen_dataset(tmp_uri_fixture):  # NOQA

    import dtoolcore

    # Create a dataset.
    admin_metadata = dtoolcore.generate_admin_metadata("test_name")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=tmp_uri_fixture
    )
    proto_dataset.create()
    proto_dataset.freeze()

    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset.name == "test_name"

    dataset.update_name("updated_name")
    assert dataset.name == "updated_name"

    dataset_again = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset_again.name == "updated_name"

    # Make sure that none of the other admin metadata has been altered.
    for key, value in admin_metadata.items():
        if key == "name":
            continue
        assert dataset_again._admin_metadata[key] == value
