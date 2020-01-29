"""Test the helper functions and classes for creating datasets."""

from . import tmp_dir_fixture  # NOQA


def test_create_proto_dataset(tmp_dir_fixture):  # NOQA
    import dtoolcore

    name = "my-test-ds"
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=tmp_dir_fixture,
        readme_content=readme_content,
        creator_username=creator_username
    )
    assert isinstance(proto_dataset, dtoolcore.ProtoDataSet)
    assert proto_dataset._admin_metadata["creator_username"] == creator_username  # NOQA
    assert proto_dataset.name == name
    assert proto_dataset.get_readme_content() == readme_content


def test_DataSetCreator(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    with dtoolcore.DataSetCreator(
        name=name,
        base_uri=tmp_dir_fixture,
        readme_content=readme_content,
        creator_username=creator_username
    ) as dataset_creator:
        uri = dataset_creator.uri

    # The below would raise if the dataset was not frozen
    dtoolcore.DataSet.from_uri(uri)


def test_DataSetCreator_does_not_freeze_if_raises(tmp_dir_fixture):  # NOQA

    import dtoolcore

    name = "my-test-ds"
    readme_content = "---\ndescription: a test dataset"
    creator_username = "tester"

    try:
        with dtoolcore.DataSetCreator(
            name=name,
            base_uri=tmp_dir_fixture,
            readme_content=readme_content,
            creator_username=creator_username
        ) as dataset_creator:
            uri = dataset_creator.uri
            raise(RuntimeError("Something went wrong"))
    except RuntimeError:
        # The below would raise if the dataset was frozen.
        dtoolcore.ProtoDataSet.from_uri(uri)
