"""Test the helper functions and classes for creating datasets."""

import os

import pytest

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

    assert "created_at" in proto_dataset.admin_metadata
    assert "frozen_at" not in proto_dataset.admin_metadata
    assert proto_dataset.admin_metadata["dtoolcore_version"] == dtoolcore.__version__  # NOQA
    assert proto_dataset.admin_metadata["creator_username"] == creator_username  # NOQA
    assert proto_dataset.admin_metadata["uuid"] == proto_dataset.uuid
    assert proto_dataset.admin_metadata["type"] == "protodataset"

    assert proto_dataset.name == name
    assert proto_dataset.get_readme_content() == readme_content


def test_create_derived_proto_dataset(tmp_dir_fixture):  # NOQA
    import dtoolcore

    name = "derived-data-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    with dtoolcore.DataSetCreator("raw-data-ds", base_uri) as dataset_creator:
        source_dataset_uri = dataset_creator.uri
    source_dataset = dtoolcore.DataSet.from_uri(source_dataset_uri)

    proto_dataset = dtoolcore.create_derived_proto_dataset(
        name=name,
        base_uri=base_uri,
        source_dataset=source_dataset,
        readme_content=readme_content,
        creator_username=creator_username
    )
    assert isinstance(proto_dataset, dtoolcore.ProtoDataSet)

    assert "created_at" in proto_dataset.admin_metadata
    assert "frozen_at" not in proto_dataset.admin_metadata
    assert proto_dataset.admin_metadata["dtoolcore_version"] == dtoolcore.__version__  # NOQA
    assert proto_dataset.admin_metadata["creator_username"] == creator_username  # NOQA
    assert proto_dataset.admin_metadata["uuid"] == proto_dataset.uuid
    assert proto_dataset.admin_metadata["type"] == "protodataset"

    assert proto_dataset.name == name

    # Test the annotations.
    assert proto_dataset.get_annotation("source_dataset_name") == source_dataset.name  # NOQA
    assert proto_dataset.get_annotation("source_dataset_uri") == source_dataset.uri  # NOQA
    assert proto_dataset.get_annotation("source_dataset_uuid") == source_dataset.uuid  # NOQA


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
        assert dataset_creator.name == name
        uri = dataset_creator.uri
        handle = dataset_creator.put_item(local_file_path, "subdir/tiny.png")
        dataset_creator.add_item_metadata(handle, "ext", ".png")

    # The below would raise if the dataset was not frozen.
    dataset = dtoolcore.DataSet.from_uri(uri)

    # Check admin metadata
    assert "created_at" in dataset.admin_metadata
    assert "frozen_at" in dataset.admin_metadata
    assert dataset.admin_metadata["frozen_at"] >= dataset.admin_metadata["created_at"]  # NOQA
    assert dataset.admin_metadata["dtoolcore_version"] == dtoolcore.__version__  # NOQA
    assert dataset.admin_metadata["creator_username"] == creator_username  # NOQA
    assert dataset.admin_metadata["uuid"] == dataset.uuid
    assert dataset.admin_metadata["type"] == "dataset"

    # Check the content.
    expected_identifier = generate_identifier("subdir/tiny.png")
    assert expected_identifier in dataset.identifiers
    assert len(dataset.identifiers) == 1

    # Check item metadata
    expected_ext_overlay = {expected_identifier: ".png"}
    assert dataset.get_overlay("ext") == expected_ext_overlay


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


