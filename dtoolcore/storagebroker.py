"""Disk storage broker."""

import os
import json
import shutil
import logging
import datetime

from dtoolcore.utils import (
    mkdir_parents,
    generate_identifier,
    generous_parse_uri,
    timestamp,
)
from dtoolcore.filehasher import FileHasher, md5sum_hexdigest

logger = logging.getLogger(__name__)


_STRUCTURE_PARAMETERS = {
    "data_directory": ["data"],
    "dataset_readme_relpath": ["README.yml"],
    "dtool_directory": [".dtool"],
    "admin_metadata_relpath": [".dtool", "dtool"],
    "structure_metadata_relpath": [".dtool", "structure.json"],
    "dtool_readme_relpath": [".dtool", "README.txt"],
    "manifest_relpath": [".dtool", "manifest.json"],
    "overlays_directory": [".dtool", "overlays"],
    "metadata_fragments_directory": [".dtool", "tmp_fragments"],
}

_DTOOL_README_TXT = """README
======

This is a Dtool dataset stored on traditional file system storage.

Content provided during the dataset creation process
----------------------------------------------------

Dataset descriptive metadata: README.yml
Dataset items: data/

Automatically generated files and directories
---------------------------------------------

This file: .dtool/README.txt
Administrative metadata describing the dataset: .dtool/dtool
Structural metadata describing the dataset: .dtool/structure.json
Structural metadata describing the data items: .dtool/manifest.json
Per item descriptive metadata: .dtool/overlays/
"""


class StorageBrokerOSError(OSError):
    pass


class DiskStorageBrokerValidationWarning(Warning):
    pass


class DiskStorageBroker(object):
    """
    Storage broker to interact with datasets on local disk storage.

    The :class:`dtoolcore.ProtoDataSet` class uses the
    :class:`dtoolcore.storage_broker.DiskStorageBroker` to construct datasets
    by writing to disk and the :class:`dtoolcore.DataSet` class uses it to read
    datasets from disk.
    """

    #: Attribute used to define the type of storage broker.
    key = "file"

    #: Attribute used by :class:`dtoolcore.ProtoDataSet` to write the hash
    #: function name to the manifest.
    hasher = FileHasher(md5sum_hexdigest)

    def __init__(self, uri, config_path=None):

        self._set_abspaths(uri)

        self._essential_subdirectories = [
            self._dtool_abspath,
            self._data_abspath,
            self._overlays_abspath
        ]

    def _set_abspaths(self, uri):
        """Define useful absolute paths for future reference."""

        parse_result = generous_parse_uri(uri)
        path = parse_result.path
        self._abspath = os.path.abspath(path)

        def generate_abspath(key):
            return os.path.join(self._abspath, *_STRUCTURE_PARAMETERS[key])

        self._dtool_abspath = generate_abspath("dtool_directory")
        self._data_abspath = generate_abspath("data_directory")
        self._admin_metadata_fpath = generate_abspath("admin_metadata_relpath")
        self._structure_metadata_fpath = generate_abspath(
            "structure_metadata_relpath"
        )
        self._dtool_readme_abspath = generate_abspath("dtool_readme_relpath")
        self._manifest_abspath = generate_abspath("manifest_relpath")
        self._readme_abspath = generate_abspath("dataset_readme_relpath")
        self._overlays_abspath = generate_abspath("overlays_directory")
        self._metadata_fragments_abspath = generate_abspath(
            "metadata_fragments_directory"
        )

    @classmethod
    def list_dataset_uris(cls, base_uri, config_path):
        """Return list containing URIs in location given by base_uri."""

        parsed_uri = generous_parse_uri(base_uri)
        uri_list = []
        path = parsed_uri.path
        for d in os.listdir(path):
            dir_path = os.path.join(path, d)

            if not os.path.isdir(dir_path):
                continue

            storage_broker = cls(dir_path, config_path)

            if not storage_broker.has_admin_metadata():
                continue

            uri = storage_broker.generate_uri(
                name=d,
                uuid=None,
                base_uri=base_uri
            )
            uri_list.append(uri)

        return uri_list

    @classmethod
    def generate_uri(cls, name, uuid, base_uri):
        prefix = generous_parse_uri(base_uri).path
        dataset_path = os.path.join(prefix, name)
        dataset_abspath = os.path.abspath(dataset_path)
        return "{}://{}".format(cls.key, dataset_abspath)

