"""API for creating and interacting with dtool datasets.

"""

import os
import datetime
import uuid

from pkg_resources import iter_entry_points
from collections import defaultdict

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import dtoolcore.utils


__version__ = "2.9.1"


def _generate_storage_broker_lookup():
    """Return dictionary of available storage brokers."""
    storage_broker_lookup = dict()
    for entrypoint in iter_entry_points("dtool.storage_brokers"):
        StorageBroker = entrypoint.load()
        storage_broker_lookup[StorageBroker.key] = StorageBroker
    return storage_broker_lookup


def _get_storage_broker(uri, config_path):
    """Helper function to enable use lookup of appropriate storage brokers."""
    storage_broker_lookup = _generate_storage_broker_lookup()
    parsed_uri = urlparse(uri)
    scheme = parsed_uri.scheme

    # If scheme is missing (e.g. /some/path) assume it is on local disk.
    if scheme == "":
        scheme = "file"

    StorageBroker = storage_broker_lookup[scheme]
    return StorageBroker(parsed_uri.path, config_path)


def _admin_metadata_from_uri(uri, config_path):
    """Helper function for getting admin metadata."""
    storage_broker = _get_storage_broker(uri, config_path)
    admin_metadata = storage_broker.get_admin_metadata()
    return admin_metadata


def _is_dataset(uri, config_path):
    """Helper function for determining if a URI is a dataset."""
    storage_broker = _get_storage_broker(uri, config_path)
    return storage_broker.has_admin_metadata()


def generate_admin_metadata(name, creator_username=None):
    """Return admin metadata as a dictionary."""
    if creator_username is None:
        creator_username = dtoolcore.utils.getuser()
    admin_metadata = {
        "uuid": str(uuid.uuid4()),
        "dtoolcore_version": __version__,
        "name": name,
        "type": "protodataset",
        "creator_username": creator_username,
        "readme_path": "README.yml"
    }
    return admin_metadata


def _generate_uri(admin_metadata, prefix, storage):
    """Return dataset URI.

    :param admin_metadata: dataset administrative metadata
    :param prefix: dataset root
    :param storage: type of storage
    :returns: dataset URI
    """
    name = admin_metadata["name"]
    uuid = admin_metadata["uuid"]
    storage_broker_lookup = _generate_storage_broker_lookup()
    StorageBroker = storage_broker_lookup[storage]
    return StorageBroker.generate_uri(name, uuid, prefix)


def generate_proto_dataset(admin_metadata, prefix, storage, config_path=None):
    """Return :class:`dtoolcore.ProtoDataSet` instance.

    :param admin_metadata: dataset administrative metadata
    :param prefix: dataset root
    :param storage: type of storage
    :param config_path: path to dtool configuration file
    """
    uri = _generate_uri(admin_metadata, prefix, storage)
    return ProtoDataSet(uri, admin_metadata, config_path)


def copy(src_uri, prefix, storage, config_path=None, progressbar=None):
    """Copy a dataset to another location.

    :param src_uri: URI of dataset to be copied
    :param prefix: root to put dataset into
    :param storage: type of storage
    :param config_path: path to dtool configuration file
    :returns: URI of new dataset
    """
    dataset = DataSet.from_uri(src_uri)

    if progressbar:
        progressbar.label = "Copying dataset"

    admin_metadata = dataset._admin_metadata
    admin_metadata["type"] = "protodataset"
    del admin_metadata["frozen_at"]

    proto_dataset = generate_proto_dataset(
        admin_metadata=admin_metadata,
        prefix=prefix,
        storage=storage,
        config_path=config_path
    )

    # Ensure that this bug does not get re-introduced:
    # https://github.com/jic-dtool/dtoolcore/issues/1
    assert proto_dataset._admin_metadata["type"] == "protodataset"
    assert "frozen_at" not in proto_dataset._admin_metadata

    proto_dataset.create()

    for identifier in dataset.identifiers:
        item_properties = dataset.item_properties(identifier)
        src_abspath = dataset.item_content_abspath(identifier)
        relpath = item_properties["relpath"]
        proto_dataset.put_item(src_abspath, relpath)
        if progressbar:
            progressbar.item_show_func = lambda x: relpath
            progressbar.update(1)

    proto_dataset.put_readme(dataset.get_readme_content())

    for overlay_name in dataset.list_overlay_names():
        overlay = dataset.get_overlay(overlay_name)
        proto_dataset._put_overlay(overlay_name, overlay)

    proto_dataset.freeze(progressbar=progressbar)

    return proto_dataset.uri


