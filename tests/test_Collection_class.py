"""Test the dtoolcore.Collection class."""

import os
import json

import pytest

from . import tmp_dir_fixture  # NOQA
from . import chdir_fixture  # NOQA


def test_Collection_initialisation():
    from dtoolcore import Collection
    collection = Collection()
    assert len(collection.uuid) == 36
    assert collection.abs_readme_path is None
    assert collection._admin_metadata["type"] == "collection"
    assert isinstance(collection.dtool_version, str)


def test_persist_to_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection
    collection = Collection()

    expected_dtool_dir = os.path.join(tmp_dir_fixture, ".dtool")
    expected_dtool_file = os.path.join(expected_dtool_dir, "dtool")
    assert not os.path.isdir(expected_dtool_dir)
    assert not os.path.isfile(expected_dtool_file)

    collection.persist_to_path(tmp_dir_fixture)
    assert os.path.isdir(expected_dtool_dir)
    assert os.path.isfile(expected_dtool_file)

    import json
    with open(expected_dtool_file) as fh:
        admin_metadata = json.load(fh)
    assert admin_metadata["type"] == "collection"
    assert collection._admin_metadata == admin_metadata


def test_multiple_persist_to_path_raises(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection
    collection = Collection()

    collection.persist_to_path(tmp_dir_fixture)
    with pytest.raises(OSError):
        collection.persist_to_path(tmp_dir_fixture)


def test_decriptive_metadata_property(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection
    collection = Collection()
    assert collection.raw_descriptive_metadata == ""

    collection.persist_to_path(tmp_dir_fixture)
    assert collection.raw_descriptive_metadata == ""

    with open(collection.abs_readme_path, "w") as fh:
        fh.write("---\n")
        fh.write("project: my_project\n")
    assert collection.raw_descriptive_metadata ==  \
        open(collection.abs_readme_path, "r").read()


def test_equality():
    from copy import deepcopy
    from dtoolcore import Collection
    collection = Collection()
    collection_again = deepcopy(collection)
    assert collection_again == collection

    # We should never do this!
    collection_again._admin_metadata['uuid'] = 'nonsense'
    assert collection_again != collection


def test_cannot_change_uuid():
    from dtoolcore import Collection
    collection = Collection()
    with pytest.raises(AttributeError):
        collection.uuid = "not_a_uuid"


def test_from_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection
    collection = Collection()
    collection.persist_to_path(tmp_dir_fixture)

    collection_again = Collection.from_path(tmp_dir_fixture)
    assert collection == collection_again


def test_check_type_on_from_path(chdir_fixture):  # NOQA
    from dtoolcore import Collection, DtoolTypeError

    admin_metadata = {'type': 'dataset'}
    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)
    dtool_file = os.path.join(dtool_dir, 'dtool')

    with open(dtool_file, 'w') as fh:
        json.dump(admin_metadata, fh)

    with pytest.raises(DtoolTypeError):
        Collection.from_path('.')


def test_from_path_raises_DtoolTypeError_if_type_does_not_exist(chdir_fixture):  # NOQA
    from dtoolcore import Collection, DtoolTypeError

    admin_metadata = {}
    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)
    dtool_file = os.path.join(dtool_dir, 'dtool')

    with open(dtool_file, 'w') as fh:
        json.dump(admin_metadata, fh)

    with pytest.raises(DtoolTypeError):
        Collection.from_path('.')


def test_no_dtool_file_raises_NotDtoolObject(chdir_fixture):  # NOQA
    from dtoolcore import Collection, NotDtoolObject

    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)

    with pytest.raises(NotDtoolObject):
        Collection.from_path('.')


def test_no_dtool_dir_raises_NotDtoolObject(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection, NotDtoolObject

    with pytest.raises(NotDtoolObject):
        Collection.from_path(tmp_dir_fixture)


def test_persist_to_path_sets_abs_readme_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection

    collection = Collection()

    expected_abs_readme_path = os.path.join(tmp_dir_fixture, 'README.yml')

    assert collection.abs_readme_path is None

    collection.persist_to_path(tmp_dir_fixture)

    assert collection.abs_readme_path == expected_abs_readme_path


def test_do_not_overwrite_existing_readme(chdir_fixture):  # NOQA
    from dtoolcore import Collection

    collection = Collection()

    readme_contents = "---\nproject_name: test_project\n"

    with open('README.yml', 'w') as fh:
        fh.write(readme_contents)

    collection.persist_to_path('.')

    with open('README.yml') as fh:
        actual_contents = fh.read()

    assert actual_contents == readme_contents


def test_from_path_sets_abspath(tmp_dir_fixture):  # NOQA
    from dtoolcore import Collection
    collection = Collection()
    collection.persist_to_path(tmp_dir_fixture)
    assert collection._abs_path == tmp_dir_fixture

    collection_again = Collection.from_path(tmp_dir_fixture)
    assert collection_again._abs_path == tmp_dir_fixture
