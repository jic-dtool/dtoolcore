"""API for creating and interacting with dtool datasets.

"""

import uuid
import datetime

from pkg_resources import iter_entry_points
from collections import defaultdict

import dtoolcore.utils


__version__ = "2.0.0"


def _generate_storage_broker_lookup():
    """Return dictionary of available storage brokers."""
    storage_broker_lookup = dict()
    for entrypoint in iter_entry_points("dtool.storage_brokers"):
        StorageBroker = entrypoint.load()
        storage_broker_lookup[StorageBroker.key] = StorageBroker
    return storage_broker_lookup


def _get_storage_broker(type_uri, config_path):
    """Helper function to enable use lookup of appropriate storage brokers."""
    storage_broker_lookup = _generate_storage_broker_lookup()
    sb_type, stripped_uri = type_uri.split(":", 1)
    StorageBroker = storage_broker_lookup[sb_type]
    return StorageBroker(stripped_uri, config_path)


def _admin_metadata_from_uri(uri, config_path):
    """Helper function for getting admin metadata."""
    storage_broker = _get_storage_broker(uri, config_path)
    admin_metadata = storage_broker.get_admin_metadata()
    return admin_metadata


def _is_dataset(uri, config_path):
    """Helper function for determining if a URI is a dataset."""
    storage_broker = _get_storage_broker(uri, config_path)
    return storage_broker.has_admin_metadata()


class DtoolCoreTypeError(TypeError):
    pass


class _BaseDataSet(object):
    """Base class for datasets."""

    def __init__(self, uri, admin_metadata, config_path=None):
        self._admin_metadata = admin_metadata
        self._storage_broker = _get_storage_broker(uri, config_path)

    @classmethod
    def _from_uri_with_typecheck(cls, uri, config_path, type_name):
        # Make sure that the URI refers to a dataset.
        if not _is_dataset(uri, config_path):
            raise(DtoolCoreTypeError("{} is not a dataset".format(uri)))

        # Get the admin metadata out of the URI and type check.
        admin_metadata = _admin_metadata_from_uri(uri, config_path)
        if admin_metadata['type'] != type_name:
            raise DtoolCoreTypeError(
                "{} is not a {}".format(uri, cls.__name__))

        # Instantiate and return.
        return cls(uri, admin_metadata, config_path)

    @property
    def uuid(self):
        """Return the UUID of the dataset."""
        return self._admin_metadata["uuid"]

    @property
    def name(self):
        """Return the name of the dataset."""
        return self._admin_metadata['name']

    def get_readme_content(self):
        """
        Return the content of the README describing the dataset.

        :returns: content of README as a string
        """
        return self._storage_broker.get_readme_content()

    def _put_overlay(self, overlay_name, overlay):
        """Store overlay so that it is accessible by the given name.

        :param overlay_name: name of the overlay
        :param overlay: overlay must be a dictionary where the keys are
                        identifiers in the dataset
        :raises: TypeError if the overlay is not a dictionary,
                 ValueError if identifiers in overlay and dataset do not match
        """
        if not isinstance(overlay, dict):
            raise TypeError("Overlay must be dict")

        if set(self._identifiers()) != set(overlay.keys()):
            raise ValueError("Overlay keys must be dataset identifiers")

        self._storage_broker.put_overlay(overlay_name, overlay)


class DataSet(_BaseDataSet):
    """
    Class for reading the contents of a dataset.
    """

    def __init__(self, uri, admin_metadata, config_path=None):
        super(DataSet, self).__init__(uri, admin_metadata, config_path)
        self._manifest_cache = None

    def _identifiers(self):
        return self._manifest["items"].keys()

    @classmethod
    def from_uri(cls, uri, config_path=None):
        """
        Return an existing :class:`dtoolcore.DataSet` from a URI.

        :params uri: unique resource identifier where the existing
                     :class:`dtoolcore.DataSet` is stored
        :returns: :class:`dtoolcore.DataSet`
        """
        return cls._from_uri_with_typecheck(uri, config_path, "dataset")

    @property
    def identifiers(self):
        """Return iterable of dataset item identifiers."""
        return self._identifiers()

    @property
    def _manifest(self):
        """Return manifest content."""
        if self._manifest_cache is None:
            self._manifest_cache = self._storage_broker.get_manifest()

        return self._manifest_cache

    def item_properties(self, identifier):
        """Return properties of the item with the given identifier.

        :param identifier: item identifier
        :returns: dictionary of item properties from the manifest
        """
        return self._manifest["items"][identifier]

    def item_content_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """
        return self._storage_broker.get_item_abspath(identifier)

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """
        return self._storage_broker.get_overlay(overlay_name)

    def put_overlay(self, overlay_name, overlay):
        """Store overlay so that it is accessible by the given name.

        :param overlay_name: name of the overlay
        :param overlay: overlay must be a dictionary where the keys are
                        identifiers in the dataset
        :raises: TypeError if the overlay is not a dictionary,
                 ValueError if identifiers in overlay and dataset do not match
        """
        self._put_overlay(overlay_name, overlay)


class ProtoDataSet(_BaseDataSet):
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
    def create_structure(
        cls,
        uri,
        config_path=None,
        admin_metadata=None
    ):
        """
        :params uri: unique resource identifier defining where the dataset will
                     be stored
        :params name: dataset name
        :returns: :class:`dtoolcore.ProtoDataSet`
        """
        proto_dataset = cls(
            uri,
            admin_metadata=admin_metadata,
            config_path=config_path)
        proto_dataset._storage_broker.create_structure()
        return proto_dataset

    @classmethod
    def new(cls, uri, name, config_path=None):
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

        proto_dataset = cls.create_structure(
            uri=uri,
            config_path=config_path,
            admin_metadata=admin_metadata
        )

        proto_dataset._storage_broker.put_admin_metadata(
            proto_dataset._admin_metadata
        )
        proto_dataset.put_readme("")

        return proto_dataset

    def _identifiers(self):
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
            self._put_overlay(overlay_name, overlay)

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