def test_DataSetCreator_staging_api(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    with dtoolcore.DataSetCreator(
        name=name,
        base_uri=base_uri,
        readme_content=readme_content,
        creator_username=creator_username
    ) as dataset_creator:

        # Ensure that the staging directory exists.
        assert os.path.isdir(dataset_creator.staging_directory)

        uri = dataset_creator.uri

    # Ensure that the staging directory has been removed.
    assert not os.path.isdir(dataset_creator.staging_directory)

    # The below would raise if the dataset was not frozen.
    dtoolcore.DataSet.from_uri(uri)



def test_DataSetCreator_staging_api_stage_item(tmp_dir_fixture):  # NOQA

    import dtoolcore
    from dtoolcore.utils import generate_identifier

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    handle = "subdir/test.txt"

    with dtoolcore.DataSetCreator(
        name=name,
        base_uri=base_uri,
        readme_content=readme_content,
        creator_username=creator_username
    ) as dataset_creator:

        # Ensure that the staging directory exists.
        assert os.path.isdir(dataset_creator.staging_directory)

        # Add an item more programatically.
        staging_abspath = dataset_creator.prepare_staging_abspath_promise(  # NOQA
            handle
        )
        with open(staging_abspath, "w") as fh:
            fh.write("Hello world!")

        uri = dataset_creator.uri

    # Ensure that the staging directory has been removed.
    assert not os.path.isdir(dataset_creator.staging_directory)

    # The below would raise if the dataset was not frozen.
    dataset = dtoolcore.DataSet.from_uri(uri)

    # Check the content.
    expected_identifier = generate_identifier(handle)
    assert expected_identifier in dataset.identifiers
    manual_item_props = dataset.item_properties(expected_identifier)
    assert manual_item_props["size_in_bytes"] == 12

    assert len(dataset.identifiers) == 1


def test_DerivedDataSetCreator(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "derived-data-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    creator_username = "tester"

    with dtoolcore.DataSetCreator("raw-data-ds", base_uri) as dataset_creator:
        source_dataset_uri = dataset_creator.uri
    source_dataset = dtoolcore.DataSet.from_uri(source_dataset_uri)

    with dtoolcore.DerivedDataSetCreator(
        name=name,
        base_uri=base_uri,
        source_dataset=source_dataset,
        creator_username=creator_username
    ) as derived_dataset_creator:
        derived_dataset_uri = derived_dataset_creator.uri

    # The below would raise if the dataset was not frozen.
    dataset = dtoolcore.DataSet.from_uri(derived_dataset_uri)

    # Check admin metadata
    assert "created_at" in dataset.admin_metadata
    assert "frozen_at" in dataset.admin_metadata
    assert dataset.admin_metadata["frozen_at"] >= dataset.admin_metadata["created_at"]  # NOQA
    assert dataset.admin_metadata["dtoolcore_version"] == dtoolcore.__version__  # NOQA
    assert dataset.admin_metadata["creator_username"] == creator_username  # NOQA
    assert dataset.admin_metadata["uuid"] == dataset.uuid
    assert dataset.admin_metadata["type"] == "dataset"


def test_promised_abspath_missing_raises(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    handle = "test.txt"

    with pytest.raises(dtoolcore.DtoolCoreBrokenStagingPromise):
        with dtoolcore.DataSetCreator(
            name=name,
            base_uri=base_uri,
            readme_content=readme_content,
            creator_username=creator_username
        ) as dataset_creator:

            # Add an item more programatically.
            staging_abspath = dataset_creator.prepare_staging_abspath_promise(  # NOQA
                handle
            )


def test_DataSetCreator_put_readme(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    with dtoolcore.DataSetCreator(
        name=name,
        base_uri=base_uri,
        creator_username=creator_username
    ) as dataset_creator:
        uri = dataset_creator.uri
        assert dataset_creator.proto_dataset.get_readme_content() == ""
        dataset_creator.put_readme(readme_content)

    # The below would raise if the dataset was not frozen.
    dataset = dtoolcore.DataSet.from_uri(uri)
    assert readme_content == dataset.get_readme_content()


def test_DataSetCreator_put_annotation(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    creator_username = "tester"

    with dtoolcore.DataSetCreator(
        name=name,
        base_uri=base_uri,
        creator_username=creator_username
    ) as dataset_creator:
        uri = dataset_creator.uri
        dataset_creator.put_annotation("key", "value")

    # The below would raise if the dataset was not frozen.
    dataset = dtoolcore.DataSet.from_uri(uri)
    assert dataset.get_annotation("key") == "value"
