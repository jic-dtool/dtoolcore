"""Test the :class:`dtoolcore.Manifest` class."""

import os
import json
import shutil

from dtoolcore.utils import sha1_hexdigest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATASET


def test_manifest_functional(tmp_dir_fixture):  # NOQA
    from dtoolcore import Manifest

    data_path = os.path.join(TEST_SAMPLE_DATASET, "data")
    manifest = Manifest(data_path)

    identifiers = manifest["items"].keys()

    assert sha1_hexdigest('empty_file') in identifiers

    output_fpath = os.path.join(tmp_dir_fixture, "manifest.json")
    assert not os.path.isfile(output_fpath)

    manifest.persist_to_path(output_fpath)
    assert os.path.isfile(output_fpath)

    with open(output_fpath) as fh:
        manifest_from_json = json.load(fh)
    assert manifest == manifest_from_json


def test_manifest_initialisation():
    from dtoolcore import Manifest, __version__

    data_path = os.path.join(TEST_SAMPLE_DATASET, "data")

    manifest = Manifest(abs_manifest_root=data_path)

    assert manifest.abs_manifest_root == data_path
    assert manifest.hash_generator.name == "shasum"

    assert isinstance(manifest, dict)
    assert "items" in manifest
    assert "dtool_version" in manifest
    assert "hash_function" in manifest

    assert isinstance(manifest["items"], dict)
    assert manifest["dtool_version"] == __version__
    assert manifest["hash_function"] == "shasum"

    assert len(manifest["items"]) == 7

    hashes = [entry["hash"] for entry in manifest["items"].values()]
    assert "290d3f1a902c452ce1c184ed793b1d6b83b59164" in hashes


def test_manifest_initialisation_with_trailing_slash():
    from dtoolcore import Manifest, __version__

    data_path = os.path.join(TEST_SAMPLE_DATASET, "data/")

    manifest = Manifest(abs_manifest_root=data_path)

    assert manifest.hash_generator.name == "shasum"

    assert isinstance(manifest, dict)
    assert "items" in manifest
    assert "dtool_version" in manifest
    assert "hash_function" in manifest

    assert isinstance(manifest["items"], dict)
    assert manifest["dtool_version"] == __version__
    assert manifest["hash_function"] == "shasum"

    assert len(manifest["items"]) == 7

    hashes = [entry["hash"] for entry in manifest["items"].values()]
    assert "290d3f1a902c452ce1c184ed793b1d6b83b59164" in hashes


def test_regenerate_file_list(tmp_dir_fixture):  # NOQA
    from dtoolcore import Manifest

    input_data_path = os.path.join(TEST_SAMPLE_DATASET, "data")
    output_data_path = os.path.join(tmp_dir_fixture, "data")
    shutil.copytree(input_data_path, output_data_path)

    manifest = Manifest(output_data_path)
    assert len(manifest["items"]) == 7

    # Remove all the files from the manifest root directory.
    shutil.rmtree(output_data_path)
    os.mkdir(output_data_path)

    manifest.regenerate_file_list()
    assert len(manifest["items"]) == 0


def test_persist_to_path(tmp_dir_fixture):  # NOQA

    from dtoolcore import Manifest, __version__

    manifest = Manifest(tmp_dir_fixture)

    output_fpath = os.path.join(tmp_dir_fixture, "manifest.json")
    assert not os.path.isfile(output_fpath)

    manifest.persist_to_path(output_fpath)
    assert os.path.isfile(output_fpath)

    with open(output_fpath) as fh:
        manifest_from_json = json.load(fh)

    assert manifest_from_json["dtool_version"] == __version__
    assert manifest_from_json["hash_function"] == "shasum"
    assert len(manifest_from_json["items"]) == 0


def test_file_metadata():

    from dtoolcore import Manifest

    input_data_path = os.path.join(TEST_SAMPLE_DATASET, "data")
    png_path = os.path.join(input_data_path, 'tiny.png')

    manifest = Manifest(input_data_path)

    metadata = manifest._file_metadata(png_path)
    expected_keys = ["hash", "size", "mtime"]
    assert set(expected_keys) == set(metadata.keys())
    assert metadata["hash"] == "09648d19e11f0b20e5473594fc278afbede3c9a4"
    assert metadata["size"] == 276


def test_manifest_from_path(tmp_dir_fixture):  # NOQA
    from dtoolcore import Manifest

    data_dir = os.path.join(tmp_dir_fixture, "data")
    os.mkdir(data_dir)

    test_file1 = os.path.join(data_dir, "test1.txt")
    with open(test_file1, "w") as fh:
        fh.write("hello")

    manifest = Manifest(data_dir)
    manifest_path = os.path.join(tmp_dir_fixture, "manifest.json")
    manifest.persist_to_path(manifest_path)

    test_file2 = os.path.join(data_dir, "test2.txt")
    with open(test_file2, "w") as fh:
        fh.write("world")

    parsed_manifest = Manifest.from_path(
        manifest_path=manifest_path, data_directory=data_dir)
    assert parsed_manifest is not manifest
    assert parsed_manifest == manifest
    assert isinstance(parsed_manifest, Manifest)

    assert len(parsed_manifest["items"]) == 1
    parsed_manifest.regenerate_file_list()
    assert len(parsed_manifest["items"]) == 2


def test_manifest_ignore_using_dtool_markup_scenario(tmp_dir_fixture):  # NOQA
    from dtoolcore import Manifest

    data_path = os.path.join(TEST_SAMPLE_DATASET)
    ignore_prefixes = [
        ".dtool{}".format(os.sep),
        "README.yml",
    ]
    manifest = Manifest(data_path, ignore_prefixes=ignore_prefixes)
    assert len(manifest["items"]) == 7
