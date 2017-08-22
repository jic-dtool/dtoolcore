import uuid
import datetime

from collections import defaultdict

import dtoolcore.utils
from dtoolcore.utils import generate_identifier

from dtoolcore.storage_broker import DiskStorageBroker

from dtoolcore import __version__


class ProtoDataSet(object):

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
        """Return the proto dataset's UUID."""
        return self._admin_metadata["uuid"]

    @property
    def name(self):
        """Return the proto dataset's name."""
        return self._admin_metadata["name"]

    def _generate_manifest(self):
        """Return manifest generated from knowledge about contents."""

        items = {
            generate_identifier(handle): self._item_properties(handle)
            for handle in self._iterhandles()
        }

        manifest = {
            "items": items,
            "dtoolcore_version": __version__,
            "hash_function": self._storage_broker.hasher.name
        }

        return manifest

    def put_item(self, fpath, relpath):

        self._storage_broker.put_item(
            fpath,
            relpath
        )

    def put_readme(self, contents):

        self._storage_broker.put_readme(contents)

    @property
    def readme_content(self):
        return self._storage_broker.get_readme_contents()

    def add_item_metadata(self, handle, key, value):
        self._storage_broker.add_item_metadata(handle, key, value)

    def freeze(self):

        manifest = self._generate_manifest()
        self._storage_broker.put_manifest(manifest)

        all_user_metadata = defaultdict(dict)
        for handle in self._iterhandles():
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

    def _item_properties(self, handle):

        return self._storage_broker.item_properties(handle)

    def _iterhandles(self):

        return self._storage_broker.iter_item_handles()
