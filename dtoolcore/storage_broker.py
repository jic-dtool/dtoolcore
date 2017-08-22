"""Disk storage broker."""

import os
import json
import shutil

from dtoolcore.utils import (
    mkdir_parents,
    generate_identifier,
)
from dtoolcore.filehasher import FileHasher, md5sum


class StorageBrokerOSError(OSError):
    pass


class DiskStorageBroker(object):
    """Storage broker to allow DataSets and ProtoDataSets to be read from and
    written to local disk storage."""

    hasher = FileHasher(md5sum)

    def __init__(self, path):

        # Define useful absolute paths for future reference.
        self._abspath = os.path.abspath(path)
        self._dtool_abspath = os.path.join(self._abspath, '.dtool')
        self._admin_metadata_fpath = os.path.join(self._dtool_abspath, 'dtool')
        self._data_abspath = os.path.join(self._abspath, 'data')
        self._manifest_abspath = os.path.join(
            self._dtool_abspath,
            'manifest.json'
        )
        self._readme_abspath = os.path.join(
            self._abspath,
            'README.yml'
        )
        self._overlays_abspath = os.path.join(
            self._dtool_abspath,
            'overlays'
        )
        self._metadata_fragments_abspath = os.path.join(
            self._dtool_abspath,
            'tmp_fragments'
        )

#############################################################################
# Methods used by both ProtoDataSet and DataSet.
#############################################################################

    def get_admin_metadata(self):
        """Return admin metadata from disk."""

        with open(self._admin_metadata_fpath) as fh:
            return json.load(fh)

    def get_readme_content(self):
        """Return content of the readme file as a string."""

        with open(self._readme_abspath) as fh:
            return fh.read()

    def put_overlay(self, overlay_name, overlay):
        """Store the overlay by writing it to disk."""

        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        with open(fpath, 'w') as fh:
            json.dump(overlay, fh)

#############################################################################
# Methods only used by DataSet.
#############################################################################

    def get_manifest(self):
        """Retrieve the manifest contents."""

        with open(self._manifest_abspath) as fh:
            return json.load(fh)

    def get_overlay(self, overlay_name):

        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        with open(fpath) as fh:
            return json.load(fh)

    def get_item_abspath(self, identifier):
        manifest = self.get_manifest()
        item = manifest["items"][identifier]
        item_abspath = os.path.join(self._data_abspath, item["relpath"])
        return item_abspath

#############################################################################
# Methods only used by ProtoDataSet.
#############################################################################

    def create_structure(self):
        """Create necessary structure to hold ProtoDataset or DataSet."""

        # Ensure that the specified path does not exist and create it.
        if os.path.exists(self._abspath):
            raise(StorageBrokerOSError(
                "Path already exists: {}".format(self._abspath)
            ))
        os.mkdir(self._abspath)

        # Create more essential subdirectories.
        for abspath in [self._dtool_abspath, self._overlays_abspath]:
            if not os.path.isdir(abspath):
                os.mkdir(abspath)

    def put_admin_metadata(self, admin_metadata):
        """Store the admin metadata by writing to disk."""

        with open(self._admin_metadata_fpath, 'w') as fh:
            json.dump(admin_metadata, fh)

    def put_manifest(self, manifest_contents):
        """Store the given manifest contents so we can retrieve it later."""

        with open(self._manifest_abspath, 'w') as fh:
            json.dump(manifest_contents, fh)

    def put_readme(self, readme_contents):
        """Store readme contents. It is up to the caller to ensure that the
        contents are valid YAML."""

        with open(self._readme_abspath, 'w') as fh:
            fh.write(readme_contents)

    def put_item(self, fpath, relpath):
        """Store item with contents from fpath at relpath."""

        # Define the destination path and make any missing parent directories.
        dest_path = os.path.join(self._data_abspath, relpath)
        dirname = os.path.dirname(dest_path)
        mkdir_parents(dirname)

        # Copy the file across.
        shutil.copyfile(fpath, dest_path)

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
        properties = {
            'size_in_bytes': os.stat(fpath).st_size,
            'utc_timestamp': os.stat(fpath).st_mtime,
            'hash': DiskStorageBroker.hasher(fpath),
            'relpath': handle
        }
        return properties

    def _handle_to_fragment_absprefixpath(self, handle):

        stem = generate_identifier(handle)
        return os.path.join(self._metadata_fragments_abspath, stem)

    def add_item_metadata(self, handle, key, value):
        """Store the given key:value pair for the item associated with handle.
        """

        if not os.path.isdir(self._metadata_fragments_abspath):
            os.mkdir(self._metadata_fragments_abspath)

        prefix = self._handle_to_fragment_absprefixpath(handle)
        fpath = prefix + '.{}.json'.format(key)

        with open(fpath, 'w') as fh:
            json.dump(value, fh)

    def get_item_metadata(self, handle):
        """Return dictionary with all metadata associated with handle."""

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

    def post_freeze_hook(self):
        """Cleanup actions post calling :meth:`ProtoDataSet.freeze` method."""
        if os.path.isdir(self._metadata_fragments_abspath):
            shutil.rmtree(self._metadata_fragments_abspath)
