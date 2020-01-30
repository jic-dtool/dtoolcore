"""Test the helper functions and classes for creating datasets."""

import os

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA

from dtoolcore.utils import (
    IS_WINDOWS,
    generous_parse_uri,
    windows_to_unix_path,
)

def _sanitise_base_uri(tmp_dir):
    base_uri = tmp_dir
    if IS_WINDOWS:
        parsed_base_uri = generous_parse_uri(tmp_dir)
        unix_path = windows_to_unix_path(parsed_base_uri.path)
        base_uri = "file://{}".format(unix_path)
    return base_uri



def test_create_proto_dataset(tmp_dir_fixture):  # NOQA
    import dtoolcore

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
        readme_content=readme_content,
        creator_username=creator_username
    )
    assert isinstance(proto_dataset, dtoolcore.ProtoDataSet)
    assert proto_dataset._admin_metadata["creator_username"] == creator_username  # NOQA
    assert proto_dataset.name == name
    assert proto_dataset.get_readme_content() == readme_content


def test_DataSetCreator(tmp_dir_fixture):  # NOQA

    import dtoolcore
    from dtoolcore.utils import generate_identifier

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"
    local_file_path = os.path.join(TEST_SAMPLE_DATA, "tiny.png")

    with dtoolcore.DataSetCreator(
        name=name,
        base_uri=base_uri,
        readme_content=readme_content,
        creator_username=creator_username
    ) as dataset_creator:
        uri = dataset_creator.uri
        dataset_creator.put_item(local_file_path, "tiny.png")

    # The below would raise if the dataset was not frozen
    dataset = dtoolcore.DataSet.from_uri(uri)

    # Check the content.
    expected_identifier = generate_identifier("tiny.png")
    assert expected_identifier in dataset.identifiers
    assert len(dataset.identifiers) == 1


def test_DataSetCreator_does_not_freeze_if_raises(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    try:
        with dtoolcore.DataSetCreator(
            name=name,
            base_uri=base_uri,
            readme_content=readme_content,
            creator_username=creator_username
        ) as dataset_creator:
            uri = dataset_creator.uri
            raise(RuntimeError("Something went wrong"))
    except RuntimeError:
        # The below would raise if the dataset was frozen.
        dtoolcore.ProtoDataSet.from_uri(uri)