class DtoolCoreTypeError(TypeError):
    pass


class _BaseDataSet(object):
    """Base class for datasets."""

    def __init__(self, uri, admin_metadata, config_path=None):
        self._admin_metadata = admin_metadata
        self._storage_broker = _get_storage_broker(uri, config_path)

        # Create a full qualified URI for the dataset.
        parsed_uri = urlparse(uri)
        prefix = os.path.dirname(parsed_uri.path)
        uri = self._storage_broker.generate_uri(
            name=admin_metadata["name"],
            uuid=admin_metadata["uuid"],
            prefix=prefix
        )

        self._uri = uri

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
    def uri(self):
        """Return the URI of the dataset."""
        return self._uri

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

    def generate_manifest(self, progressbar=None):
        """Return manifest generated from knowledge about contents."""
        items = dict()

        if progressbar:
            progressbar.label = "Generating manifest"

        for handle in self._storage_broker.iter_item_handles():
            key = dtoolcore.utils.generate_identifier(handle)
            value = self._storage_broker.item_properties(handle)
            items[key] = value
            if progressbar:
                progressbar.item_show_func = lambda x: handle
                progressbar.update(1)

        manifest = {
            "items": items,
            "dtoolcore_version": __version__,
            "hash_function": self._storage_broker.hasher.name
        }

        return manifest


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

    def list_overlay_names(self):
        """Return list of overlay names."""
        return self._storage_broker.list_overlay_names()

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

    def _identifiers(self):
        """Return iterable of dataset item identifiers."""
        for handle in self._storage_broker.iter_item_handles():
            yield dtoolcore.utils.generate_identifier(handle)

    def update_name(self, new_name):
        """Update the name of the proto dataset.

        :param new_name: the new name of the proto dataset
        """
        self._admin_metadata['name'] = new_name
        if self._storage_broker.has_admin_metadata():
            self._storage_broker.put_admin_metadata(self._admin_metadata)

    def create(self):
        """Create the required directory structure and admin metadata."""
        self._storage_broker.create_structure()
        self._storage_broker.put_admin_metadata(self._admin_metadata)

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
        :returns: the handle given to the item
        """
        return self._storage_broker.put_item(fpath, relpath)

    def add_item_metadata(self, handle, key, value):
        """
        Add metadata to a specific item in the :class:`dtoolcore.ProtoDataSet`.

        :param handle: handle representing the relative path of the item in the
                       :class:`dtoolcore.ProtoDataSet`
        :param key: metadata key
        :param value: metadata value
        """
        self._storage_broker.add_item_metadata(handle, key, value)

    def _generate_overlays(self):
        """Return dictionary of overlays generated from added item metadata."""
        overlays = defaultdict(dict)
        for handle in self._storage_broker.iter_item_handles():
            identifier = dtoolcore.utils.generate_identifier(handle)
            item_metadata = self._storage_broker.get_item_metadata(handle)
            for k, v in item_metadata.items():
                overlays[k][identifier] = v

        return overlays

    def freeze(self, progressbar=None):
        """
        Convert :class:`dtoolcore.ProtoDataSet` to :class:`dtoolcore.DataSet`.
        """
        # Call the storage broker pre_freeze hook.
        self._storage_broker.pre_freeze_hook()

        if progressbar:
            progressbar.label = "Freezing dataset"

        # Generate and persist the manifest.
        manifest = self.generate_manifest(progressbar=progressbar)
        self._storage_broker.put_manifest(manifest)

        # Generate and persist overlays from any item metadata that has been
        # added.

        overlays = self._generate_overlays()
        for overlay_name, overlay in overlays.items():
            self._put_overlay(overlay_name, overlay)

        # Change the type of the dataset from "protodataset" to "dataset" and
        # add a "frozen_at" time stamp to the administrative metadata.
        now_timestamp = float(datetime.datetime.utcnow().strftime("%s"))
        metadata_update = {
            "type": "dataset",
            "frozen_at": now_timestamp
        }
        self._admin_metadata.update(metadata_update)
        self._storage_broker.put_admin_metadata(self._admin_metadata)

        # Clean up using the storage broker's post freeze hook.
        self._storage_broker.post_freeze_hook()
