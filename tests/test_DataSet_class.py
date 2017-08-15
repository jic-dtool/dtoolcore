"""Test the dtoolcore.DataSet class."""

import os
import json

import pytest

from dtoolcore.utils import sha1_hexdigest

from . import tmp_dir_fixture  # NOQA
from . import chdir_fixture  # NOQA
from . import TEST_SAMPLE_DATASET


def test_dataset_initialisation():
    from dtoolcore import DataSet

    dataset = DataSet(name='my_dataset')
    assert dataset.name == 'my_dataset'
    assert len(dataset.uuid) == 36
    assert dataset._admin_metadata['type'] == 'dataset'
    assert dataset._admin_metadata['manifest_root'] == '.'
    expected_manifest_path = os.path.join('.dtool', 'manifest.json')
    assert dataset._admin_metadata['manifest_path'] == expected_manifest_path
    assert dataset._abs_manifest_path is None
    assert isinstance(dataset.dtool_version, str)
    assert isinstance(dataset.creator_username, str)
    assert dataset.abs_readme_path is None

    assert dataset.data_directory == '.'

    expected_overlays_path = os.path.join('.dtool', 'overlays')
    assert dataset._admin_metadata['overlays_path'] == expected_overlays_path
    assert dataset._abs_overlays_path is None


def test_initialise_alternative_manifest_root():
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset', data_directory='archive')

    assert dataset._admin_metadata['manifest_root'] == 'archive'


def test_cannot_change_uuid_or_name():
    from dtoolcore import DataSet

    dataset = DataSet(name='my_dataset')

    with pytest.raises(AttributeError):
        dataset.uuid = None

    with pytest.raises(AttributeError):
        dataset.name = None


def test_dataset_persist_to_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet('my_dataset')

    expected_dtool_dir = os.path.join(tmp_dir_fixture, '.dtool')
    expected_dtool_file = os.path.join(expected_dtool_dir, 'dtool')
    expected_overlays_dir = os.path.join(expected_dtool_dir, "overlays")
    assert not os.path.isdir(expected_dtool_dir)
    assert not os.path.isfile(expected_dtool_file)
    assert not os.path.isdir(expected_overlays_dir)

    dataset.persist_to_path(tmp_dir_fixture)
    assert os.path.isdir(expected_dtool_dir)
    assert os.path.isfile(expected_dtool_file)
    assert os.path.isdir(expected_overlays_dir)

    import json
    with open(expected_dtool_file) as fh:
        admin_metadata = json.load(fh)
    assert admin_metadata['type'] == 'dataset'
    assert dataset._admin_metadata == admin_metadata

    expected_readme_path = os.path.join(tmp_dir_fixture, 'README.yml')
    assert os.path.isfile(expected_readme_path)

    expected_manifest_path = os.path.join(
        tmp_dir_fixture, '.dtool', 'manifest.json')
    assert os.path.isfile(expected_manifest_path)


