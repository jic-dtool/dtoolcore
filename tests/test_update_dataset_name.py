"""Test the dtoolcore.ProtoDataset.update_name method."""

from . import tmp_dir_fixture  # NOQA


def test_copy(tmp_dir_fixture):  # NOQA

    import dtoolcore

    admin_metadata = dtoolcore.generate_admin_metadata("test_name")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        prefix=tmp_dir_fixture,
        storage="file")

    assert proto_dataset.name == "test_name"

    proto_dataset.update_name("test_new_name")

    assert proto_dataset.name == "test_new_name"

    proto_dataset.create()

    proto_dataset.update_name("test_another_new_name")

    assert proto_dataset.name == "test_another_new_name"

    read_proto_dataset = dtoolcore.ProtoDataSet.from_uri(proto_dataset.uri)

    assert read_proto_dataset.name == "test_another_new_name"
