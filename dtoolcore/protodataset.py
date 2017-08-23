import uuid
import datetime

from collections import defaultdict

import dtoolcore.utils

from dtoolcore import __version__

from dtoolcore.dataset import _BaseDataSet


class _ProtoDataSet(_BaseDataSet):
    """
    Class for building up a dataset.
    """

    @classmethod
    def from_uri(cls, uri, config_path=None):
        """
        Return an existing :class:`dtoolcore.ProtoDataSet` from a URI.

        :params uri: unique resource identifier where the existing
                     :class:`dtoolcore.ProtoDataSet` is stored
        :returns: :class:`dtoolcore.ProtoDataSet`
        """
        return cls._from_uri_with_typecheck(uri, config_path, "protodataset")

    @classmethod
    def create(cls, uri, name, config_path=None):
        """
        Return a :class:`dtoolcore.ProtoDataSet`.

        :params uri: unique resource identifier defining where the dataset will
                     be stored
        :params name: dataset name
        :returns: :class:`dtoolcore.ProtoDataSet`
        """
        admin_metadata = {
            "uuid": str(uuid.uuid4()),
            "dtoolcore_version": __version__,
            "name": name,
            "type": "protodataset",
            "creator_username": dtoolcore.utils.getuser(),
            "readme_path": "README.yml"
        }
        proto_dataset = cls(uri, admin_metadata, config_path)

        proto_dataset._storage_broker.create_structure()
        proto_dataset._storage_broker.put_admin_metadata(
            proto_dataset._admin_metadata
        )

        proto_dataset.put_readme("")

        return proto_dataset

    @property
    def identifiers(self):
        """Return iterable of dataset item identifiers."""
        for handle in self._storage_broker.iter_item_handles():
            yield dtoolcore.utils.generate_identifier(handle)

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """
        self._storage_broker.put_readme(content)

    def put_item(self, fpath, relpath):
        """
        Put an item into the dataset.

        :param fpath: path to the item on disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        """
        self._storage_broker.put_item(fpath, relpath)

    def add_item_metadata(self, handle, key, value):
        """
        Add metadata to a specific item in the :class:`dtoolcore.ProtoDataSet`.

        :param handle: handle representing the relative path of the item in the
                       :class:`dtoolcore.ProtoDataSet`
        :param key: metadata key
        :param value: metadata value
        """
        self._storage_broker.add_item_metadata(handle, key, value)

    def _generate_manifest(self):
        """Return manifest generated from knowledge about contents."""
        items = dict()
        for handle in self._storage_broker.iter_item_handles():
            key = dtoolcore.utils.generate_identifier(handle)
            value = self._storage_broker.item_properties(handle)
            items[key] = value

        manifest = {
            "items": items,
            "dtoolcore_version": __version__,
            "hash_function": self._storage_broker.hasher.name
        }

        return manifest

    def _generate_overlays(self):
        """Return dictionary of overlays generated from added item metadata."""
        overlays = defaultdict(dict)
        for handle in self._storage_broker.iter_item_handles():
            identifier = dtoolcore.utils.generate_identifier(handle)
            item_metadata = self._storage_broker.get_item_metadata(handle)
            for k, v in item_metadata.items():
                overlays[k][identifier] = v

        return overlays

    def freeze(self):
        """
        Convert :class:`dtoolcore.ProtoDataSet` to :class:`dtoolcore.DataSet`.
        """
        # Generate and persist the manifest.
        manifest = self._generate_manifest()
        self._storage_broker.put_manifest(manifest)

        # Generate and persist overlays from any item metadata that has been
        # added.

        overlays = self._generate_overlays()
        for overlay_name, overlay in overlays.items():
            self.put_overlay(overlay_name, overlay)

        # Change the type of the dataset from "protodataset" to "dataset" and
        # add a "frozen_at" time stamp to the administrative metadata.
        now_timestamp = datetime.datetime.utcnow().strftime("%s")
        metadata_update = {
            "type": "dataset",
            "frozen_at": now_timestamp
        }
        self._admin_metadata.update(metadata_update)
        self._storage_broker.put_admin_metadata(self._admin_metadata)

        # Clean up using the storage broker's post freeze hook.
        self._storage_broker.post_freeze_hook()