#############################################################################
# Methods used by both ProtoDataSet and DataSet.
#############################################################################

    def get_admin_metadata(self):
        """Return admin metadata from disk.

        :returns: administrative metadata as a dictionary
        """
        with open(self._admin_metadata_fpath) as fh:
            return json.load(fh)

    def has_admin_metadata(self):
        """Return True if the administrative metadata exists.

        This is the definition of being a "dataset".
        """
        return os.path.isfile(self._admin_metadata_fpath)

    def get_readme_content(self):
        """Return content of the README file as a string.

        :returns: readme content as a string
        """
        with open(self._readme_abspath) as fh:
            return fh.read()

    def put_overlay(self, overlay_name, overlay):
        """Store the overlay by writing it to disk.

        It is the client's responsibility to ensure that the overlay provided
        is a dictionary with valid contents.

        :param overlay_name: name of the overlay
        :overlay: overlay dictionary
        """

        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        with open(fpath, 'w') as fh:
            json.dump(overlay, fh)

#############################################################################
# Methods only used by DataSet.
#############################################################################

    def get_manifest(self):
        """Return the manifest contents from disk.

        :returns: manifest as a dictionary
        """

        with open(self._manifest_abspath) as fh:
            return json.load(fh)

    def list_overlay_names(self):
        """Return list of overlay names."""
        overlay_names = []
        if not os.path.isdir(self._overlays_abspath):
            return overlay_names
        for fname in os.listdir(self._overlays_abspath):
            name, ext = os.path.splitext(fname)
            overlay_names.append(name)
        return overlay_names

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """

        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        with open(fpath) as fh:
            return json.load(fh)

    def get_item_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """
        manifest = self.get_manifest()
        item = manifest["items"][identifier]
        item_abspath = os.path.join(self._data_abspath, item["relpath"])
        return item_abspath

