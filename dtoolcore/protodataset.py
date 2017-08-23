import uuid
import datetime

from collections import defaultdict

import dtoolcore.utils
from dtoolcore.utils import generate_identifier

from dtoolcore.storage_broker import DiskStorageBroker

from dtoolcore import __version__


class ProtoDataSet(object):
    """
    Class for building up a dataset.
    """

    def __init__(self, name, admin_metadata=None):

        if admin_metadata is None:
            self._admin_metadata = {
                "uuid": str(uuid.uuid4()),
                "dtoolcore_version": __version__,
                "name": name,
                "type": "protodataset",
                "creator_username": dtoolcore.utils.getuser(),
                "readme_path": "README.yml"

            }
        else:
            self._admin_metadata = admin_metadata

        self._storage_broker = None

    @classmethod
    def create(cls, uri, name):
        """
        Return a :class:`dtoolcore.ProtoDataSet`.

        :params uri: unique resource identifier defining where the dataset will
                     be stored
        :params name: dataset name
        :returns: :class:`dtoolcore.ProtoDataSet`
        """

        proto_dataset = cls(name)

        proto_dataset._storage_broker = DiskStorageBroker(uri)

        proto_dataset._storage_broker.create_structure()
        proto_dataset._storage_broker.put_admin_metadata(
            proto_dataset._admin_metadata
        )

        proto_dataset.put_readme("")

        return proto_dataset

    @classmethod
    def from_uri(cls, uri):
        """
        Return an existing :class:`dtoolcore.ProtoDataSet` from a URI.

        :params uri: unique resource identifier where the existing
                     :class:`dtoolcore.ProtoDataSet` is stored
        :returns: :class:`dtoolcore.ProtoDataSet`
        """

        storage_broker = DiskStorageBroker(uri)
        admin_metadata = storage_broker.get_admin_metadata()
        if admin_metadata["type"] != "protodataset":
            raise(TypeError("{} is not a ProtoDataSet".format(uri)))
        proto_dataset = cls(
            name=None,
            admin_metadata=admin_metadata
        )
        proto_dataset._storage_broker = storage_broker
        return proto_dataset

    @property
    def uuid(self):
        """Return the UUID of the dataset."""
        return self._admin_metadata["uuid"]

    @property
    def name(self):
        """Return the name of the dataset."""
        return self._admin_metadata["name"]

    def _generate_manifest(self):
        """Return manifest generated from knowledge about contents."""

        items = dict()
        for handle in self._storage_broker.iter_item_handles():
            key = generate_identifier(handle)
            value = self._storage_broker.item_properties(handle)
            items[key] = value

        manifest = {
            "items": items,
            "dtoolcore_version": __version__,
            "hash_function": self._storage_broker.hasher.name
        }

        return manifest

    def put_item(self, fpath, relpath):
        """
        Put an item into the dataset.

        :param fpath: path to the item on disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        """

        self._storage_broker.put_item(
            fpath,
            relpath
        )

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """

        self._storage_broker.put_readme(content)

    def get_readme_content(self):
        """
        Return the content of the README describing the dataset.

        :returns: content of README as a string
        """
        return self._storage_broker.get_readme_content()

    def add_item_metadata(self, handle, key, value):
        """
        Add metadata to a specific item in the :class:`dtoolcore.ProtoDataSet`.

        :param handle: handle representing the relative path of the item in the
                       :class:`dtoolcore.ProtoDataSet`
        :param key: metadata key
        :param value: metadata value
        """

        self._storage_broker.add_item_metadata(handle, key, value)

    def freeze(self):
        """
        Convert :class:`dtoolcore.ProtoDataSet` to :class:`dtoolcore.DataSet`.

        1. Generate and persist the manifest
        2. Create and persist overlays from any item metadata that has been
           added
        3. Change the type of the dataset from "protodataset" to "dataset"
           and add a "frozen_at" time stamp to the administrative metadata
        4. Clean up using the storage broker's post freeze hook
        """

        manifest = self._generate_manifest()
        self._storage_broker.put_manifest(manifest)

        all_user_metadata = defaultdict(dict)
        for handle in self._storage_broker.iter_item_handles():
            identifier = generate_identifier(handle)
            item_metadata = self._storage_broker.get_item_metadata(handle)
            for k, v in item_metadata.items():
                all_user_metadata[k][identifier] = v

        for overlay_name, overlay in all_user_metadata.items():
            self._storage_broker.put_overlay(overlay_name, overlay)

        now_timestamp = datetime.datetime.utcnow().strftime("%s")
        metadata_update = {
            "type": "dataset",
            "frozen_at": now_timestamp
        }

        self._admin_metadata.update(metadata_update)
        self._storage_broker.put_admin_metadata(self._admin_metadata)

        self._storage_broker.post_freeze_hook()