def test_dataset_persist_to_path_hash_function(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')
    dataset.persist_to_path(tmp_dir_fixture)

    parsed_ds = DataSet.from_path(tmp_dir_fixture)
    assert parsed_ds.manifest["hash_function"] == "shasum"


def test_persist_to_path_updates_abs_readme_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    assert dataset.abs_readme_path is None

    dataset.persist_to_path(tmp_dir_fixture)

    expected_abs_readme_path = os.path.join(tmp_dir_fixture, 'README.yml')
    assert dataset.abs_readme_path == expected_abs_readme_path


def test_creation_of_data_dir(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet('my_dataset', data_directory='data')

    expected_data_directory = os.path.join(tmp_dir_fixture, 'data')
    assert not os.path.isdir(expected_data_directory)

    dataset.persist_to_path(tmp_dir_fixture)
    assert os.path.isdir(expected_data_directory)


def test_multiple_persist_to_path_raises(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    dataset.persist_to_path(tmp_dir_fixture)

    with pytest.raises(OSError):
        dataset.persist_to_path(tmp_dir_fixture)


def test_persist_to_path_sets_abs_paths(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    expected_abs_readme_path = os.path.join(tmp_dir_fixture, 'README.yml')
    expected_abs_manifest_path = os.path.join(tmp_dir_fixture,
                                              '.dtool',
                                              'manifest.json')
    expected_abs_overlays_path = os.path.join(tmp_dir_fixture,
                                              '.dtool',
                                              'overlays')

    assert dataset.abs_readme_path is None
    assert dataset._abs_manifest_path is None
    assert dataset._abs_overlays_path is None

    dataset.persist_to_path(tmp_dir_fixture)

    assert dataset.abs_readme_path == expected_abs_readme_path
    assert dataset._abs_manifest_path == expected_abs_manifest_path
    assert dataset._abs_overlays_path == expected_abs_overlays_path


def test_equality():
    from copy import deepcopy
    from dtoolcore import DataSet
    dataset = DataSet('my_dataset')
    dataset_again = deepcopy(dataset)
    assert dataset_again == dataset

    # We should never do this!
    dataset_again._admin_metadata['name'] = 'nonsense'
    assert dataset_again != dataset


def test_do_not_overwrite_existing_readme(chdir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    readme_contents = "---\nproject_name: test_project\n"

    with open('README.yml', 'w') as fh:
        fh.write(readme_contents)

    dataset.persist_to_path('.')

    with open('README.yml') as fh:
        actual_contents = fh.read()

    assert actual_contents == readme_contents


def test_persist_to_path_raises_if_path_does_not_exist(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    attempted_path = os.path.join(tmp_dir_fixture, 'my_project')

    with pytest.raises(OSError) as excinfo:
        dataset.persist_to_path(attempted_path)

    expected_error = 'No such directory: {}'.format(attempted_path)
    assert expected_error in str(excinfo.value)


def test_manifest_generation(chdir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    with open('README.yml', 'w') as fh:
        fh.write('---')
        fh.write('project_name: test_project')

    with open('test_file.txt', 'w') as fh:
        fh.write('Hello world')

    dataset.persist_to_path('.')

    expected_manifest_path = os.path.join('.dtool', 'manifest.json')

    with open(expected_manifest_path) as fh:
        manifest = json.load(fh)

    assert 'items' in manifest
    assert len(manifest['items']) == 1
    identifier = sha1_hexdigest('test_file.txt')
    assert identifier in manifest['items']
    assert manifest['items'][identifier]['size'] == 11


def test_abspath_from_identifier(chdir_fixture):  # NOQA
    from dtoolcore import DataSet

    filename = 'test_file.txt'

    dataset = DataSet('my_dataset')

    with open(filename, 'w') as fh:
        fh.write('Hello world')

    dataset.persist_to_path('.')

    expected_path = os.path.abspath(filename)
    identifier = sha1_hexdigest(filename)
    actual_path = dataset.abspath_from_identifier(identifier)
    assert actual_path == expected_path

    with pytest.raises(KeyError):
        dataset.abspath_from_identifier("nonsense")


def test_item_from_identifier(chdir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    with open('test_file.txt', 'w') as fh:
        fh.write('Hello world')

    dataset.persist_to_path('.')

    identifier = sha1_hexdigest('test_file.txt')
    item = dataset.item_from_identifier(identifier)
    assert item["hash"] == "7b502c3a1f48c8609ae212cdfb639dee39673f5e"
    assert "size" in item
    assert "path" in item

    with pytest.raises(KeyError):
        dataset.item_from_identifier("nonsense")


def test_abspath_from_identifier_with_different_datadir(chdir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset', "crazy")
    dataset.persist_to_path('.')

    fpath = os.path.join("crazy", "test_file.txt")
    with open(fpath, 'w') as fh:
        fh.write('Hello world')

    dataset.update_manifest()

    expected_path = os.path.abspath(fpath)
    identifier = sha1_hexdigest('test_file.txt')
    actual_path = dataset.abspath_from_identifier(identifier)
    assert actual_path == expected_path


def test_dataset_from_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet("my_data_set")
    dataset.persist_to_path(tmp_dir_fixture)

    dataset_again = DataSet.from_path(tmp_dir_fixture)
    assert dataset_again == dataset


def test_dataset_from_path_sets_structural_metadata(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet("my_data_set")
    dataset.persist_to_path(tmp_dir_fixture)

    dataset_again = DataSet.from_path(tmp_dir_fixture)
    assert hasattr(dataset_again, "_structural_metadata")

    from dtoolcore import Manifest
    assert isinstance(dataset_again._structural_metadata,
                      Manifest)


def test_dataset_from_path_issue_with_manifest_datadirectory_being_relative(tmp_dir_fixture):  # NOQA

    # Because the data directory is relative care must be taken to make sure
    # that it is set correctly when creating absolute data directory when
    # instantiating the Manifest instance for the DataSet._structural_metadata
    # when reading from path.

    from dtoolcore import DataSet

    dataset = DataSet("my_data_set", data_directory="data")
    dataset.persist_to_path(tmp_dir_fixture)

    sample_fpath = os.path.join(tmp_dir_fixture, "data", "sample.txt")
    with open(sample_fpath, "w") as fh:
        fh.write("hello")

    dataset_again = DataSet.from_path(tmp_dir_fixture)
    dataset_again.update_manifest()
    assert len(dataset_again._structural_metadata["items"]) == 1


def test_dataset_from_path_raises_if_no_dtool_file(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet, NotDtoolObject
    with pytest.raises(NotDtoolObject):
        DataSet.from_path(tmp_dir_fixture)


def test_dataset_from_path_if_called_on_collection(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet, Collection, DtoolTypeError
    collection = Collection()
    collection.persist_to_path(tmp_dir_fixture)
    with pytest.raises(DtoolTypeError):
        DataSet.from_path(tmp_dir_fixture)


def test_from_path_raises_DtoolTypeError_if_type_does_not_exist(chdir_fixture):  # NOQA
    from dtoolcore import DataSet, DtoolTypeError

    admin_metadata = {}
    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)
    dtool_file = os.path.join(dtool_dir, 'dtool')

    with open(dtool_file, 'w') as fh:
        json.dump(admin_metadata, fh)

    with pytest.raises(DtoolTypeError):
        DataSet.from_path('.')


def test_from_path_sets_abspath(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet("my_data_set")
    assert dataset._abs_path is None
    dataset.persist_to_path(tmp_dir_fixture)
    assert dataset._abs_path == tmp_dir_fixture

    dataset_again = DataSet.from_path(tmp_dir_fixture)
    assert dataset_again._abs_path == tmp_dir_fixture


def test_manifest_property(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset', 'data')
    assert dataset.manifest == {}

    dataset.persist_to_path(tmp_dir_fixture)
    assert 'items' in dataset.manifest
    assert dataset.manifest['items'] == {}


def test_update_manifest(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset', 'data')
    dataset.persist_to_path(tmp_dir_fixture)

    new_file_path = os.path.join(
        tmp_dir_fixture, dataset.data_directory, 'test.txt')
    with open(new_file_path, 'w') as fh:
        fh.write('Hello world')

    dataset.update_manifest()

    assert len(dataset.manifest['items']) == 1


def test_update_manifest_does_nothing_if_not_persisted():
    from dtoolcore import DataSet

    dataset = DataSet('my_dataset')

    dataset.update_manifest()

    assert dataset.manifest == {}


def test_decriptive_metadata_property(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet('my_dataset')
    assert dataset.raw_descriptive_metadata == ""

    dataset.persist_to_path(tmp_dir_fixture)
    assert dataset.raw_descriptive_metadata == ""

    with open(dataset.abs_readme_path, "w") as fh:
        fh.write("---\n")
        fh.write("project: my_project\n")
    assert dataset.raw_descriptive_metadata ==  \
        open(dataset.abs_readme_path, "r").read()


def test_identifiers_property():
    from dtoolcore import DataSet
    dataset = DataSet.from_path(TEST_SAMPLE_DATASET)
    assert isinstance(dataset.identifiers, list)
    assert len(dataset.identifiers) == 7
    second_identifier = sha1_hexdigest('empty_file')
    assert second_identifier in dataset.identifiers


def test_dataset_ignore_dtool_and_readme(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet
    dataset = DataSet(name='my_dataset')
    dataset.persist_to_path(tmp_dir_fixture)
    dataset.update_manifest()
    assert len(dataset.manifest["items"]) == 0

    dataset_from_path = DataSet.from_path(tmp_dir_fixture)
    dataset_from_path.update_manifest()
    assert len(dataset_from_path.manifest["items"]) == 0
