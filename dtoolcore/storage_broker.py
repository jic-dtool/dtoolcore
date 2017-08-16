"""Disk storage broker."""

import os
import json
import shutil

from dtoolcore.utils import mkdir_parents


class StorageBrokerOSError(OSError):
    pass


class DiskStorageBroker(object):
    """Storage broker to allow DataSets and ProtoDataSets to be read from and
    written to local disk storage."""

    def __init__(self, path):

        self._abspath = os.path.abspath(path)
        self._dtool_abspath = os.path.join(self._abspath, '.dtool')
        self._admin_metadata_fpath = os.path.join(self._dtool_abspath, 'dtool')

        self._data_abspath = os.path.join(self._abspath, 'data')

    def create_structure(self):
        """Create necessary structure to hold ProtoDataset or DataSet."""

        if os.path.exists(self._abspath):
            raise(StorageBrokerOSError(
                "Path already exists: {}".format(self._abspath)
            ))

        os.mkdir(self._abspath)

    def store_admin_metadata(self, admin_metadata):
        """Store the admin metadata by writing to disk."""

        if not os.path.isdir(self._dtool_abspath):
            os.mkdir(self._dtool_abspath)

        with open(self._admin_metadata_fpath, 'w') as fh:
            json.dump(admin_metadata, fh)

    def get_admin_metadata(self):
        """Retrieve admin metadata from disk and return."""

        with open(self._admin_metadata_fpath) as fh:
            return json.load(fh)

    def put_item(self, fpath, relpath):
        """Store item with contents from fpath at relpath."""

        dest_path = os.path.join(self._data_abspath, relpath)

        dirname = os.path.dirname(dest_path)

        mkdir_parents(dirname)

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