#############################################################################
# Methods only used by ProtoDataSet.
#############################################################################

    def create_structure(self):
        """Create necessary structure to hold a dataset."""

        # Ensure that the specified path does not exist and create it.
        if os.path.exists(self._abspath):
            raise(StorageBrokerOSError(
                "Path already exists: {}".format(self._abspath)
            ))

        # Make sure the parent directory exists.
        parent, _ = os.path.split(self._abspath)
        if not os.path.isdir(parent):
            raise(StorageBrokerOSError(
                "No such directory: {}".format(parent)))

        os.mkdir(self._abspath)

        # Create more essential subdirectories.
        for abspath in self._essential_subdirectories:
            if not os.path.isdir(abspath):
                os.mkdir(abspath)

        # Write out self descriptive metadata.
        with open(self._structure_metadata_fpath, "w") as fh:
            json.dump(_STRUCTURE_PARAMETERS, fh, indent=2, sort_keys=True)
        with open(self._dtool_readme_abspath, "w") as fh:
            fh.write(_DTOOL_README_TXT)

    def put_admin_metadata(self, admin_metadata):
        """Store the admin metadata by writing to disk.

        It is the client's responsibility to ensure that the admin metadata
        provided is a dictionary with valid contents.

        :param admin_metadata: dictionary with administrative metadata
        """
        with open(self._admin_metadata_fpath, 'w') as fh:
            json.dump(admin_metadata, fh)

    def put_manifest(self, manifest):
        """Store the manifest by writing it to disk.

        It is the client's responsibility to ensure that the manifest provided
        is a dictionary with valid contents.

        :param manifest: dictionary with manifest structural metadata
        """
        with open(self._manifest_abspath, 'w') as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """
        with open(self._readme_abspath, 'w') as fh:
            fh.write(content)

    def put_item(self, fpath, relpath):
        """Put item with content from fpath at relpath in dataset.

        Missing directories in relpath are created on the fly.

        :param fpath: path to the item on disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        :returns: the handle given to the item
        """

        # Define the destination path and make any missing parent directories.
        dest_path = os.path.join(self._data_abspath, relpath)
        dirname = os.path.dirname(dest_path)
        mkdir_parents(dirname)

        # Copy the file across.
        shutil.copyfile(fpath, dest_path)

        return relpath

    def iter_item_handles(self):
        """Return iterator over item handles."""

        path = self._data_abspath
        path_length = len(path) + 1

        for dirpath, dirnames, filenames in os.walk(path):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                relative_path = path[path_length:]
                yield relative_path

    def item_properties(self, handle):
        """Return properties of the item with the given handle."""

        fpath = os.path.join(self._data_abspath, handle)
        datetime_obj = datetime.datetime.utcfromtimestamp(
            os.stat(fpath).st_mtime
        )
        properties = {
            'size_in_bytes': os.stat(fpath).st_size,
            'utc_timestamp': timestamp(datetime_obj),
            'hash': DiskStorageBroker.hasher(fpath),
            'relpath': handle
        }
        return properties

    def _handle_to_fragment_absprefixpath(self, handle):
        stem = generate_identifier(handle)
        return os.path.join(self._metadata_fragments_abspath, stem)

    def add_item_metadata(self, handle, key, value):
        """Store the given key:value pair for the item associated with handle.

        :param handle: handle for accessing an item before the dataset is
                       frozen
        :param key: metadata key
        :param value: metadata value
        """
        if not os.path.isdir(self._metadata_fragments_abspath):
            os.mkdir(self._metadata_fragments_abspath)

        prefix = self._handle_to_fragment_absprefixpath(handle)
        fpath = prefix + '.{}.json'.format(key)

        with open(fpath, 'w') as fh:
            json.dump(value, fh)

    def get_item_metadata(self, handle):
        """Return dictionary containing all metadata associated with handle.

        In other words all the metadata added using the ``add_item_metadata``
        method.

        :param handle: handle for accessing an item before the dataset is
                       frozen
        :returns: dictionary containing item metadata
        """

        if not os.path.isdir(self._metadata_fragments_abspath):
            return {}

        prefix = self._handle_to_fragment_absprefixpath(handle)

        def list_abspaths(dirname):
            for f in os.listdir(dirname):
                yield os.path.join(dirname, f)

        files = [f for f in list_abspaths(self._metadata_fragments_abspath)
                 if f.startswith(prefix)]

        metadata = {}
        for f in files:
            key = f.split('.')[-2]  # filename: identifier.key.json
            with open(f) as fh:
                value = json.load(fh)
            metadata[key] = value

        return metadata

    def pre_freeze_hook(self):
        """Pre :meth:`dtoolcore.ProtoDataSet.freeze` actions.

        This method is called at the beginning of the
        :meth:`dtoolcore.ProtoDataSet.freeze` method.

        It may be useful for remote storage backends to generate
        caches to remove repetitive time consuming calls
        """
        allowed = set([v[0] for v in _STRUCTURE_PARAMETERS.values()])
        for d in os.listdir(self._abspath):
            if d not in allowed:
                msg = "Rogue content in base of dataset: {}".format(d)
                raise(DiskStorageBrokerValidationWarning(msg))

    def post_freeze_hook(self):
        """Post :meth:`dtoolcore.ProtoDataSet.freeze` cleanup actions.

        This method is called at the end of the
        :meth:`dtoolcore.ProtoDataSet.freeze` method.

        In the :class:`dtoolcore.storage_broker.DiskStorageBroker` it removes
        the temporary directory for storing item metadata fragment files.
        """
        if os.path.isdir(self._metadata_fragments_abspath):
            shutil.rmtree(self._metadata_fragments_abspath)
