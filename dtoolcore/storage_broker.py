"""Disk storage broker."""

import os


class StorageBrokerOSError(OSError):
    pass


class DiskStorageBroker(object):
    """Storage broker to allow DataSets and ProtoDataSets to be read from and
    written to local disk storage."""

    def __init__(self, path):

        self._path = path

    def create_structure(self):
        """Create necessary structure to hold ProtoDataset or DataSet."""

        if os.path.exists(self._path):
            raise(StorageBrokerOSError(
                "Path already exists: {}".format(self._path)
            ))

        os.mkdir(self._path)
